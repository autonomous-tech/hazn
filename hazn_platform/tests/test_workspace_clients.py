"""Tests for WS-03: EndClient CRUD scoped by agency FK.

Verifies:
- GET /api/workspace/clients/ returns only agency's clients
- POST creates client with agency auto-set from user
- PUT updates client only if it belongs to user's agency
- DELETE/GET returns 404 for other agency's clients
"""


import pytest
from django.test import RequestFactory
from rest_framework.test import force_authenticate

from hazn_platform.core.models import Agency, EndClient
from hazn_platform.users.models import User


@pytest.fixture()
def agency_a():
    return Agency.objects.create(name="Agency A", slug="agency-a")


@pytest.fixture()
def agency_b():
    return Agency.objects.create(name="Agency B", slug="agency-b")


@pytest.fixture()
def user_a(agency_a):
    return User.objects.create_user(
        username="user_a",
        email="a@test.com",
        password="testpass",
        agency=agency_a,
    )


@pytest.fixture()
def user_b(agency_b):
    return User.objects.create_user(
        username="user_b",
        email="b@test.com",
        password="testpass",
        agency=agency_b,
    )


@pytest.fixture()
def client_a1(agency_a):
    return EndClient.objects.create(
        agency=agency_a, name="Client A1", slug="client-a1"
    )


@pytest.fixture()
def client_a2(agency_a):
    return EndClient.objects.create(
        agency=agency_a, name="Client A2", slug="client-a2"
    )


@pytest.fixture()
def client_b1(agency_b):
    return EndClient.objects.create(
        agency=agency_b, name="Client B1", slug="client-b1"
    )


@pytest.mark.django_db()
class TestEndClientViewSet:
    def _get_view(self, actions=None, kwargs=None):
        from hazn_platform.workspace.views import EndClientViewSet

        if actions is None:
            actions = {"get": "list", "post": "create"}
        return EndClientViewSet.as_view(actions, **(kwargs or {}))

    def _get_detail_view(self):
        from hazn_platform.workspace.views import EndClientViewSet

        return EndClientViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        )

    def test_list_returns_only_agency_clients(
        self, user_a, client_a1, client_a2, client_b1
    ):
        factory = RequestFactory()
        request = factory.get("/api/workspace/clients/")
        force_authenticate(request, user=user_a)
        response = self._get_view({"get": "list"})(request)
        assert response.status_code == 200
        ids = {str(c["id"]) for c in response.data}
        assert str(client_a1.pk) in ids
        assert str(client_a2.pk) in ids
        assert str(client_b1.pk) not in ids

    def test_create_auto_sets_agency(self, user_a):
        factory = RequestFactory()
        request = factory.post(
            "/api/workspace/clients/",
            data={"name": "New Client", "slug": "new-client"},
            content_type="application/json",
        )
        force_authenticate(request, user=user_a)
        response = self._get_view({"post": "create"})(request)
        assert response.status_code == 201
        created = EndClient.objects.get(pk=response.data["id"])
        assert created.agency == user_a.agency

    def test_retrieve_own_client(self, user_a, client_a1):
        factory = RequestFactory()
        request = factory.get(f"/api/workspace/clients/{client_a1.pk}/")
        force_authenticate(request, user=user_a)
        response = self._get_detail_view()(request, pk=str(client_a1.pk))
        assert response.status_code == 200
        assert response.data["name"] == "Client A1"

    def test_retrieve_other_agency_client_returns_404(self, user_a, client_b1):
        factory = RequestFactory()
        request = factory.get(f"/api/workspace/clients/{client_b1.pk}/")
        force_authenticate(request, user=user_a)
        response = self._get_detail_view()(request, pk=str(client_b1.pk))
        assert response.status_code == 404

    def test_update_own_client(self, user_a, client_a1):
        factory = RequestFactory()
        request = factory.put(
            f"/api/workspace/clients/{client_a1.pk}/",
            data={"name": "Updated Client", "slug": "client-a1"},
            content_type="application/json",
        )
        force_authenticate(request, user=user_a)
        response = self._get_detail_view()(request, pk=str(client_a1.pk))
        assert response.status_code == 200
        client_a1.refresh_from_db()
        assert client_a1.name == "Updated Client"

    def test_delete_other_agency_client_returns_404(self, user_a, client_b1):
        factory = RequestFactory()
        request = factory.delete(f"/api/workspace/clients/{client_b1.pk}/")
        force_authenticate(request, user=user_a)
        response = self._get_detail_view()(request, pk=str(client_b1.pk))
        assert response.status_code == 404

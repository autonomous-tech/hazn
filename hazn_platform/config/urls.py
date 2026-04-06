from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.http import HttpResponseNotFound
from django.views.generic import TemplateView

# Dummy view for allauth URL names suppressed by HEADLESS_ONLY=True
_headless_stub = lambda r, *a, **kw: HttpResponseNotFound()

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("hazn_platform.users.urls", namespace="users")),
    # Allauth headless stubs — HEADLESS_ONLY suppresses these URL names but
    # allauth 65.x still reverse()s them internally during login/signup.
    path("accounts/signup/", _headless_stub, name="account_signup"),
    path("accounts/login/", _headless_stub, name="account_login"),
    path("accounts/", include("allauth.urls")),
    path("api/_allauth/", include("allauth.headless.urls")),
    # Your stuff: custom urls includes go here
    path("api/orchestrator/", include("hazn_platform.orchestrator.api.urls")),
    path("api/workspace/", include("hazn_platform.workspace.urls")),
    # SSE events endpoint (django-eventstream)
    path("api/events/", include("django_eventstream.urls"), {"channels": []}),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]

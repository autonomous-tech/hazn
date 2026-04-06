# Django service policy -- read+write for agency onboarding
path "secret/data/agencies/*" {
  capabilities = ["create", "read", "update", "delete"]
}

path "secret/metadata/agencies/*" {
  capabilities = ["list", "read", "delete"]
}

# Explicit deny on admin paths -- prevents privilege escalation
path "sys/*" {
  capabilities = ["deny"]
}

path "auth/*" {
  capabilities = ["deny"]
}

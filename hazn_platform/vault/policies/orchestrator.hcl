# Orchestrator service policy -- read-only on agency credentials
path "secret/data/agencies/*" {
  capabilities = ["read"]
}

path "secret/metadata/agencies/*" {
  capabilities = ["list", "read"]
}

# Explicit deny on admin paths -- prevents privilege escalation
path "sys/*" {
  capabilities = ["deny"]
}

path "auth/*" {
  capabilities = ["deny"]
}

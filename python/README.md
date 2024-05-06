# SBC Common Python Libraries

## Libraries

[structured logging](./structured-logging)


## Private Artifact Registry

### Required roles:
The following roles are needed to work with the private Python Artifact Registry

- roles/artifactregistry.reader: All developers
- roles/artifactregistry.writer: CI/CD and Leads.
- roles/artifactregistry.repoAdmin: SRE

### Poetry common setup for GCP Artifact Registry
Initialize _gcloud_ for the private project Artifact Registry
```bash
gcloud init
```

Update poetry and add the google keyring
```bash
poetry self update && poetry self add keyrings.google-artifactregistry-auth
```

Register the private Python Artifact Registry
```bash
export SBC_CONNECT_PYTHON_REPO_URL="https://northamerica-northeast1-python.pkg.dev/c4hnrd-tools/python/"
poetry config repositories.sbc-connect $SBC_CONNECT_PYTHON_REPO_URL
```

### Install from GCP Artifact Registry
As a user of the library
```bash
poetry source add --priority=explicit sbc-connect $SBC_CONNECT_PYTHON_REPO_URL
```
```bash
poetry add --source sbc-connect structured-logging
```

### Publish to GCP Artifact Registry
As a CI/CD maintianer or SRE member
```bash
poetry publish --build --repository sbc-connect
```

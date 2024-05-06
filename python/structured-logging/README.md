





### Required roles:
roles/artifactregistry.reader: All developers
roles/artifactregistry.writer: CI/CD and Leads.
roles/artifactregistry.repoAdmin: SRE

```bash
gcloud init
```

### Poetry common setup for GCP Artifact Registry
```bash
poetry self update && poetry self add keyrings.google-artifactregistry-auth
```

```bash
export SBC_CONNECT_PYTHON_REPO_URL="https://northamerica-northeast1-python.pkg.dev/c4hnrd-tools/python/"
poetry config repositories.sbc-connect $SBC_CONNECT_PYTHON_REPO_URL
```

### Install from GCP Artifact Registry
```bash
poetry source add --priority=explicit sbc-connect $SBC_CONNECT_PYTHON_REPO_URL
```
```bash
poetry add --source sbc-connect structured-logging
```

### Publish to GCP Artifact Registry
```bash
poetry publish --build --repository sbc-connect
```

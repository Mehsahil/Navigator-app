# Navigation POC — Cloud Run Cloud SQL Integration

This POC intentionally uses **Cloud Run's native Cloud SQL integration**.

It does NOT use:

- Public Cloud SQL IP
- `DB_HOST` public IP
- A database URL containing credentials
- A VPC connector for the Cloud SQL connection

## Architecture

```text
GitHub
  │
  │ OIDC
  ▼
GCP Workload Identity Federation
  │
  ▼
github-deploy-sa
  │
  ├── Artifact Registry
  │
  └── Cloud Run deployment
          │
          ▼
   navigation-backend
          │
          ├── backend-runtime-sa
          │
          ├── Secret Manager
          │      ├── DB_NAME
          │      ├── DB_USER
          │      └── DB_PASSWORD
          │
          └── Cloud SQL integration
                   │
                   ▼
             Cloud SQL MySQL
```

## GCP resources

Create:

- Artifact Registry repository: `navigation-app`
- Cloud SQL MySQL instance: `navigation-mysql`
- Database: `navigationdb`
- Database user: `navigation_app`
- Service accounts:
  - `github-deploy-sa`
  - `backend-runtime-sa`
  - `frontend-runtime-sa`
- Secret Manager:
  - `backend-db-name`
  - `backend-db-user`
  - `backend-db-password`
- Workload Identity Pool:
  - `github-pool`
- OIDC Provider:
  - `github-provider`
- Cloud Run:
  - `navigation-backend`
  - `navigation-frontend`

## Backend service account

`backend-runtime-sa` needs:

```text
Cloud SQL Client
Secret Manager Secret Accessor
```

Grant Secret Manager access only to:

```text
backend-db-name
backend-db-user
backend-db-password
```

## GitHub deployment service account

`github-deploy-sa` needs permissions to:

```text
push images to Artifact Registry
deploy Cloud Run
act as/use the runtime service accounts
```

Use least privilege in production.

## GitHub repository variables

Add:

```text
GCP_PROJECT_ID
GCP_WORKLOAD_IDENTITY_PROVIDER
CLOUD_SQL_INSTANCE
```

Example:

```text
GCP_PROJECT_ID=major-navigator-poc

GCP_WORKLOAD_IDENTITY_PROVIDER=
projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider

CLOUD_SQL_INSTANCE=
major-navigator-poc:asia-south1:navigation-mysql
```

These are identifiers/configuration, not passwords.

## Secret Manager values

Create:

```text
backend-db-name
    navigationdb

backend-db-user
    navigation_app

backend-db-password
    <strong random MySQL password>
```

Do not put the password into GitHub.

## How Cloud SQL connection works

Cloud Run is deployed with:

```bash
--add-cloudsql-instances=PROJECT_ID:REGION:INSTANCE_NAME
```

The backend receives:

```text
INSTANCE_UNIX_SOCKET=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME
```

The Python application connects using:

```python
pymysql.connect(
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    database=os.environ["DB_NAME"],
    unix_socket=os.environ["INSTANCE_UNIX_SOCKET"]
)
```

No database password is in the Docker image.

## Test endpoints

Backend:

```text
GET /health
```

Cloud SQL:

```text
GET /db-test
```

Secret/config test:

```text
GET /config-test
```

`/db-test` runs:

```sql
SELECT 1
```

and reports whether MySQL is reachable.

## GitHub Actions image tagging

Every image uses:

```text
${{ github.sha }}
```

Example:

```text
asia-south1-docker.pkg.dev/PROJECT_ID/navigation-app/backend:8e7a91...
```

This makes every Cloud Run revision traceable to a specific Git commit.

## Important

The frontend is deliberately simple. Do not put real database credentials, API keys, or other confidential values into frontend JavaScript.

The frontend's job in this POC is only to call the backend.

For the real Navigation application, ETL/API credentials should remain server-side and be consumed by the backend/ETL workload through Secret Manager.

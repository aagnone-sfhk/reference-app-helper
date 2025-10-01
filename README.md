# Heroku Reference App Search

<a href="https://deploy.herokuapps.ai?template=https://github.com/aagnone-sfhk/reference-app-helper">
    <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy to Heroku">
</a>

A [FastAPI](https://fastapi.tiangolo.com/) web application that demonstrates RAG (Retrieval-Augmented Generation) for searching Heroku reference app documentation using vector embeddings and Heroku AppLink for easy integration with Salesforce & Agentforce.

## Table of Contents

- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)

## Quick Start

### Prerequisites

- Python 3.8+
- uv (package manager)
- Git
- Heroku CLI (for deployment)
- Salesforce CLI (for setup)
- Salesforce org (for AppLink integration)

### Scripted Setup

**Recommended Workflow:**

1. **Deploy via Heroku Button** (above) - This handles:
   - App creation with proper buildpacks
   - Heroku AppLink addon installation
   - PostgreSQL database provisioning
   - Initial code deployment

2. **Clone your app locally:**

   ```bash
   heroku git:clone -a <your-app-name>
   cd <your-app-name>
   git remote add origin git@github.com:aagnone-sfhk/reference-app-helper.git
   git pull origin main
   ```

3. **Configure Salesforce connections:**
   ```bash
   ./bin/fresh_app.sh <sf_org_alias>
   ```

**Example:**

```bash
./bin/fresh_app.sh acme
```

The configuration script adds:

- Salesforce connections
- API specification publishing to Salesforce
- Permission set assignments for users
- Local `.env` file for development

### Manual Heroku Deployment

If the automatic setup does not work, or you prefer to manually follow along, [follow this getting started guide](https://devcenter.heroku.com/articles/getting-started-heroku-applink).

## Local Development

### Install and Run

```bash
# Install dependencies
uv sync

# Get environment variables from Heroku
heroku config -s > .env

# Start development server
uv run --env-file .env uvicorn app.main:app --reload
```

Your app will be available at `http://localhost:8000`.

**Note:** Protected endpoints under `/api` require Salesforce context headers. Use `invoke.py` for local testing (see Configuration section).

### Indexing Reference App READMEs

After deployment, index the Heroku reference app documentation into the vector database:

```bash
# Ensure you have environment variables loaded
heroku config -s > .env

# Run the indexing script
uv run --env-file .env python bin/index_ref_app_readmes.py
```

This script:
- Downloads READMEs from all repositories in the heroku-reference-apps GitHub organization
- Generates vector embeddings using Heroku Managed Inference and Cohere
- Stores embeddings in PostgreSQL for RAG search functionality

### Local Testing with invoke.py

Test your locally running app with proper Salesforce client context:

```bash
# Set your credentials
sf_org_alias=acme
org_domain=$(sf org display -o $sf_org_alias --json | jq -r .result.instanceUrl | sed 's|https://||')
access_token=$(sf org display -o $sf_org_alias --json | jq -r .result.accessToken)
org_id=$(sf org display -o $sf_org_alias --json | jq -r .result.id)
user_id=$(sf org display -o $sf_org_alias --json | jq -r .result.userId)

# Test endpoints
./bin/invoke.py $org_domain $access_token $org_id $user_id GET /api/accounts/
./bin/invoke.py $org_domain $access_token $org_id $user_id GET "/api/search/?query=How do I deploy to Heroku"
```

For detailed AppLink setup, see the [getting started guide](https://devcenter.heroku.com/articles/getting-started-heroku-applink).

**Note**: This application is designed for educational purposes and as a starting point for building Salesforce-integrated RAG applications. For production use, ensure proper error handling, security measures, and testing practices are implemented.

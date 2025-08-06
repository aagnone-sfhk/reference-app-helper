# Heroku AppLink Python App Template

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy?template=https://github.com/heroku-reference-apps/applink-getting-started-python)

The Heroku AppLink Python app template is a [FastAPI](https://fastapi.tiangolo.com/) web application that demonstrates how to build APIs for Salesforce integration using Heroku AppLink. This template includes authentication, authorization, and API specifications for seamless integration with Salesforce and Data Cloud.

## Table of Contents

- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Testing with invoke.py](#testing-with-invokepy)
- [Running Automated Tests](#running-automated-tests)
- [Manual Heroku Deployment](#manual-heroku-deployment)
- [Heroku AppLink Setup](#heroku-applink-setup)
- [Additional Resources](#additional-resources)

## Quick Start

### Prerequisites

- Python 3.8+
- `pip` for package management
- Git
- Heroku CLI (for deployment)
- Salesforce org (for AppLink integration)

### Deploy to Heroku (One-Click)

Click the Deploy button above to deploy this app directly to Heroku with the AppLink add-on pre-configured.

## Local Development

### 1. Clone and Install

```bash
git clone https://github.com/heroku-reference-apps/applink-getting-started-python.git
cd applink-getting-started-python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the Development Server

```bash
uvicorn app.main:app --reload
```

Your app will be available at `http://localhost:8000`. When you visit this URL, you will see a welcome message.

#### A Note on Local Errors
If you try to access an endpoint under the `/api` prefix directly in your browser (e.g., `http://localhost:8000/api/accounts/`), you will see a `ValueError: x-client-context not set` error. This is expected behavior. The AppLink middleware is protecting these endpoints, and they require Salesforce context headers to be present. The `invoke.py` script is designed to provide these headers for local testing.

### 3. API Endpoints

- **GET /** - A public welcome page.
- **GET /health** - A public health check endpoint.
- **POST /handleDataCloudDataChangeEvent/** - A public webhook for Data Cloud events.
- **GET /docs** - Interactive Swagger UI for API documentation.
- **GET /api/accounts/** - (Protected) Retrieve Salesforce accounts from the invoking org.
- **POST /api/unitofwork/** - (Protected) Create a unit of work for Salesforce.

### 4. View API Documentation

Visit `http://localhost:8000/docs` to explore the interactive API documentation powered by Swagger UI.

## Testing with invoke.py

The `bin/invoke.py` script allows you to test your locally running, protected API endpoints with the proper Salesforce client context headers.

### Usage

```bash
./bin/invoke.py ORG_DOMAIN ACCESS_TOKEN ORG_ID USER_ID [METHOD] [API_PATH] [--data DATA]
```

### Examples

```bash
# Test the accounts endpoint (note the /api/ prefix)
./bin/invoke.py mycompany.my.salesforce.com TOKEN_123 00D123456789ABC 005123456789ABC GET /api/accounts/

# Test with POST data
./bin/invoke.py mycompany.my.salesforce.com TOKEN_123 00D123456789ABC 005123456789ABC POST /api/unitofwork/ --data '{"data":{"accountName":"Test Account", "lastName":"Test", "subject":"Test Case"}}'
```

### Getting Salesforce Credentials

To get the required Salesforce credentials for testing:

1.  **Access Token**: Use Salesforce CLI to generate a session token (`sf org display --target-org <alias> --json | jq .result.accessToken -r`).
2.  **Org ID**: Found in Setup → Company Information or by running `sf org display --target-org <alias> --json | jq .result.id -r`.
3.  **User ID**: Found in your user profile or Setup → Users or by running `sf org display --target-org <alias> --json | jq .result.userId -r`.

## Running Automated Tests

This project uses `pytest` for unit testing. To run the tests:

```bash
pytest
```

## Manual Heroku Deployment

### 1. Prerequisites

- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- Git repository initialized
- Heroku account with billing enabled (for add-ons)

### 2. Create Heroku App

```bash
# Create a new Heroku app
heroku create your-app-name

# Or let Heroku generate a name
heroku create
```

### 3. Add Required Buildpacks

The app requires two buildpacks in the correct order:

```bash
# Add the AppLink Service Mesh buildpack first
heroku buildpacks:add heroku/heroku-applink-service-mesh

# Add the Python buildpack second
heroku buildpacks:add heroku/python
```

### 4. Provision the AppLink Add-on

```bash
# Provision the Heroku AppLink add-on
heroku addons:create heroku-applink

# Set the required HEROKU_APP_ID config var
heroku config:set HEROKU_APP_ID="$(heroku apps:info --json | jq -r '.app.id')"
```

### 5. Deploy the Application

```bash
# Deploy to Heroku
git push heroku main

# Check deployment status
heroku ps:scale web=1
heroku open
```

### 6. Verify Deployment

```bash
# Check app logs
heroku logs --tail
```

## Heroku AppLink Setup

### 1. Install AppLink CLI Plugin

```bash
# Install the AppLink CLI plugin
heroku plugins:install @heroku-cli/plugin-applink
```

### 2. Connect to Salesforce Org

```bash
# Connect to a production org (replace your-addon-name and your-app-name)
heroku salesforce:connect production-org --addon your-addon-name -a your-app-name

# Connect to a sandbox org
heroku salesforce:connect sandbox-org --addon your-addon-name -a your-app-name --login-url https://test.salesforce.com
```

### 3. Authorize a User

```bash
# Authorize a Salesforce user for API access
heroku salesforce:authorizations:add auth-user --addon your-addon-name -a your-app-name
```

### 4. Publish Your App

```bash
# Publish the app to Salesforce as an External Service
heroku salesforce:publish api-spec.yaml \
  --client-name MyAPI \
  --connection-name production-org \
  --authorization-connected-app-name MyAppConnectedApp \
  --authorization-permission-set-name MyAppPermissions \
  --addon your-addon-name
```

### 5. Required Salesforce Permissions
Users need the "Manage Heroku AppLink" permission in Salesforce:
1.  Go to Setup → Permission Sets
2.  Create a new permission set or edit an existing one
3.  Add "Manage Heroku AppLink" system permission
4.  Assign the permission set to users

## Additional Resources

### Documentation

- [Getting Started with Heroku AppLink](https://devcenter.heroku.com/articles/getting-started-heroku-applink)
- [Heroku AppLink CLI Plugin](https://devcenter.heroku.com/articles/heroku-applink-cli)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Note**: This template is designed for educational purposes and as a starting point for building Salesforce-integrated applications. For production use, ensure proper error handling, security measures, and testing practices are implemented.

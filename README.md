# Heroku AppLink Python App Template

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy?template=https://github.com/heroku-reference-apps/applink-getting-started-python)

The Heroku AppLink Python app template is a [FastAPI](https://fastapi.tiangolo.com/) web application that demonstrates how to build APIs for Salesforce integration using Heroku AppLink. This template includes authentication, authorization, and API specifications for seamless integration with Salesforce, Data Cloud, and Agentforce.

## Table of Contents

- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Testing with invoke.py](#testing-with-invokepy)
- [Running Automated Tests](#running-automated-tests)
- [Manual Heroku Deployment](#manual-heroku-deployment)
- [Heroku AppLink Setup](#heroku-applink-setup)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
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

Your app will be available at `http://localhost:8000`.

### 3. API Endpoints

- **GET /accounts** - Retrieve Salesforce accounts from the invoking org.
- **POST /unitofwork** - Create a unit of work for Salesforce.
- **POST /handleDataCloudDataChangeEvent** - Handle a Salesforce Data Cloud Change Event.
- **GET /docs** - Interactive Swagger UI for API documentation.
- **GET /health** - Health check endpoint.

### 4. View API Documentation

Visit `http://localhost:8000/docs` to explore the interactive API documentation powered by Swagger UI.

## Testing with invoke.py

The `bin/invoke.py` script allows you to test your locally running app with proper Salesforce client context headers.

### Usage

```bash
./bin/invoke.py ORG_DOMAIN ACCESS_TOKEN ORG_ID USER_ID [METHOD] [API_PATH] [--data DATA]
```

### Parameters

- **ORG_DOMAIN**: Your Salesforce org domain (e.g., `mycompany.my.salesforce.com`)
- **ACCESS_TOKEN**: Valid Salesforce access token
- **ORG_ID**: Salesforce organization ID (15 or 18 characters)
- **USER_ID**: Salesforce user ID (15 or 18 characters)
- **METHOD**: HTTP method (default: GET)
- **API_PATH**: API endpoint path (default: /accounts)
- **--data**: JSON data for POST/PUT requests (as a string)

### Examples

```bash
# Test the accounts endpoint
./bin/invoke.py mycompany.my.salesforce.com TOKEN_123 00D123456789ABC 005123456789ABC

# Test with POST data
./bin/invoke.py mycompany.my.salesforce.com TOKEN_123 00D123456789ABC 005123456789ABC POST /unitofwork --data '{"data":{"accountName":"Test Account", "lastName":"Test", "subject":"Test Case"}}'

# Test custom endpoint
./bin/invoke.py mycompany.my.salesforce.com TOKEN_123 00D123456789ABC 005123456789ABC GET /health
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

(Instructions for `heroku salesforce:connect`, `heroku salesforce:authorizations:add`, and `heroku salesforce:publish` are identical to the Node.js version and can be referenced from the official documentation.)

## Additional Resources

### Documentation

- [Getting Started with Heroku AppLink](https://devcenter.heroku.com/articles/getting-started-heroku-applink)
- [Heroku AppLink CLI Plugin](https://devcenter.heroku.com/articles/heroku-applink-cli)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Note**: This template is designed for educational purposes and as a starting point for building Salesforce-integrated applications. For production use, ensure proper error handling, security measures, and testing practices are implemented.

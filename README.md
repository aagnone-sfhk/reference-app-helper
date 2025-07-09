# FastAPI Heroku AppLink Integration

This is a basic FastAPI application that demonstrates integration with Heroku AppLink.

## Local Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn main:app --reload
```

The application will be available at `http://localhost:8000`

## Heroku Deployment

1. Make sure you have the Heroku CLI installed and are logged in:
```bash
heroku login
```

2. Create a new Heroku app:
```bash
heroku create your-app-name
```

3. Deploy to Heroku:
```bash
git add .
git commit -m "Initial commit"
git push heroku main
```

4. Configure Heroku AppLink:
```bash
heroku addons:create heroku-applink
```

5. Open your application:
```bash
heroku open
```

## Endpoints

- `GET /`: Returns a simple root page
- `GET /accounts`: Queries accounts using Heroku AppLink Data API

## Note

This application requires proper Heroku AppLink configuration to work with the Data API. Make sure you have the necessary credentials and configuration set up in your environment. 
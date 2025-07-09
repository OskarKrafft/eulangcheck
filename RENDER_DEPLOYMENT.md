# Render Deployment Guide for EU eTranslation Service

## Overview
This guide explains how to deploy your EU eTranslation service to Render, a cloud platform that provides reliable hosting for web applications.

## Prerequisites
1. A Render account (free tier available at https://render.com)
2. Your EU eTranslation API credentials
3. This cleaned-up repository

## Environment Variables
You'll need to set these environment variables in Render:

### Required Environment Variables
- `ETRANSLATION_APPLICATION_NAME`: Your registered application name with EU eTranslation
- `ETRANSLATION_EMAIL`: Your registered email address
- `ETRANSLATION_API_PASSWORD`: Your API password
- `PRODUCTION_URL`: Your Render app URL (e.g., `https://your-app-name.onrender.com`)

### Optional Environment Variables
- `ETRANSLATION_REST_URL`: Default is `https://webgate.ec.europa.eu/etranslation/si/translate`
- `FLASK_PORT`: Default is 5000 (Render will override this with $PORT)
- `FLASK_DEBUG`: Set to `false` for production

## Deployment Steps

### 1. Create a New Web Service on Render

1. Go to https://render.com and sign in
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository containing this code
4. Configure the service:
   - **Name**: Choose a unique name for your app
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`

### 2. Set Environment Variables

In the Render dashboard for your service:

1. Go to the "Environment" tab
2. Add each required environment variable:
   ```
   ETRANSLATION_APPLICATION_NAME=your_app_name
   ETRANSLATION_EMAIL=your_email@domain.com
   ETRANSLATION_API_PASSWORD=your_password
   PRODUCTION_URL=https://your-app-name.onrender.com
   ```

### 3. Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. The deployment usually takes 2-5 minutes

### 4. Update PRODUCTION_URL

After your first deployment:
1. Note the URL that Render assigns to your service
2. Update the `PRODUCTION_URL` environment variable with this URL
3. Redeploy the service

## Important Notes

### Callback URL
- The EU eTranslation service will send callbacks to `https://your-app-name.onrender.com/callback`
- Make sure your `PRODUCTION_URL` environment variable is set correctly
- The callback URL must be publicly accessible via HTTPS

### Free Tier Limitations
- Render's free tier applications sleep after 15 minutes of inactivity
- EU eTranslation callbacks might fail if your app is sleeping
- Consider upgrading to a paid plan for production use

### Debugging
- Check the logs in Render's dashboard if the deployment fails
- Use the `/status` endpoint to verify your callback URL configuration
- Test translations with the web interface first

## File Structure
After cleanup, your repository should contain only these essential files:

```
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── models.py             # Data models
├── etranslation_service.py # EU eTranslation API client
├── error_handling.py     # Error handling utilities
├── requirements.txt      # Python dependencies
├── Procfile             # Render deployment configuration
├── templates/
│   └── index.html       # Web interface
├── static/              # CSS, JS, and other static files
└── README.md           # Project documentation
```

## Testing Your Deployment

1. Visit your Render app URL
2. Try submitting a translation request
3. Check the `/status` endpoint to verify configuration
4. Monitor the Render logs for any errors

## Support

- Render Documentation: https://render.com/docs
- EU eTranslation Documentation: https://ec.europa.eu/cefdigital/wiki/display/CEFDIGITAL/eTranslation

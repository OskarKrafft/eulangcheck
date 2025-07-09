# EU eTranslation Web Application 🇪🇺

A modern web application that provides a clean, user-friendly interface for the European Union's eTranslation API service. Built with Flask and ready for deployment on cloud platforms like Render.

## ⚠️ Important: Deployment Requirements

**The EU eTranslation service must be able to reach your callback URL to deliver translation results.** This means:

- ❌ **Local development (localhost) will NOT receive translation results**
- ✅ **Public HTTPS endpoint is required for production**
- ✅ **Cloud hosting platforms like Render work perfectly**

## Features ✨

- **Modern Web Interface**: Clean, responsive design with EU styling
- **Real-time Translation**: Asynchronous translation processing with live status updates
- **25 EU Languages**: Support for all official European Union languages
- **API Testing**: Built-in tools to test your API credentials and connection
- **Error Handling**: Comprehensive error messages and troubleshooting guidance
- **Mobile Friendly**: Responsive design that works on all devices
- **Cloud Ready**: Optimized for deployment on Render and other cloud platforms

## Supported Languages 🌍

- Bulgarian (BG), Czech (CS), Danish (DA), German (DE), Greek (EL)
- English (EN), Spanish (ES), Estonian (ET), Finnish (FI), French (FR)
- Irish (GA), Croatian (HR), Hungarian (HU), Italian (IT), Lithuanian (LT)
- Latvian (LV), Maltese (MT), Dutch (NL), Polish (PL), Portuguese (PT)
- Romanian (RO), Slovak (SK), Slovenian (SL), Swedish (SV)

## Prerequisites 📋

- Python 3.8 or higher
- EU eTranslation API credentials (Application Name and API Password)
- Internet connection for API calls
- **For production**: A cloud hosting account (Render recommended)

## Quick Start (Deploy to Render) 🚀

**Recommended for production use:**

1. **Fork or clone this repository**

3. **Set up your credentials** (IMPORTANT):
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your actual EU eTranslation credentials
2. **Deploy to Render** following the [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) guide

3. **Set up environment variables** in Render:
   ```
   ETRANSLATION_APPLICATION_NAME=your_actual_app_name
   ETRANSLATION_EMAIL=your_actual_email@domain.com
   ETRANSLATION_API_PASSWORD=your_actual_password
   PRODUCTION_URL=https://your-app-name.onrender.com
   ```

4. **Access your deployed application** at your Render URL

## Local Development 🏠

**Note: Translations will NOT complete in local mode due to callback limitations**

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd eu-language-tools-test
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file:**
   ```bash
   cp .env.example .env  # If example exists
   nano .env  # or use your preferred editor
   ```
   
   Your `.env` file should look like:
   ```
   ETRANSLATION_APPLICATION_NAME=your_actual_app_name
   ETRANSLATION_EMAIL=your_actual_email@domain.com
   ETRANSLATION_API_PASSWORD=your_actual_password
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open:** `http://localhost:5000`

## Project Structure 📁

```
eu-language-tools-test/
├── app.py                    # Main Flask application
├── config.py                # Configuration management
├── models.py                # Data models
├── etranslation_service.py   # EU eTranslation API client
├── error_handling.py        # Error handling utilities
├── requirements.txt         # Python dependencies
├── Procfile                 # Render deployment config
├── templates/
│   └── index.html          # Main translation interface
├── static/                 # Static assets (CSS, JS, images)
├── README.md              # This file
└── RENDER_DEPLOYMENT.md   # Detailed deployment guide
```

## How It Works 🔧

The application follows the official EU eTranslation documentation pattern:

1. **User submits translation request** via the web interface
2. **Flask backend processes the request** and sends it to the eTranslation API
3. **eTranslation returns a request ID** (positive number = success, negative = error)
4. **Backend stores request status** and waits for callback
5. **eTranslation calls back** with the completed translation
6. **Frontend displays the result** to the user

## API Endpoints 🛠️

- `GET /` - Main translation interface
- `POST /receiveRequest` - Submit translation request
- `POST /checkResult` - Check translation status
- `POST /callback` - Receive completed translations from eTranslation
- `GET /status` - Service status and active translations

## Error Codes 🚨

The application handles various error scenarios:

- **-1001**: Empty text provided
- **-1002**: Missing language selection
- **-1003**: Same source and target language
- **-20028**: Service busy (concurrency quota exceeded)
- **-20000**: General eTranslation error
- **-401**: Authentication failed
- **-403**: Access forbidden
- **-404**: Service not available

## Configuration ⚙️

### Environment Variables (Production)


Required environment variables:

- `ETRANSLATION_APPLICATION_NAME`: Your registered application name
- `ETRANSLATION_EMAIL`: Your registered email address  
- `ETRANSLATION_API_PASSWORD`: Your API password
- `PRODUCTION_URL`: Your production URL (for Render: `https://your-app-name.onrender.com`)

Optional environment variables:

- `ETRANSLATION_REST_URL`: API endpoint (default: official EU endpoint)
- `FLASK_PORT`: Port number (default: 5000, overridden by $PORT on Render)
- `FLASK_DEBUG`: Debug mode (default: False for production)

## Testing Your Setup 🧪

1. **Check the status endpoint:** Go to your app URL + `/status`
2. **Test translation:** Use the main interface to submit a translation
3. **Monitor logs:** Check Render's logs for any errors

## Troubleshooting 🔍

### Translation Never Completes (Most Common Issue):

**Problem**: Translations get submitted but never return results.
**Cause**: EU eTranslation service cannot reach your callback URL.

**Solutions**:
1. **Verify PRODUCTION_URL** is set correctly in environment variables
2. **Check callback URL** at `/status` endpoint
3. **Ensure HTTPS** is working on your Render deployment

### Connection and API Issues:

1. **"Authentication failed"**: 
   - Verify your Application Name and API Password
   - Check at: https://webgate.ec.europa.eu/etranslation

2. **"Access forbidden"**: 
   - Ensure your application is properly registered
   - Complete the API key request process

3. **"Service busy"**: 
   - The service has usage quotas
   - Wait a few minutes and try again

4. **"Connection failed"**: 
   - Check your internet connection
   - Verify the API endpoint is accessible

### Deployment Modes:

| Mode | Callback URL | Translations Complete? | Use Case |
|------|-------------|----------------------|----------|
| Local (`localhost`) | `http://localhost:5000/callback` | ❌ No | Development only |
| Render | `https://your-app.onrender.com/callback` | ✅ Yes | Production |

## Production Considerations 🌐

For production deployment:

1. **Monitor app sleeping**: Render free tier apps sleep after 15 minutes
2. **Consider paid plans**: For reliable 24/7 availability
3. **Set up monitoring**: Monitor translation success rates
4. **Configure logging**: Enable detailed logging for debugging

## License 📄

This project is based on the official EU eTranslation documentation examples and is intended for educational and development purposes.

## Support 🤝

- **EU eTranslation Portal**: https://webgate.ec.europa.eu/etranslation
- **Render Documentation**: https://render.com/docs
- **Project Issues**: Create an issue in this repository

---

**Built with ❤️ for the European Union eTranslation service**

For detailed deployment instructions, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)

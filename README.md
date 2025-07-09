# EU eTranslation Web Application 🇪🇺

A modern web interface for the European Union's eTranslation API service. Supports all 25 EU languages with real-time translation processing.

## ⚠️ Important

**Requires public HTTPS deployment to work.** The EU eTranslation service must reach your callback URL:
- ❌ localhost won't receive results
- ✅ Deploy to Render/similar for full functionality

## Features

- Real-time translation with live status updates
- All 25 official EU languages
- Modern responsive interface
- API credential testing
- Comprehensive error handling

## Quick Deploy to Render 🚀

1. **Fork this repository**

2. **Get EU eTranslation credentials** at https://webgate.ec.europa.eu/etranslation

3. **Deploy to Render:**
   - Connect your GitHub repo
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `gunicorn --bind 0.0.0.0:$PORT app:app`

4. **Configure environment variables:**
   ```
   ETRANSLATION_APPLICATION_NAME=your_app_name
   ETRANSLATION_EMAIL=your_email@domain.com
   ETRANSLATION_API_PASSWORD=your_password
   PRODUCTION_URL=https://eulangcheck.onrender.com
   ```

5. **Test at your Render URL**

**Detailed instructions:** [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)

## Local Development 🏠

**Note:** Translations won't complete locally due to callback limitations.

```bash
git clone <repo-url>
cd eulangcheck
pip install -r requirements.txt

# Create .env file:
ETRANSLATION_APPLICATION_NAME=your_app_name
ETRANSLATION_EMAIL=your_email@domain.com
ETRANSLATION_API_PASSWORD=your_password

python app.py
# Open http://localhost:5000
```

## How It Works

1. User submits translation via web interface
2. Request sent to EU eTranslation API  
3. API returns request ID and processes asynchronously
4. EU eTranslation calls back with completed translation
5. Result displayed to user

## Supported Languages

Bulgarian, Czech, Danish, German, Greek, English, Spanish, Estonian, Finnish, French, Irish, Croatian, Hungarian, Italian, Lithuanian, Latvian, Maltese, Dutch, Polish, Portuguese, Romanian, Slovak, Slovenian, Swedish

## Troubleshooting

### Translation Never Completes
- **Check** `PRODUCTION_URL` environment variable is correct
- **Verify** callback URL at `/status` endpoint  
- **Ensure** your deployment has HTTPS

### Common Errors
- **Authentication failed**: Verify Application Name and API Password
- **Access forbidden**: Complete API registration process
- **Service busy**: Wait and retry (quota limits)

### Testing
- Check `/status` endpoint for configuration
- Monitor deployment logs for errors
- Test with short translations first

## Resources

- **EU eTranslation Portal**: https://webgate.ec.europa.eu/etranslation
- **Detailed Deployment Guide**: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
- **Render Documentation**: https://render.com/docs

---

*Built for the European Union eTranslation service*

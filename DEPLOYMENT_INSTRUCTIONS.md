# Cookie Tracker Deployment Instructions

## 🎉 Your app is now live!
Visit: https://cookie-counter-eu-1762630027.ew.r.appspot.com

## ⚠️ Important Note about Regions
Bybit blocks API requests from US IP addresses. The app must be deployed in a non-US region (e.g., europe-west) for the API to work.

## Current Status
- The app is deployed and working with your API keys
- Shows your real Bybit trading data

## Important Note
- The app requires `gunicorn` as the WSGI server
- The `entrypoint` directive in app.yaml is required: `gunicorn -b :$PORT app:app`

## To Add Your Bybit API Keys:

### Option 1: Using app.secure.yaml (Recommended)
1. Copy your API keys from the .env file
2. Edit `app.secure.yaml` and replace:
   - `YOUR_BYBIT_API_KEY_HERE` with your actual API key
   - `YOUR_BYBIT_API_SECRET_HERE` with your actual API secret
3. Deploy with: `gcloud app deploy app.secure.yaml --quiet`

### Option 2: Using Google Cloud Console
1. Go to: https://console.cloud.google.com/appengine/settings?project=cookie-counter-eu-1762630027
2. Click on "Environment variables"
3. Add:
   - `BYBIT_API_KEY`: Your API key
   - `BYBIT_API_SECRET`: Your API secret
4. Save and redeploy

### Option 3: Using deployment script
```bash
./deploy.sh your_api_key your_api_secret
```

## Monitoring
- View logs: `gcloud app logs tail -s default`
- View in browser: `gcloud app browse`
- Check versions: `gcloud app versions list`

## Costs
- App Engine has a free tier that includes:
  - 28 instance hours per day
  - 1 GB outbound data transfer
  - This should be sufficient for personal use

## Security Notes
- Never commit app.secure.yaml with real API keys to git
- Use read-only API keys only
- Consider using Google Secret Manager for production apps

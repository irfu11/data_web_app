# DataLens Deployment Guide — Render.com

## What's Changed?

Your DataLens application has been converted from **Tkinter (desktop)** to **Streamlit (web)**.

### Benefits:
✅ Web-accessible from anywhere  
✅ No desktop installation needed  
✅ Mobile-friendly interface  
✅ Same analytics features + AI integration  

---

## Step 1: Prepare Your Local Environment

```bash
# Install Streamlit locally
pip install -r requirements.txt

# Test the app locally
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

---

## Step 2: Push to GitHub

```bash
cd "c:\Users\irfan\OneDrive\Desktop\python P"
git add .
git commit -m "Convert to Streamlit for web deployment"
git push origin main
```

---

## Step 3: Deploy to Render

### Option A: Use render.yaml (Recommended)
1. Go to https://dashboard.render.com
2. Click **"+ New" → "Web Service"**
3. Connect your GitHub repo `irfu11/data_web_app`
4. Render will automatically detect `render.yaml`
5. Click **Deploy**

### Option B: Manual Setup
1. Go to https://dashboard.render.com
2. Click **"+ New" → "Web Service"**
3. Select your GitHub repo
4. **Environment**: Python 3.10
5. **Build Command**: `pip install -r requirements.txt`
6. **Start Command**: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
7. Click **Deploy**

### Environment Variables (Optional)
If you want to pre-set your Groq API key on the deployed app:
- Add `GROQ_API_KEY` environment variable in Render dashboard
- Update `streamlit_app.py` line ~XX to read from env if not set in UI

---

## Step 4: Access Your App

Once deployment completes, Render will give you a URL like:
```
https://datalens-xyz123.onrender.com
```

Click the link to access your app! 🎉

---

## Features Available in Streamlit Version

| Feature | Status |
|---------|--------|
| Dataset Upload (CSV/Excel) | ✅ |
| Overview & Statistics | ✅ |
| Data Cleaning | ✅ |
| Visualization (8 chart types) | ✅ |
| Correlation Analysis | ✅ |
| Statistical Insights | ✅ |
| Groq AI Chat | ✅ |
| Export (CSV/Excel/JSON) | ✅ |

---

## Troubleshooting

### Problem: "Module not found" error
**Solution**: Ensure `requirements.txt` is in the root directory

### Problem: App takes too long to load
**Solution**: On free Render tier, cold starts take 30-60 seconds. Upgrade to paid for faster performance.

### Problem: File uploads fail
**Solution**: Render has a max upload size of ~100MB. Compress your data files if needed.

### Problem: Groq API errors
**Solution**: 
1. Verify your API key at https://console.groq.com
2. Check that your account is verified and active
3. Paste the key in the sidebar "API Key" field on the app

---

## Local Testing Before Deployment

```bash
# Activate virtual environment
cd "c:\Users\irfan\OneDrive\Desktop\python P"
.\.venv\Scripts\Activate.ps1

# Run the app
streamlit run streamlit_app.py

# Open browser to http://localhost:8501
```

Test all features (upload, clean, visualize, export) before deploying.

---

## Monitoring & Logs

In Render Dashboard:
1. Click your service
2. Go to **Logs** tab to see errors
3. Check **Metrics** for CPU/Memory usage

---

## Cost

- **Free Tier**: 1 app, 0.5 GB RAM, sleeps after 15 min inactivity (~$0/month)
- **Paid Tier**: Unlimited apps, 1 GB+ RAM, always running ($7+/month)

---

## Next Steps

1. ✅ **Now**: Push code and test locally
2. **Deploy**: Use render.yaml to auto-deploy
3. **Share**: Copy the Render URL and share with users
4. **Monitor**: Check Render logs if issues occur

Questions? Check Render docs: https://render.com/docs

---

**Happy analyzing! 📊**

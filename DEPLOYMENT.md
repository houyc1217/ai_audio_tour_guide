# AI Audio Tour Agent - Static HTML Deployment Guide

## 📋 Overview

This guide explains how to deploy the AI Audio Tour Agent as a static HTML application on GitHub Pages or other static hosting platforms.

## 🚀 Quick Deployment to GitHub Pages

### Method 1: Direct GitHub Pages Deployment

1. **Push to GitHub Repository**
   ```bash
   git add .
   git commit -m "Add static HTML version for GitHub Pages"
   git push origin main
   ```

2. **Enable GitHub Pages**
   - Go to your repository settings
   - Navigate to "Pages" section
   - Select "Deploy from a branch"
   - Choose "main" branch and "/ (root)" folder
   - Click "Save"

3. **Access Your Site**
   - Your site will be available at: `https://yourusername.github.io/repository-name`
   - GitHub will provide the exact URL in the Pages settings

### Method 2: GitHub Actions Deployment

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Pages
      uses: actions/configure-pages@v3
      
    - name: Upload artifact
      uses: actions/upload-pages-artifact@v2
      with:
        path: './'
        
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v2
```

## ⚠️ Important Limitations

### CORS Restrictions

The current HTML version has limitations due to browser CORS (Cross-Origin Resource Sharing) policies:

- **Direct API calls from browser may be blocked**
- **NetMind API calls require server-side proxy or CORS configuration**

### Solutions for Full Functionality

#### Option 1: Use the Python Streamlit Version
For full functionality, use the original Python application:
```bash
streamlit run ai_audio_tour_agent.py
```

#### Option 2: Deploy with Backend Proxy
Create a simple backend proxy to handle API calls:

1. **Node.js Express Proxy Example**:
```javascript
const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');

const app = express();
app.use(cors());
app.use(express.json());

// Serve static files
app.use(express.static('.'));

// Proxy endpoint for NetMind API
app.post('/api/proxy', async (req, res) => {
  try {
    const response = await fetch('https://api.netmind.ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': req.headers.authorization
      },
      body: JSON.stringify(req.body)
    });
    
    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
```

#### Option 3: Serverless Functions
Use Vercel, Netlify, or similar platforms with serverless functions:

**Vercel Example** (`api/netmind.js`):
```javascript
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const response = await fetch('https://api.netmind.ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': req.headers.authorization
      },
      body: JSON.stringify(req.body)
    });

    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
```

## 🔧 Configuration

### Environment Variables
For production deployment, consider using environment variables:

- `NETMIND_API_KEY`: Your NetMind API key
- `API_BASE_URL`: NetMind API base URL

### Security Considerations

1. **Never expose API keys in client-side code**
2. **Use environment variables for sensitive data**
3. **Implement rate limiting for API calls**
4. **Add input validation and sanitization**

## 📱 Mobile Responsiveness

The HTML version includes responsive design:
- Bootstrap 5 for responsive grid system
- Mobile-friendly form controls
- Touch-optimized buttons and inputs
- Responsive audio player

## 🎨 Customization

### Styling
Modify the CSS variables in `index.html`:
```css
:root {
    --primary-color: #2E86AB;
    --secondary-color: #A23B72;
    --accent-color: #F18F01;
    /* Add your custom colors */
}
```

### Branding
Update the NetMind branding section:
```html
<div class="netmind-branding">
    Powered by Your Company Name
</div>
```

## 🔍 Testing

### Local Testing
1. Open `index.html` in a web browser
2. Test form validation and UI interactions
3. Note: API calls will not work without proxy setup

### Production Testing
1. Deploy to staging environment
2. Test with actual API keys (if proxy is configured)
3. Verify mobile responsiveness
4. Check loading times and performance

## 📊 Analytics

Add Google Analytics or similar:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🆘 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Solution: Implement backend proxy or use serverless functions

2. **API Key Exposure**
   - Solution: Move API calls to backend/serverless functions

3. **Mobile Layout Issues**
   - Solution: Test on various devices and adjust CSS media queries

4. **Audio Playback Issues**
   - Solution: Ensure proper MIME types and browser compatibility

### Support

For technical support:
1. Check browser console for errors
2. Verify API key validity
3. Test network connectivity
4. Review deployment logs

## 📄 License

This project is open source. Please refer to the main repository for license information.
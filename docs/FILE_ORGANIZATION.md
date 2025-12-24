# File Organization Guide

## Problem Solved ✅

Previously had two `index.html` files causing confusion. Now fixed.

## Current File Structure

```
/workspaces/ai-agent/
├── templates/
│   └── index.html          ← Flask uses this (only HTML file)
├── static/
│   └── config.js           ← API configuration file
├── app.py                  ← Flask application
└── ...
```

## Key Points

### 1. **Only One index.html**
- ✅ **`templates/index.html`** - Used by Flask's `render_template()`
- ❌ **`static/index.html`** - Deleted (was causing confusion)

### 2. **Flask Routing Explanation**

```python
# Home route
@app.route('/')
def index():
    return render_template('index.html')  # Reads from templates/

# Static file route
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)  # Reads from static/
```

### 3. **Static File Access**

- **config.js**: http://localhost:5000/static/config.js
- **Other static files**: `/static/<filename>`

### 4. **Google Maps Configuration**

In [`templates/index.html`](templates/index.html):

```html
<!-- 1. Load config.js first -->
<script src="/static/config.js"></script>

<!-- 2. Then read API key -->
<script>
    let GOOGLE_MAPS_API_KEY = window.GOOGLE_MAPS_API_KEY || '';
</script>
```

In [`static/config.js`](static/config.js):

```javascript
window.GOOGLE_MAPS_API_KEY = 'AIzaSyBdHVb2k8QHkY98WSSn20rm1PNQP38Kv8Y';
```

## To Modify Frontend

**Only edit one file:**
```bash
# Edit this file
vim templates/index.html

# Restart server
python3 app.py
```

**Do NOT create `static/index.html`!** It won't be used.

## Deployment to Vercel/Render

### Vercel (Frontend)
- Uses files from `static/` directory
- `build-config.js` generates `static/config.js`
- Does not need `templates/`

### Render (Backend)
- Uses `templates/index.html`
- Needs `static/config.js`
- Flask correctly serves both directories

## Common Mistakes

### ❌ Wrong Approach
```bash
# Don't do this!
cp templates/index.html static/index.html  # Causes confusion
```

### ✅ Correct Approach
```bash
# Only edit this one file
vim templates/index.html

# Commit changes
git add templates/index.html
git commit -m "Update frontend"
git push
```

## Verify Configuration

Check if server is running correctly:

```bash
# 1. Check homepage
curl http://localhost:5000 | grep -i "shanghai"
# Should see Shanghai option

# 2. Check config.js
curl http://localhost:5000/static/config.js
# Should see API_BASE and GOOGLE_MAPS_API_KEY

# 3. Check Google Maps
curl http://localhost:5000 | grep -i "google.*maps"
# Should see Google Maps related code
```

## Summary

- **Single Source of Truth**: `templates/index.html`
- **Static Resources**: `static/` directory (CSS, JS, images, etc.)
- **No More Confusion**: Deleted redundant `static/index.html`
- **Google Maps**: Loaded correctly through `/static/config.js`

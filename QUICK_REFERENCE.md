# 🗂️ Quick Reference Guide

## 📂 Where to Find Things

### 🚀 Getting Started
```
README.md                           # Start here!
docs/deployment/VERCEL_SETUP.md    # Deploy to Vercel
docs/guides/REDIS_QUICK_START.md   # Add Redis cache
```

### 📖 Documentation Structure

```
docs/
├── guides/                  # How-to guides
│   ├── REDIS_CACHE_GUIDE.md       # Redis setup (detailed)
│   ├── REDIS_QUICK_START.md       # Redis setup (quick)
│   ├── FETCH_SPOTS_GUIDE.md       # Get spot data
│   ├── CUSTOM_SPOTS_GUIDE.md      # Add custom spots
│   ├── CHINA_SPOTS_GUIDE.md       # China-specific guide
│   ├── ENGLISH_NAMES_GUIDE.md     # Bilingual support
│   └── GAODE_API_GUIDE.md         # Gaode Maps API
│
├── deployment/              # Deployment guides
│   ├── VERCEL_SETUP.md            # Quick Vercel setup
│   ├── DEPLOY_VERCEL.md           # Detailed Vercel
│   ├── VERCEL_REDIS_GUIDE.md      # Redis on Vercel
│   ├── DEPLOY_BACKEND.md          # Backend deployment
│   └── VERCEL_CHECKLIST.md        # Deployment checklist
│
├── FILE_ORGANIZATION.md     # Old organization doc
└── PRODUCT_ROADMAP.md       # Feature roadmap
```

### 🧪 Testing
```
tests/
├── test_redis_cache.py          # Redis functionality
├── test_planning_coverage.py    # Planning algorithm
├── test_custom_spots.py         # Custom spots
└── test_shanghai_data.py        # Data integrity
```

### 🔧 Tools
```
tools/
├── redis-manager.ps1            # Redis manager (Windows)
└── redis-manager.sh             # Redis manager (Linux/macOS)
```

### 💻 Core Code
```
agent/                           # Core planning logic
├── cache.py                     # Redis cache
├── planner.py                   # Planning algorithm
├── models.py                    # Data models
└── ...

app.py                           # Web application
main.py                          # CLI interface
```

### 📊 Data
```
data/                            # City spot data
├── spots_beijing.json
├── spots_shanghai.json
└── ... (40+ cities)
```

## 🎯 Common Tasks

### Local Development

**Start the app:**
```bash
python app.py
```

**Run tests:**
```bash
python tests/test_redis_cache.py
pytest tests/
```

**Manage Redis:**
```bash
# Windows
.\tools\redis-manager.ps1

# Linux/macOS
./tools/redis-manager.sh
```

### Add New Features

**Add a new city:**
1. Create `data/spots_cityname.json`
2. Follow format in existing files
3. See [docs/guides/CUSTOM_SPOTS_GUIDE.md](docs/guides/CUSTOM_SPOTS_GUIDE.md)

**Fetch spots from OSM:**
```bash
python scripts/fetch_osm_spots.py --city "New York"
```
See [docs/guides/FETCH_SPOTS_GUIDE.md](docs/guides/FETCH_SPOTS_GUIDE.md)

### Deployment

**Deploy to Vercel:**
1. Read [docs/deployment/VERCEL_SETUP.md](docs/deployment/VERCEL_SETUP.md)
2. Connect GitHub repo
3. Set environment variables
4. Deploy!

**Add Redis to Vercel:**
1. Sign up for Upstash
2. Get connection details
3. Add to Vercel env vars
4. See [docs/deployment/VERCEL_REDIS_GUIDE.md](docs/deployment/VERCEL_REDIS_GUIDE.md)

## 📝 File Naming Conventions

- **Documentation**: `UPPER_CASE.md`
- **Python code**: `snake_case.py`
- **Test files**: `test_*.py`
- **Shell scripts**: `kebab-case.sh`
- **PowerShell**: `PascalCase.ps1`

## 🔗 External Links

- [Upstash](https://upstash.com/) - Redis for serverless
- [Vercel](https://vercel.com/) - Deployment platform
- [OpenStreetMap](https://www.openstreetmap.org/) - Map data source

## 💡 Tips

**Finding documentation:**
- Local setup → `docs/guides/`
- Deployment → `docs/deployment/`
- Quick start → `README.md`

**Running scripts:**
- Data processing → `scripts/`
- Utilities → `tools/`
- Tests → `tests/`

**Configuration:**
- Copy `.env.example` to `.env`
- Never commit `.env` file
- Use Vercel dashboard for production env vars

## 🆘 Need Help?

1. Check [README.md](../README.md) first
2. Look in appropriate `docs/` subdirectory
3. Check [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for file locations
4. See test files for code examples

## 📱 Quick Commands Cheatsheet

```bash
# Development
python app.py                    # Start web app
python main.py                   # CLI interface

# Testing
python tests/test_redis_cache.py # Test Redis
pytest tests/                    # Run all tests

# Redis
.\tools\redis-manager.ps1        # Windows manager
./tools/redis-manager.sh         # Unix manager
docker run -d redis:7-alpine     # Quick Redis

# Data
python scripts/fetch_osm_spots.py --city "Paris"
python scripts/add_english_names.py --city beijing

# Git
git status                       # Check changes
git add .                        # Stage all
git commit -m "message"          # Commit
git push origin main             # Deploy (if Vercel connected)
```

## 🎨 Project at a Glance

```
📦 Travel-Planning-Agent
│
├── 🎯 Entry Points
│   ├── app.py         → Web application
│   └── main.py        → CLI interface
│
├── 🧠 Core Logic
│   └── agent/         → Planning algorithms
│
├── 📊 Data
│   └── data/          → City spot data (40+ cities)
│
├── 📖 Documentation
│   ├── docs/guides/   → User guides
│   └── docs/deployment/ → Deploy guides
│
├── 🧪 Quality
│   └── tests/         → All tests
│
└── 🔧 Utilities
    ├── scripts/       → Data processing
    └── tools/         → Dev tools
```

---

**Remember**: When in doubt, check the README! 📖

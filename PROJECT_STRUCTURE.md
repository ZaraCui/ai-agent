# 📁 Project Structure

## Current Organization (After Cleanup)

```
Travel-Planning-Agent/
├── 📄 README.md                 # Main project documentation
├── 📄 LICENSE                   # Project license
│
├── 🐍 Core Application Files
│   ├── app.py                   # Flask web application (main entry)
│   ├── main.py                  # CLI interface for planning
│   └── requirements.txt         # Python dependencies
│
├── 📁 agent/                    # Core planning agent logic
│   ├── cache.py                 # Redis cache management
│   ├── constraints.py           # Soft constraint scoring
│   ├── explainer.py             # Explanation generation
│   ├── geometry.py              # Distance and travel time calculations
│   ├── llm.py                   # LLM integration
│   ├── models.py                # Data models (Spot, DayPlan, Itinerary)
│   ├── planner.py               # Core planning algorithm
│   ├── reasoning.py             # Reasoning logic
│   ├── replanner.py             # Replanning functionality
│   ├── semantics.py             # Semantic analysis
│   └── weather.py               # Weather integration
│
├── 📁 data/                     # City spot data (JSON files)
│   ├── spots_beijing.json
│   ├── spots_shanghai.json
│   ├── spots_tokyo.json
│   └── ... (40+ cities)
│
├── 📁 static/                   # Frontend static files
│   ├── index.html               # Main web interface
│   ├── config.js                # Frontend configuration
│   └── assets/                  # CSS, JS, images
│
├── 📁 templates/                # Flask HTML templates
│   └── index.html               # Server-side rendered page
│
├── 📁 scripts/                  # Data processing scripts
│   ├── fetch_osm_spots.py       # Fetch spots from OpenStreetMap
│   ├── add_english_names.py    # Add English names to spots
│   ├── enrich_spots.py          # Enrich spot data
│   └── ...
│
├── 📁 tests/                    # Test files
│   ├── test_redis_cache.py      # Redis cache tests
│   ├── test_planning_coverage.py# Planning algorithm tests
│   ├── test_custom_spots.py     # Custom spots tests
│   └── ...
│
├── 📁 tools/                    # Utility tools
│   ├── redis-manager.ps1        # Redis management (Windows)
│   └── redis-manager.sh         # Redis management (Linux/macOS)
│
├── 📁 docs/                     # Documentation
│   ├── 📁 guides/               # User guides
│   │   ├── REDIS_CACHE_GUIDE.md
│   │   ├── REDIS_QUICK_START.md
│   │   ├── FETCH_SPOTS_GUIDE.md
│   │   ├── CHINA_SPOTS_GUIDE.md
│   │   ├── CUSTOM_SPOTS_GUIDE.md
│   │   ├── ENGLISH_NAMES_GUIDE.md
│   │   ├── ENRICH_SPOTS_GUIDE.md
│   │   ├── GAODE_API_GUIDE.md
│   │   ├── API_FETCH_SPOTS.md
│   │   ├── WEBSOCKET_PROGRESS.md
│   │   └── REDIS_IMPLEMENTATION_SUMMARY.md
│   │
│   ├── 📁 deployment/           # Deployment guides
│   │   ├── DEPLOY_VERCEL.md
│   │   ├── DEPLOY_BACKEND.md
│   │   ├── VERCEL_SETUP.md
│   │   ├── VERCEL_CHECKLIST.md
│   │   └── VERCEL_REDIS_GUIDE.md
│   │
│   ├── FILE_ORGANIZATION.md     # This file
│   └── PRODUCT_ROADMAP.md       # Feature roadmap
│
├── 📁 deploy/                   # Deployment configurations
│   └── nginx.conf               # Nginx configuration
│
├── 📁 output/                   # Generated output files
│   └── *.html                   # Generated map visualizations
│
├── 🐳 Deployment Files
│   ├── Dockerfile               # Docker container definition
│   ├── docker-compose.yml       # Docker Compose configuration
│   ├── Procfile                 # Heroku deployment
│   ├── runtime.txt              # Python runtime version
│   ├── vercel.json              # Vercel configuration
│   └── vercel-build.sh          # Vercel build script
│
└── 🔧 Configuration Files
    ├── .env.example             # Environment variables template
    ├── .gitignore               # Git ignore rules
    ├── .dockerignore            # Docker ignore rules
    ├── .vercelignore            # Vercel ignore rules
    ├── package.json             # Node.js dependencies (if any)
    └── build-config.js          # Build configuration
```

## Directory Purposes

### 📁 Root Directory
- **Core application files**: `app.py`, `main.py`, `requirements.txt`
- **Documentation entry point**: `README.md`
- **Configuration files**: `.env`, `.env.example`, etc.

### 📁 agent/
**Core planning logic and algorithms**
- Planning algorithms and search
- Constraint evaluation
- Data models
- Cache management
- LLM integration

### 📁 data/
**City spot data**
- JSON files for each supported city
- Standardized format with bilingual support
- Used by planning algorithm

### 📁 static/
**Frontend assets**
- Single-page application (SPA)
- HTML, CSS, JavaScript
- Client-side configuration

### 📁 templates/
**Server-rendered templates**
- Flask/Jinja2 templates
- Alternative to static SPA

### 📁 scripts/
**Data processing and utilities**
- Fetch spots from APIs
- Enrich spot data
- Data transformation
- One-time processing tasks

### 📁 tests/
**Test files**
- Unit tests
- Integration tests
- Performance tests
- All files matching `test_*.py`

### 📁 tools/
**Development and operations tools**
- Redis management scripts
- Deployment helpers
- Database utilities

### 📁 docs/
**All documentation**

#### docs/guides/
User guides and tutorials:
- Redis cache setup
- Spot data management
- API usage
- Feature guides

#### docs/deployment/
Deployment documentation:
- Vercel deployment
- Backend deployment
- Cloud services setup
- Configuration guides

### 📁 deploy/
**Deployment configurations**
- Server configs (nginx, apache)
- Cloud platform configs
- Infrastructure as code

### 📁 output/
**Generated files**
- Map visualizations
- Reports
- Temporary outputs
- (Gitignored, not committed)

## File Organization Rules

### 1. Documentation Files
- **Guides** → `docs/guides/`
- **Deployment** → `docs/deployment/`
- **Architecture** → `docs/`
- **README** → Root (main entry point)

### 2. Code Files
- **Core logic** → `agent/`
- **Web app** → `app.py` (root)
- **CLI** → `main.py` (root)
- **Scripts** → `scripts/`

### 3. Test Files
- All `test_*.py` → `tests/`
- Test data → `tests/fixtures/` (if needed)

### 4. Configuration Files
- **Environment** → `.env`, `.env.example` (root)
- **Deployment** → `vercel.json`, `Dockerfile` (root)
- **Build** → `package.json`, `build-config.js` (root)

### 5. Data Files
- **Spot data** → `data/`
- **Generated output** → `output/`

### 6. Tools and Scripts
- **User-facing tools** → `tools/`
- **Data processing** → `scripts/`

## Quick Access

### 🚀 Getting Started
- Setup: [README.md](../README.md)
- Redis: [docs/guides/REDIS_QUICK_START.md](guides/REDIS_QUICK_START.md)

### 📖 User Guides
- Cache: [docs/guides/REDIS_CACHE_GUIDE.md](guides/REDIS_CACHE_GUIDE.md)
- Spots: [docs/guides/FETCH_SPOTS_GUIDE.md](guides/FETCH_SPOTS_GUIDE.md)
- Custom Data: [docs/guides/CUSTOM_SPOTS_GUIDE.md](guides/CUSTOM_SPOTS_GUIDE.md)

### 🚢 Deployment
- Vercel: [docs/deployment/VERCEL_SETUP.md](deployment/VERCEL_SETUP.md)
- Redis on Vercel: [docs/deployment/VERCEL_REDIS_GUIDE.md](deployment/VERCEL_REDIS_GUIDE.md)
- Backend: [docs/deployment/DEPLOY_BACKEND.md](deployment/DEPLOY_BACKEND.md)

### 🧪 Testing
- Run all tests: `pytest tests/`
- Redis tests: `python tests/test_redis_cache.py`

### 🔧 Tools
- Redis manager: `./tools/redis-manager.ps1` or `./tools/redis-manager.sh`

## Migration Guide

If you're reorganizing an existing installation:

1. **Run the organization script**:
   ```bash
   # Windows
   .\organize.ps1
   
   # Linux/macOS
   chmod +x organize.sh
   ./organize.sh
   ```

2. **Update import paths** (if any scripts referenced old paths)

3. **Update git**:
   ```bash
   git add .
   git commit -m "Reorganize project structure"
   ```

4. **Update documentation links** in your own docs (if any)

## Benefits of This Structure

✅ **Clear separation of concerns**
- Documentation separate from code
- Tests isolated from application
- Tools separate from scripts

✅ **Easy navigation**
- Find guides quickly in `docs/guides/`
- All tests in one place
- Clear deployment documentation

✅ **Better maintainability**
- Logical grouping
- Standard conventions
- Scalable structure

✅ **Improved discoverability**
- New contributors can find things easily
- Self-documenting structure
- Industry-standard layout

## Conventions

### File Naming
- **Code**: `snake_case.py`
- **Docs**: `UPPER_CASE.md`
- **Tests**: `test_*.py`
- **Tools**: `kebab-case.sh` or `PascalCase.ps1`

### Directory Naming
- **Code**: `lowercase`
- **Docs**: `lowercase`
- All directories use single words or underscores

## Future Considerations

As the project grows, consider:

- `api/` directory for API-specific code
- `models/` for database models (if using DB)
- `services/` for business logic services
- `utils/` for shared utilities
- `config/` for configuration files
- `migrations/` for database migrations
- `logs/` for application logs (gitignored)

## Related Documentation

- [README.md](../README.md) - Main documentation
- [PRODUCT_ROADMAP.md](PRODUCT_ROADMAP.md) - Feature roadmap
- [REDIS_CACHE_GUIDE.md](guides/REDIS_CACHE_GUIDE.md) - Redis setup
- [VERCEL_SETUP.md](deployment/VERCEL_SETUP.md) - Deployment guide

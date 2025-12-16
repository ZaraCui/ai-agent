#!/bin/bash
# Vercel build hook: 生成 static/config.js 注入 API_BASE 和 GOOGLE_MAPS_API_KEY
mkdir -p static
cat > static/config.js <<JS
const API_BASE = '${API_BASE:-https://travel-planning-agent.onrender.com}';
const GOOGLE_MAPS_API_KEY = '${GOOGLE_MAPS_API_KEY}';
JS

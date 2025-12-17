# 部署到 Vercel 的配置指南

## 问题说明

本地运行时使用 `templates/index.html`（包含 Google Maps），而 Vercel 部署使用 `static/index.html`。已经将 Google Maps 集成代码添加到静态版本。

## 配置步骤

### 1. 获取 Google Maps API Key

1. 访问 [Google Cloud Console](https://console.cloud.google.com/google/maps-apis)
2. 创建新项目或选择现有项目
3. 启用 **Maps JavaScript API**
4. 创建 API 密钥（建议：限制密钥使用范围到你的域名）

### 2. 配置 static/config.js

编辑 `/workspaces/ai-agent/static/config.js` 文件：

```javascript
const API_BASE = 'https://travel-planning-agent.onrender.com';  // 你的后端 API 地址

// 替换为你的 Google Maps API Key
window.GOOGLE_MAPS_API_KEY = 'AIzaSy...你的密钥';  // ⚠️ 重要：替换这个值！
```

### 3. 部署到 Vercel

```bash
# 确保 static/config.js 已正确配置
git add static/config.js
git commit -m "Configure Google Maps API key"
git push

# Vercel 会自动部署（如果已连接 GitHub）
# 或手动部署：
vercel --prod
```

### 4. 验证部署

访问你的 Vercel 网站，检查：
- 表单可以提交
- 行程规划结果显示
- **Google Maps 地图正常显示**（在行程下方）

## 常见问题

### Q: 地图不显示？

检查浏览器控制台是否有错误：

1. **API Key 错误**
   - 错误: "Google Maps API error: InvalidKeyMapError"
   - 解决: 检查 `static/config.js` 中的 API key 是否正确

2. **API 未启用**
   - 错误: "Google Maps JavaScript API has not been authorized"
   - 解决: 在 Google Cloud Console 中启用 Maps JavaScript API

3. **域名限制**
   - 错误: "RefererNotAllowedMapError"
   - 解决: 在 Google Cloud Console 中添加你的 Vercel 域名到 API key 的允许列表

### Q: 为什么本地能显示但 Vercel 不能？

- **本地**: Flask 使用 `templates/index.html`
- **Vercel**: 使用 `static/index.html`（现已包含地图代码）
- **解决**: 确保 `static/config.js` 配置了正确的 API key

### Q: 如何保护我的 API Key？

Google Maps API key 在前端使用时无法完全隐藏，建议：

1. **限制密钥使用**
   - 在 Google Cloud Console 中限制密钥只能从你的域名使用
   - 添加 HTTP referrer 限制（例如：`*.vercel.app/*`）

2. **设置使用配额**
   - 设置每日使用配额防止滥用
   - 启用计费提醒

3. **监控使用情况**
   - 定期检查 API 使用情况
   - 如发现异常立即重新生成密钥

## 文件说明

- `static/index.html` - 静态前端页面（Vercel 部署）
- `static/config.js` - 运行时配置（**需手动创建和配置**）
- `static/config.example.js` - 配置模板
- `templates/index.html` - Flask 模板（本地开发）
- `vercel.json` - Vercel 部署配置

## 安全建议

⚠️ **不要将包含真实 API key 的 `static/config.js` 提交到公开仓库！**

建议将 `static/config.js` 添加到 `.gitignore`：

```bash
echo "static/config.js" >> .gitignore
```

然后在 Vercel 上直接编辑或通过环境变量注入。

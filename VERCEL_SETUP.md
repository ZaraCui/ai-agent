# 🚀 Vercel 快速设置指南

## 立即修复地图不显示问题

### 步骤 1: 在 Vercel 设置环境变量

1. 访问你的 Vercel 项目: https://vercel.com/dashboard
2. 选择你的项目
3. 点击 **Settings** → **Environment Variables**
4. 添加以下两个变量：

```
名称: GOOGLE_MAPS_API_KEY
值: [你的 Google Maps API 密钥]
环境: ✅ Production ✅ Preview ✅ Development
```

```
名称: API_BASE
值: https://travel-planning-agent.onrender.com
环境: ✅ Production ✅ Preview ✅ Development
```

### 步骤 2: 获取 Google Maps API Key（如果还没有）

1. 访问: https://console.cloud.google.com/google/maps-apis
2. 创建或选择项目
3. 启用 **Maps JavaScript API**
4. 转到 **凭据** → **创建凭据** → **API 密钥**
5. 复制生成的密钥

### 步骤 3: 限制 API Key（推荐）

1. 在 Google Cloud Console 中点击你的 API 密钥
2. 选择 **应用限制** → **HTTP referrer**
3. 添加网站限制：
   ```
   https://*.vercel.app/*
   http://localhost:*
   ```
4. 点击 **保存**

### 步骤 4: 触发重新部署

在 Vercel 项目中：
1. 转到 **Deployments** 选项卡
2. 点击最新部署的 **⋯** 菜单
3. 选择 **Redeploy**
4. 等待部署完成

## ✅ 验证

部署完成后访问你的网站：
1. 填写表单并提交
2. 应该看到：
   - ✅ 行程规划结果
   - ✅ 地图显示（带有标记和路线）
   - ✅ 没有控制台错误

## 🐛 故障排查

### 问题：地图还是不显示

打开浏览器开发者工具（F12）查看控制台：

**错误**: `Google Maps API error: InvalidKeyMapError`
- 原因：API key 不正确
- 解决：检查 Vercel 环境变量中的 `GOOGLE_MAPS_API_KEY` 是否正确

**错误**: `Google Maps JavaScript API has not been authorized`
- 原因：API 未启用
- 解决：在 Google Cloud Console 启用 Maps JavaScript API

**错误**: `RefererNotAllowedMapError`
- 原因：域名限制不匹配
- 解决：在 Google Cloud 中添加你的 Vercel 域名到 API key 的允许列表

**错误**: `GOOGLE_MAPS_API_KEY is undefined`
- 原因：环境变量未设置或未生效
- 解决：确认已在 Vercel 设置环境变量并重新部署

### 问题：点击按钮没反应

打开浏览器开发者工具查看网络请求：

**错误**: `Failed to fetch` 或 CORS 错误
- 原因：后端 API 不可达或 CORS 配置问题
- 解决：确认 `API_BASE` 环境变量正确，后端服务正常运行

## 📝 技术细节

构建过程中发生了什么：

1. Vercel 运行 `npm run build`
2. 执行 `node build-config.js`
3. 读取环境变量 `API_BASE` 和 `GOOGLE_MAPS_API_KEY`
4. 生成 `static/config.js`：
   ```javascript
   const API_BASE = 'https://...';
   window.GOOGLE_MAPS_API_KEY = 'AIza...';
   ```
5. 部署静态文件到 Vercel

## 📚 更多信息

- [完整部署指南](DEPLOY_VERCEL.md)
- [检查清单](VERCEL_CHECKLIST.md)

# 部署到 Vercel 的配置指南

## 问题说明

本地运行时使用 `templates/index.html`（包含 Google Maps），而 Vercel 部署使用 `static/index.html`。已经将 Google Maps 集成代码添加到静态版本。

## 配置步骤

### 1. 获取 Google Maps API Key

1. 访问 [Google Cloud Console](https://console.cloud.google.com/google/maps-apis)
2. 创建新项目或选择现有项目
3. 启用 **Maps JavaScript API**
4. 创建 API 密钥（建议：限制密钥使用范围到你的域名）

### 2. 在 Vercel 中配置环境变量

⚠️ **重要**: 不要在代码中硬编码 API key，使用 Vercel 的环境变量功能。

1. 登录 Vercel 并进入你的项目
2. 进入 **Settings** > **Environment Variables**
3. 添加以下环境变量：

```
变量名: API_BASE
值: https://travel-planning-agent.onrender.com
环境: Production, Preview, Development

变量名: GOOGLE_MAPS_API_KEY  
值: AIza...你的真实密钥
环境: Production, Preview, Development
```

### 3. 部署到 Vercel

```bash
# 提交代码
git add .
git commit -m "Add Google Maps integration"
git push origin main

# Vercel 会自动部署（如果已连接 GitHub）
# 构建过程会读取环境变量并生成 static/config.js
```

构建脚本 (`build-config.js`) 会在部署时自动：
- 读取环境变量 `API_BASE` 和 `GOOGLE_MAPS_API_KEY`
- 生成 `static/config.js` 文件
- 注入到静态网站中

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
- **解决**: 在 Vercel 项目设置中配置环境变量 `GOOGLE_MAPS_API_KEY`

### Q: 构建脚本如何工作？

`build-config.js` 在构建时：
1. 读取环境变量 `API_BASE` 和 `GOOGLE_MAPS_API_KEY`
2. 生成 `static/config.js`：
   ```javascript
   const API_BASE = 'https://...';
   window.GOOGLE_MAPS_API_KEY = 'AIza...';
   ```
3. 静态网站加载此配置文件

### Q: 如何保护我的 API Key？

Google Maps API key 在前端使用时无法完全隐藏，建议：

1. **使用 Vercel 环境变量**
   - 不要在代码中硬编码 API key
   - 使用 Vercel 的环境变量功能
   - 不会暴露在 GitHub 仓库中

2. **限制密钥使用**
   - 在 Google Cloud Console 中限制密钥只能从你的域名使用
   - 添加 HTTP referrer 限制（例如：`*.vercel.app/*`）

3. **设置使用配额**
   - 设置每日使用配额防止滥用
   - 启用计费提醒

4. **监控使用情况**
   - 定期检查 API 使用情况
   - 如发现异常立即重新生成密钥

## 文件说明

- `static/index.html` - 静态前端页面（Vercel 部署）
- `build-config.js` - 构建脚本，生成 config.js
- `static/config.example.js` - 配置模板（仅供参考）
- `templates/index.html` - Flask 模板（本地开发）
- `vercel.json` - Vercel 部署配置
- `package.json` - 定义构建命令

## 安全建议

⚠️ **使用 Vercel 环境变量，不要在代码中硬编码 API key！**

`static/config.js` 会在构建时自动生成，不需要提交到仓库。`.gitignore` 已配置忽略此文件。

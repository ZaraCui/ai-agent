# ✅ Vercel 部署前检查清单

## 🔧 必须完成的配置

### 1. 在 Vercel 设置环境变量

**重要**: Vercel 会在构建时自动生成 `static/config.js`，不需要手动编辑。

在 Vercel 项目设置中添加环境变量：

1. 访问你的 Vercel 项目仪表板
2. 进入 **Settings** > **Environment Variables**
3. 添加以下变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `API_BASE` | `https://travel-planning-agent.onrender.com` | 后端 API 地址 |
| `GOOGLE_MAPS_API_KEY` | `AIza...` | 你的 Google Maps API 密钥 |

**获取 Google Maps API Key**:
1. 访问: https://console.cloud.google.com/google/maps-apis
2. 创建/选择项目
3. 启用 "Maps JavaScript API"
4. 创建凭据 > API 密钥

### 2. 限制 API Key（推荐）

在 Google Cloud Console 中：
- 应用限制 > HTTP referrer
- 添加网站限制:
  - `https://your-project.vercel.app/*`
  - `https://*.vercel.app/*` (如果使用预览部署)
  - `http://localhost:*` (本地测试)

### 3. 检查文件

确认这些文件存在且配置正确:

- ✅ `static/index.html` - 已包含 Google Maps 代码
- ✅ `build-config.js` - 构建时生成 config.js
- ✅ `vercel.json` - 部署配置

## 🚀 部署步骤

```bash
# 1. 提交代码到 GitHub
git add .
git commit -m "Add Google Maps integration"
git push origin main

# 2. 在 Vercel 项目中设置环境变量（见上方）

# 3. Vercel 会自动重新部署
# 或者手动触发: Deployments > Redeploy
```

**不需要**手动创建或编辑 `static/config.js`，构建脚本会自动生成！

## ⚠️ 重要提示

1. **不要提交真实的 API key 到 GitHub**
   - `static/config.js` 已在 `.gitignore` 中
   - 只提交 `config.example.js` 作为模板
使用 Vercel 环境变量**
   - 不要在代码中硬编码 API key
   - 使用 Vercel 的环境变量功能
   - 构建脚本会自动读取并生成配置文件

2. **在 Vercel 上配置**
   - Settings > Environment Variables
   - 添加 `GOOGLE_MAPS_API_KEY` 和 `API_BASE`
   - 保存后重新部署
   - 检查浏览器控制台无错误
   - 验证标记和路线正确显示

## 📱 故障排查

| 问题 | 检查项 |
|------|--------|
| 地图不显示 | 1. 查看浏览器控制台错误<br>2. 确认 API key 正确<br>3. 检查 API 是否启用 |
| "InvalidKeyMapError" | API key 不正确 |
| "RefererNotAllowedMapError" | 需要添加域名到 API key 限制列表 |
| "ApiNotActivatedMapError" | 需要在 Google Cloud 启用 Maps JavaScript API |

## 📚 参考文档

- [完整部署指南](DEPLOY_VERCEL.md)
- [Google Maps API 文档](https://developers.google.com/maps/documentation/javascript)
- [Vercel 部署文档](https://vercel.com/docs)

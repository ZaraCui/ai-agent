# ✅ Vercel 部署前检查清单

## 🔧 必须完成的配置

### 1. 配置 Google Maps API Key

**文件**: `static/config.js`

```javascript
const API_BASE = 'https://travel-planning-agent.onrender.com';
window.GOOGLE_MAPS_API_KEY = 'AIzaSy...';  // ⚠️ 替换为你的真实密钥
```

**获取 API Key**:
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
- ✅ `static/config.js` - **需要你手动配置 API key**
- ✅ `vercel.json` - 部署配置
- ✅ `.gitignore` - 已添加 `static/config.js`

## 🚀 部署步骤

```bash
# 1. 创建 config.js（从示例复制）
cp static/config.example.js static/config.js

# 2. 编辑 config.js 添加你的 API key
nano static/config.js

# 3. 提交更改（config.js 会被 .gitignore 忽略）
git add .
git commit -m "Add Google Maps integration to static frontend"
git push

# 4. Vercel 自动部署（如果已连接 GitHub）
# 或手动：vercel --prod
```

## ⚠️ 重要提示

1. **不要提交真实的 API key 到 GitHub**
   - `static/config.js` 已在 `.gitignore` 中
   - 只提交 `config.example.js` 作为模板

2. **在 Vercel 上配置**
   - 方法 1: 部署后通过 Vercel 仪表板直接编辑文件
   - 方法 2: 在 Vercel 项目设置中使用环境变量（需修改代码读取方式）

3. **测试地图功能**
   - 提交表单后应看到地图显示
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

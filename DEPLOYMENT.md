# 部署到 Vercel 指南

本项目已经配置好可以直接部署到 Vercel。有两种部署方式可选：

## 方式一：通过 Vercel Web 界面部署（推荐）

这是最简单的方式，无需命令行操作。

### 步骤：

1. **访问 Vercel**
   - 打开 [https://vercel.com](https://vercel.com)
   - 使用 GitHub 账号登录

2. **导入项目**
   - 点击 "Add New..." → "Project"
   - 选择 "Import Git Repository"
   - 找到并选择你的 `duomiblog` 仓库
   - 选择分支：`claude/clone-raphael-app-011CULrtuPqmDMECNw8SR5ci`

3. **配置项目**
   - **Project Name**: 可以自定义，例如 `raphael-ai-clone`
   - **Framework Preset**: Next.js (自动检测)
   - **Root Directory**: `./` (默认)
   - **Build Command**: `npm run build` (默认)
   - **Output Directory**: `.next` (默认)
   - **Install Command**: `npm install` (默认)

4. **部署**
   - 点击 "Deploy" 按钮
   - 等待构建完成（通常需要 1-3 分钟）
   - 部署成功后，你会获得一个 `.vercel.app` 域名

5. **访问网站**
   - 部署完成后，点击提供的 URL 即可访问你的网站
   - 例如：`https://raphael-ai-clone.vercel.app`

### 自动部署

配置完成后，每次推送到该分支时，Vercel 会自动重新部署。

---

## 方式二：通过 Vercel CLI 部署

如果你更喜欢使用命令行，可以使用 Vercel CLI。

### 步骤：

1. **登录 Vercel**
   ```bash
   vercel login
   ```
   - 输入你的 Vercel 账号邮箱
   - 在浏览器中确认登录

2. **部署项目**
   ```bash
   # 首次部署
   vercel
   ```

   按照提示操作：
   - Set up and deploy? `Y`
   - Which scope? 选择你的账号或团队
   - Link to existing project? `N`
   - What's your project's name? `raphael-ai-clone`
   - In which directory is your code located? `./`
   - Want to override the settings? `N`

3. **部署到生产环境**
   ```bash
   vercel --prod
   ```

4. **后续部署**
   ```bash
   # 每次更新后，直接运行
   vercel --prod
   ```

---

## 环境变量配置（如果需要）

如果将来集成真实的 AI API，需要添加环境变量：

### 通过 Web 界面：
1. 进入 Vercel 项目设置
2. 点击 "Settings" → "Environment Variables"
3. 添加所需的环境变量，例如：
   - `NEXT_PUBLIC_API_KEY`
   - `API_ENDPOINT`

### 通过 CLI：
```bash
vercel env add NEXT_PUBLIC_API_KEY
```

---

## 自定义域名

部署成功后，如果想使用自己的域名：

1. 在 Vercel 项目设置中
2. 点击 "Settings" → "Domains"
3. 输入你的域名
4. 按照说明配置 DNS 记录

---

## 故障排查

### 构建失败
- 检查 `package.json` 中的依赖是否正确
- 查看 Vercel 构建日志中的错误信息
- 确保本地 `npm run build` 可以成功运行

### 部署成功但页面空白
- 检查浏览器控制台的错误信息
- 确保所有环境变量都已正确配置

### 需要更多帮助
- 访问 Vercel 文档：[https://vercel.com/docs](https://vercel.com/docs)
- 查看 Next.js 部署文档：[https://nextjs.org/docs/deployment](https://nextjs.org/docs/deployment)

---

## 快速命令参考

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录
vercel login

# 部署到预览环境
vercel

# 部署到生产环境
vercel --prod

# 查看部署列表
vercel ls

# 查看项目信息
vercel inspect

# 删除部署
vercel remove [deployment-url]
```

---

## 推荐设置

- ✅ 启用自动部署（Push to Deploy）
- ✅ 启用预览部署（Preview Deployments）
- ✅ 配置自定义域名（可选）
- ✅ 设置环境变量（如果需要 API keys）
- ✅ 启用分析（Analytics）来监控性能

---

祝你部署成功！🚀

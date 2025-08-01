# 🚀 GitHub + Vercel 部署指南

## 1. 创建GitHub仓库

### 方式1: 使用GitHub CLI
```bash
# 安装GitHub CLI (如果未安装)
brew install gh

# 登录GitHub
gh auth login

# 创建私有仓库
gh repo create stock-monitor-vercel --private --description "Stock monitoring system with real-time prices and news" --source=.
```

### 方式2: 手动创建
1. 访问 [github.com/new](https://github.com/new)
2. 仓库名称: `stock-monitor-vercel`
3. 设置为私有仓库
4. 不初始化README (因为已有文件)

## 2. 推送代码到GitHub

```bash
# 如果使用手动创建的仓库，请替换为您的仓库URL
git remote set-url origin https://github.com/your-username/stock-monitor-vercel.git
git branch -M main
git push -u origin main
```

## 3. 连接Vercel自动部署

### 方式1: 使用Vercel CLI
```bash
# 安装Vercel CLI
npm i -g vercel

# 登录Vercel
vercel login

# 部署并连接GitHub
vercel --prod
# 选择 "Yes" 连接到GitHub
```

### 方式2: 手动连接
1. 访问 [vercel.com](https://vercel.com)
2. 点击 "New Project"
3. 选择 "Import Git Repository"
4. 选择您的GitHub仓库 `stock-monitor-vercel`
5. 配置环境变量:
   - `NEWS_API_KEY`: 您的NewsAPI密钥
6. 点击 "Deploy"

## 4. 设置环境变量

### 在Vercel上设置:
```bash
# 使用Vercel CLI
vercel env add NEWS_API_KEY production
# 输入您的NewsAPI密钥

# 或者一次性设置多个环境
vercel env add NEWS_API_KEY production
vercel env add NEWS_API_KEY preview
vercel env add NEWS_API_KEY development
```

### 在GitHub上设置（可选）:
1. 进入仓库 Settings → Secrets and variables → Actions
2. 添加 `NEWS_API_KEY` 作为仓库密钥

## 5. 验证部署

部署完成后，访问:
- 生产环境: `https://your-project-name.vercel.app`
- API测试: `https://your-project-name.vercel.app/api/prices`
- 健康检查: `https://your-project-name.vercel.app/api/health`

## 6. 后续更新

每次推送到main分支将自动触发Vercel部署:

```bash
# 日常开发
# 修改代码后
git add .
git commit -m "描述您的更改"
git push origin main

# 自动部署将在几分钟内完成
```

## 📋 检查清单

- [ ] GitHub仓库已创建
- [ ] 代码已推送到GitHub
- [ ] Vercel项目已连接
- [ ] NEWS_API_KEY 环境变量已设置
- [ ] 首次部署成功
- [ ] 功能测试通过

## 🔧 故障排除

### 如果推送失败:
```bash
# 检查远程URL
git remote -v

# 更新远程URL
git remote set-url origin https://github.com/[YOUR-USERNAME]/stock-monitor-vercel.git

# 强制推送
git push -u origin main --force
```

### 如果部署失败:
- 检查 `vercel.json` 配置
- 确认 `requirements.txt` 包含所有依赖
- 检查环境变量是否正确设置
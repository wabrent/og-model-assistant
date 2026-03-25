# GitHub Deployment Guide

## Step 1: Prepare Your Repository

### Create GitHub Account
1. Go to https://github.com
2. Sign up for a free account
3. Verify your email

### Create New Repository
1. Click the "+" icon in top right
2. Select "New repository"
3. Repository name: `og-model-assistant`
4. Description: "AI-powered assistant for OpenGradient Model Hub"
5. Choose Public or Private
6. **Don't** initialize with README (we already have one)
7. Click "Create repository"

## Step 2: Initialize Git Locally

```bash
# Navigate to project directory
cd c:\Users\waabrent\Documents\trae_projects\opengradientapp\og-model-assistant-pro

# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: OpenGradient Model Hub Assistant

Features:
- AI-powered model search
- Chat interface with OpenGradient LLM
- Voice input support
- Vision AI for image analysis
- Free token faucet (auto-claim every 5h)
- Dark/Light themes
- Analytics and statistics
- Telegram/Discord bots support

Built with FastAPI, SQLAlchemy, and Vanilla JS"
```

## Step 3: Connect to GitHub

```bash
# Add GitHub as remote origin
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/og-model-assistant.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Verify on GitHub

1. Go to https://github.com/YOUR_USERNAME/og-model-assistant
2. You should see all your files
3. Check that README.md displays correctly
4. Verify all folders are present

## Step 5: Update Repository Settings

### Add Topics
1. Go to repository settings
2. Add topics:
   - `opengradient`
   - `ai`
   - `fastapi`
   - `llm`
   - `chatbot`
   - `model-hub`
   - `python`

### Add Description
1. In repository settings
2. Add description: "AI-powered assistant for discovering and exploring AI models on OpenGradient Model Hub"
3. Add website: https://www.opengradient.ai/

## Step 6: Deploy to Vercel (Optional)

### Connect Vercel to GitHub
1. Go to https://vercel.com
2. Sign in with GitHub
3. Click "New Project"
4. Import your `og-model-assistant` repository
5. Configure:
   - **Framework Preset**: FastAPI
   - **Root Directory**: `./`
   - **Build Command**: `pip install -r requirements.txt`
   - **Install Command**: `pip install -r requirements.txt`
6. Add Environment Variables:
   - `PRIVATE_KEY` (optional)
7. Click "Deploy"

### Vercel Configuration
The `vercel.json` file is already configured for deployment.

## Step 7: Share Your Project

### Create a Great README
Your README.md already includes:
- ✨ Features list
- 🚀 Quick start guide
- 📁 Project structure
- 🛠️ Tech stack
- 🌐 API endpoints
- 💎 Token system info
- 📖 Usage examples
- 🧪 Testing instructions
- 🐳 Docker deployment
- ⚙️ Configuration guide

### Add Screenshots
1. Take screenshots of your app
2. Add them to the README:
   ```markdown
   ## Screenshots
   
   ![Dashboard](screenshots/dashboard.png)
   ![Chat](screenshots/chat.png)
   ```

### Share on Social Media
```
🚀 Just launched OpenGradient Model Hub Assistant!

Features:
- AI-powered model search
- Voice input
- Vision AI
- Free tokens every 5h
- Beautiful UI

Check it out: https://github.com/YOUR_USERNAME/og-model-assistant

#OpenGradient #AI #FastAPI #Python #LLM
```

## Step 8: Maintain Your Project

### Regular Updates
```bash
# Make changes
# ...

# Commit changes
git add .
git commit -m "Add new feature: [feature name]"

# Push to GitHub
git push origin main
```

### Handle Issues
- Respond to issues promptly
- Label issues appropriately
- Create milestones for features

### Accept Contributions
- Review pull requests
- Provide constructive feedback
- Merge good contributions

## Common Git Commands

```bash
# Check status
git status

# View history
git log --oneline

# Create branch
git checkout -b feature/new-feature

# Switch branch
git checkout main

# Merge branch
git merge feature/new-feature

# Pull latest changes
git pull origin main

# Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin --tags
```

## Best Practices

1. **Commit Often**
   - Small, focused commits
   - Clear commit messages

2. **Use Branches**
   - Feature branches for new features
   - Bugfix branches for fixes

3. **Write Good Commit Messages**
   ```
   Short summary (50 chars)
   
   Longer description if needed.
   Explain what and why, not how.
   ```

4. **Keep README Updated**
   - Add new features
   - Update installation instructions
   - Add screenshots

5. **Tag Releases**
   - Use semantic versioning (v1.0.0)
   - Write release notes
   - Tag important versions

## Troubleshooting

### Authentication Issues
```bash
# Use GitHub token instead of password
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/og-model-assistant.git
```

### Large Files
```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.png"
git lfs track "*.jpg"
```

### Undo Last Commit
```bash
# Keep changes
git reset --soft HEAD~1

# Discard changes
git reset --hard HEAD~1
```

## Resources

- [GitHub Docs](https://docs.github.com/)
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [Best Practices](https://github.com/git-tips/tips)

---

**Good luck with your project! 🚀**

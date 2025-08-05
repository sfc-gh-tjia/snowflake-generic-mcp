# Publishing Snowflake MCP Server to GitHub

This guide provides clear step-by-step instructions for publishing your Snowflake MCP Server to GitHub as a public repository.

## Prerequisites

- GitHub account
- Git installed on your system
- Command line access

## Step 1: Create GitHub Repository

1. **Go to GitHub**: Open [github.com](https://github.com) and sign in
2. **Create new repository**:
   - Click the **"+"** icon → **"New repository"**
   - **Repository name**: `snowflake-mcp-server`
   - **Description**: `A secure MCP server for executing SQL queries against Snowflake`
   - **Visibility**: Select **"Public"** ✅
   - **Don't initialize** with README, .gitignore, or license (we have these already)
   - Click **"Create repository"**
3. **Copy the repository URL** shown (you'll need this later):
   ```
   https://github.com/YOUR_USERNAME/snowflake-mcp-server.git
   ```

## Step 2: Initialize Local Git Repository

Open terminal in your project directory and run:

```bash
# Initialize git repository
git init

# Configure git (replace with your details)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 3: Add and Commit Files

```bash
# Add all files to staging
git add .

# Check what will be committed
git status

# Make initial commit
git commit -m "Initial release: Snowflake MCP Server v1.0.0

- Secure MCP server for Snowflake SQL queries
- Multiple authentication methods (password/private key/SSO)
- Environment-based configuration with security best practices
- Complete Claude Desktop and Cursor integration
- Comprehensive documentation and examples"
```

## Step 4: Connect to GitHub and Push

```bash
# Add GitHub repository as remote (replace YOUR_USERNAME with your actual username)
git remote add origin https://github.com/YOUR_USERNAME/snowflake-mcp-server.git

# Create main branch and push
git branch -M main
git push -u origin main
```

## Step 5: Verify and Configure

### ✅ Verify Your Repository

1. Go to `https://github.com/YOUR_USERNAME/snowflake-mcp-server`
2. Check that:
   - Repository is marked as **"Public"**
   - README.md displays properly on the main page
   - All files are visible (not starting with `.env`)

### 🏷️ Add Topics (Recommended)

1. On your repository page, click ⚙️ **"Settings"**
2. Scroll to **"Topics"** and add:
   ```
   snowflake, mcp, model-context-protocol, ai, sql, claude, python, database
   ```

### 🎯 Create Release (Optional)

1. Click **"Releases"** → **"Create a new release"**
2. **Tag version**: `v1.0.0`
3. **Release title**: `Snowflake MCP Server v1.0.0`
4. **Description**: Brief description of features
5. Click **"Publish release"**

## Security Verification

✅ **Check these items before sharing**:
- [ ] No actual credentials in any committed files
- [ ] `.env.example` has placeholder values only
- [ ] `.gitignore` is working (no `.env` or private keys visible)
- [ ] README.md displays security warnings properly

## Troubleshooting

**Authentication required when pushing?**
- Use GitHub Personal Access Token instead of password
- Go to GitHub Settings → Developer settings → Personal access tokens → Generate new token
- Use token as password when prompted

**Repository not public?**
- Go to repository Settings → scroll to "Danger Zone" → Change visibility to Public

## 🎉 Success!

Your repository is now live at:
```
https://github.com/YOUR_USERNAME/snowflake-mcp-server
```

**What's next?**
- Share with the MCP and Snowflake communities
- Star your own repository ⭐
- Consider writing a blog post about your MCP server

## Future Updates

When you make changes:
```bash
git add .
git commit -m "Description of changes"
git push origin main
```

For major updates, create new releases with updated version numbers. 
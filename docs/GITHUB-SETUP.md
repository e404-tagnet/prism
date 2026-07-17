# GitHub Setup for PRISM

## Step 1: Create the Repo (You do this)

1. Go to [github.com/new](https://github.com/new)
2. **Repository name:** `prism` (lowercase, clean)
3. **Description:** `Shadow Bayesian scaffold for local LLM conversations — classifies, routes, learns.`
4. **Public or private:** Your call
5. **DO NOT** tick "Add a README file" (we already have one)
6. **DO NOT** tick "Add .gitignore" (we have one)
7. **DO NOT** tick "Choose a license" (pick one later if you want)
8. Click **Create repository**

## Step 2: Push Our Local Structure

Copy these commands exactly (run from the PRISM folder):

```bash
cd /path/to/prism
git init
git add .
git commit -m "init: architecture docs, config, and folder structure"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/prism.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 3: Branching Rule (ADHD-friendly)

- `main` = always clean, always reviewed
- `dev` = your play branch. Try stuff, break stuff
- `feature/whatever` = if you want to experiment on your own

## Step 4: Access Token (if it asks for a password)

GitHub killed password auth. If it asks, use a **Personal Access Token**:
- GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
- Generate new token → **Scopes: repo** (full control)
- Copy the token and paste it instead of your password when pushing

Done.

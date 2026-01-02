#!/bin/bash
# Git helper for the Apple Music analyzer scripts repo
# This repo is separate from apple-music-watch-viewer which has its own git repo

set -e

echo "📦 Apple Music Analyzer - Git Helper"
echo "====================================="
echo ""
echo "This repo contains:"
echo "  • Python analysis scripts"
echo "  • Data import tools"
echo "  • Documentation"
echo ""
echo "Note: apple-music-watch-viewer/ has its own separate git repo"
echo ""

# Check git status
echo "Current status:"
git status --short

echo ""
echo "Files to commit:"
git status --porcelain | grep -E '^\?\?|^ M|^M |^A ' || echo "  (none)"

echo ""
read -p "Continue with commit? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 0
fi

# Add files (respecting .gitignore)
echo ""
echo "Adding files..."
git add .

echo ""
read -p "Enter commit message: " commit_msg

if [ -z "$commit_msg" ]; then
    echo "❌ Commit message cannot be empty"
    exit 1
fi

# Commit
git commit -m "$commit_msg"

echo ""
echo "✅ Committed!"
echo ""

# Check if remote exists
if git remote get-url origin &>/dev/null; then
    echo "Remote 'origin' is configured:"
    git remote get-url origin
    echo ""
    read -p "Push to remote? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Get current branch
        branch=$(git rev-parse --abbrev-ref HEAD)

        # Push
        echo "Pushing to origin/$branch..."
        git push -u origin "$branch"

        echo ""
        echo "✅ Pushed to remote!"
    else
        echo "Skipped push. You can push later with:"
        echo "  git push -u origin $(git rev-parse --abbrev-ref HEAD)"
    fi
else
    echo "⚠️  No remote repository configured yet."
    echo ""
    echo "To add a remote repository:"
    echo "  1. Create a new repo on GitHub"
    echo "  2. Run: git remote add origin <your-repo-url>"
    echo "  3. Run: git push -u origin main"
    echo ""
    echo "Example:"
    echo "  git remote add origin git@github.com:yourusername/apple-music-analyzer.git"
    echo "  git push -u origin main"
fi

echo ""

#!/bin/bash

# Update Script - Run this when you need to update code on server
# Usage: ./update.sh [optional-commit-message]

set -e

echo "📤 Updating Server Deployment"
echo "=============================="

# Stage all changes
git add .

# Commit with message
if [ -n "$1" ]; then
    COMMIT_MSG="$1"
else
    COMMIT_MSG="Update $(date +'%Y-%m-%d %H:%M')"
fi

echo "💾 Committing changes: $COMMIT_MSG"
git commit -m "$COMMIT_MSG" || echo "No changes to commit"

# Push to GitHub
echo "⬆️  Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "📋 Now on your server, run:"
echo "   ssh root@210.79.129.61"
echo "   cd /opt/speak-sync"
echo "   git pull"
echo "   ./deploy.sh"
echo ""
echo "Or use the one-liner:"
echo "   ssh root@210.79.129.61 'cd /opt/speak-sync && git pull && ./deploy.sh'"

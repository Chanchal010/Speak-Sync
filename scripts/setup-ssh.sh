#!/bin/bash

# SSH Setup Guide for ExCloud Server
# Run this to setup SSH key authentication

echo "🔑 Setting up SSH Key Authentication"
echo "====================================="

# Step 1: Generate SSH key if it doesn't exist
if [ ! -f ~/.ssh/id_ed25519 ]; then
    echo ""
    echo "📝 Generating SSH key..."
    ssh-keygen -t ed25519 -C "$(whoami)@$(hostname)" -f ~/.ssh/id_ed25519 -N ""
    echo "✅ SSH key generated!"
else
    echo "✅ SSH key already exists"
fi

# Step 2: Display the public key
echo ""
echo "📋 Your SSH Public Key:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat ~/.ssh/id_ed25519.pub
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "🚀 Next Steps:"
echo ""
echo "Option 1: Add via ExCloud Console (Easiest)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Go to: https://console.excloud.in/console"
echo "2. Select your server (210.79.129.61)"
echo "3. Go to 'SSH Keys' or 'Access' section"
echo "4. Add the public key shown above"
echo "5. Wait 1-2 minutes for the key to sync"
echo ""
echo "Option 2: Add via Password (if you have root password)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Run this command (enter password when prompted):"
echo ""
echo "  ssh-copy-id root@210.79.129.61"
echo ""
echo "Option 3: Manual Copy (if console access available)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Copy the public key above"
echo "2. Login to ExCloud console terminal"
echo "3. Run these commands on the server:"
echo ""
echo "   mkdir -p ~/.ssh"
echo "   echo 'PASTE_YOUR_PUBLIC_KEY_HERE' >> ~/.ssh/authorized_keys"
echo "   chmod 700 ~/.ssh"
echo "   chmod 600 ~/.ssh/authorized_keys"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "After adding the key, test with:"
echo "  ssh root@210.79.129.61 'echo \"SSH connection successful!\"'"

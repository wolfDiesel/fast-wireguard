#!/bin/bash

# FastWG Update Script
# Обновляет FastWG после git pull

set -e

echo "🔄 FastWG Update Script"
echo "========================"

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -f "fastwg.py" ]; then
    echo "❌ Error: Please run this script from the FastWG project directory"
    exit 1
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root (use sudo)"
    exit 1
fi

echo "📦 Uninstalling current version..."
pip uninstall fastwg -y || true

echo "🔧 Installing updated version..."
pip install -e . --force-reinstall

echo "✅ FastWG updated successfully!"
echo ""
echo "📋 Version info:"
fastwg --version

echo ""
echo "🎯 You can now use the new features:"
echo "   fastwg list --all    # Show all clients including inactive"
echo "   fastwg list          # Show only active clients"

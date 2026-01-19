#!/bin/bash

# Internship Tracker - Quick Setup Script
# Run this once after cloning: ./setup.sh

echo "🚀 Setting up Internship Tracker..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate it
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✨ Setup complete!"
echo ""
echo "To run the app:"
echo "  source venv/bin/activate"
echo "  python3 app.py"
echo ""
echo "Then open: http://127.0.0.1:1453"

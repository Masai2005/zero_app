#!/bin/bash
# Activation script for the ZERO Business Management System virtual environment

echo "🚀 Activating ZERO Business Management System virtual environment..."
source venv/bin/activate

echo "✅ Virtual environment activated!"
echo "📦 Python version: $(python --version)"
echo "📦 PySide6 version: $(python -c 'import PySide6; print(PySide6.__version__)')"
echo ""
echo "💡 To deactivate, run: deactivate"
echo "💡 To run the app, use: python main.py (when main.py is created)"
echo ""
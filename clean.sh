# Remove all __pycache__ directories
find . -type d -name "__pycache__" -exec rm -r {} +

# Remove all .egg-info directories
find . -type d -name "*.egg-info" -exec rm -r {} +

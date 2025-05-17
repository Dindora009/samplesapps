#!/bin/bash
# This script generates icon files from a source image using ImageMagick
# Place your source image (at least 128x128 pixels) in this directory as "source.png"

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null
then
    echo "ImageMagick is required but not installed. Please install it first."
    exit 1
fi

# Check if source image exists
if [ ! -f "source.png" ]
then
    echo "Source image 'source.png' not found in the current directory."
    exit 1
fi

# Generate icons in different sizes
convert source.png -resize 16x16 ../icon16.png
convert source.png -resize 48x48 ../icon48.png
convert source.png -resize 128x128 ../icon128.png

echo "Icons generated successfully!"

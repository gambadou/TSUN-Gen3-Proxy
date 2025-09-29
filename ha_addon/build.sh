#!/bin/bash
set -e

# Build script for Home Assistant Add-on
echo "Building TSUN Gen3 Proxy Add-on..."

# Copy application files to the correct location
mkdir -p rootfs/app
cp -r app/* rootfs/app/
cp generate_config.py rootfs/app/

echo "Build complete!"
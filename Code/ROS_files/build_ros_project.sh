#!/bin/bash

# ROS2 Project Build Script
# Usage: ./build_ros_project.sh [clean] [package_name]

set -e  # Exit on any error

# Configuration
ROS_ENV_PATH="/opt/anaconda3/envs/ThesisRos"
PYTHON_EXEC="${ROS_ENV_PATH}/bin/python"
PYTHON_LIB="${ROS_ENV_PATH}/lib/libpython3.11.dylib"
PYTHON_INCLUDE="${ROS_ENV_PATH}/include/python3.11"
NUMPY_INCLUDE="${ROS_ENV_PATH}/lib/python3.11/site-packages/numpy/core/include"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 ROS2 Project Build Script${NC}"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "package.xml" ] && [ ! -d "src" ]; then
    echo -e "${RED}❌ Error: Run this script from your ROS2 workspace root${NC}"
    exit 1
fi

# Parse arguments
CLEAN_BUILD=false
PACKAGE_NAME=""
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        clean)
            CLEAN_BUILD=true
            shift
            ;;
        --package)
            PACKAGE_NAME="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [clean] [--package PACKAGE_NAME] [--verbose]"
            echo "  clean: Clean build and install directories"
            echo "  --package: Build only specific package"
            echo "  --verbose: Enable verbose output"
            exit 0
            ;;
        *)
            PACKAGE_NAME="$1"
            shift
            ;;
    esac
done

# Clean build if requested
if [ "$CLEAN_BUILD" = true ]; then
    echo -e "${YELLOW}🧹 Cleaning build and install directories...${NC}"
    rm -rf build/ install/ log/
fi

# Set Python environment variables
echo -e "${YELLOW}🐍 Setting up Python environment...${NC}"
export Python3_EXECUTABLE="$PYTHON_EXEC"
export Python3_LIBRARY="$PYTHON_LIB"
export Python3_INCLUDE_DIR="$PYTHON_INCLUDE"
export Python3_NumPy_INCLUDE_DIRS="$NUMPY_INCLUDE"
export PYTHON_EXECUTABLE="$PYTHON_EXEC"

# Build command
BUILD_CMD="colcon build --cmake-force-configure"

if [ -n "$PACKAGE_NAME" ]; then
    BUILD_CMD="$BUILD_CMD --packages-select $PACKAGE_NAME"
    echo -e "${YELLOW}📦 Building package: $PACKAGE_NAME${NC}"
else
    echo -e "${YELLOW}📦 Building all packages...${NC}"
fi

if [ "$VERBOSE" = true ]; then
    BUILD_CMD="$BUILD_CMD --verbose"
fi

# Add CMake arguments
BUILD_CMD="$BUILD_CMD --cmake-args"
BUILD_CMD="$BUILD_CMD -DPython3_EXECUTABLE=$PYTHON_EXEC"
BUILD_CMD="$BUILD_CMD -DPython3_LIBRARY=$PYTHON_LIB"
BUILD_CMD="$BUILD_CMD -DPython3_INCLUDE_DIR=$PYTHON_INCLUDE"
BUILD_CMD="$BUILD_CMD -DPython3_NumPy_INCLUDE_DIRS=$NUMPY_INCLUDE"
BUILD_CMD="$BUILD_CMD -DPYTHON_EXECUTABLE=$PYTHON_EXEC"

# Execute build
echo -e "${YELLOW}🔨 Building...${NC}"
eval $BUILD_CMD

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build successful!${NC}"
    
    # Setup library links
    echo -e "${YELLOW}🔗 Setting up library links...${NC}"
    
    # Create symlinks for all dylib files in install/*/lib/
    for pkg_dir in install/*/lib/; do
        if [ -d "$pkg_dir" ]; then
            for lib_file in "$pkg_dir"*.dylib; do
                if [ -f "$lib_file" ]; then
                    ln -sf "$(pwd)/$lib_file" "$ROS_ENV_PATH/lib/" 2>/dev/null || true
                fi
            done
        fi
    done
    
    # Source the setup
    echo -e "${YELLOW}📋 Sourcing setup...${NC}"
    source install/setup.bash
    
    echo -e "${GREEN}🎉 Ready to run! Use: ros2 run <package> <executable>${NC}"
    
else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

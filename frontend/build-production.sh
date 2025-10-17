#!/bin/bash

# 🚀 Script Build Frontend IndoWater untuk Production
# Usage: ./build-production.sh

echo "======================================"
echo "🚀 IndoWater Frontend Build Script"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please create .env file with:"
    echo "REACT_APP_BACKEND_URL=https://your-backend-url.onrender.com"
    exit 1
fi

# Show current backend URL
echo -e "${YELLOW}📝 Current Backend URL:${NC}"
grep REACT_APP_BACKEND_URL .env
echo ""

# Ask for confirmation
read -p "Is this the correct backend URL? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Build cancelled. Please update .env file first.${NC}"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    yarn install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Dependency installation failed!${NC}"
        exit 1
    fi
fi

# Clean previous build
if [ -d "build" ]; then
    echo -e "${YELLOW}🧹 Cleaning previous build...${NC}"
    rm -rf build
fi

# Build for production
echo -e "${YELLOW}🔨 Building production bundle...${NC}"
echo ""
yarn build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Build completed successfully!${NC}"
    echo ""
    echo "======================================"
    echo "📦 Build Output Location:"
    echo "======================================"
    echo "Folder: ./build/"
    echo ""
    ls -lh build/
    echo ""
    
    # Calculate build size
    BUILD_SIZE=$(du -sh build | cut -f1)
    echo -e "${GREEN}📊 Total Build Size: ${BUILD_SIZE}${NC}"
    echo ""
    
    echo "======================================"
    echo "📤 Next Steps:"
    echo "======================================"
    echo "1. Upload all files from 'build/' folder to your server"
    echo "2. Extract to web root directory (public_html/ or /var/www/html/)"
    echo "3. Configure Nginx/Apache for SPA routing"
    echo "4. Install SSL certificate"
    echo "5. Test your application!"
    echo ""
    echo "Upload via FTP/SFTP:"
    echo "  scp -r build/* user@your-server.com:/var/www/html/"
    echo ""
    echo "Or create zip file:"
    echo "  cd build && zip -r ../indowater-frontend.zip . && cd .."
    echo ""
    echo -e "${GREEN}🎉 Ready for deployment!${NC}"
    
    # Ask if user wants to create zip
    echo ""
    read -p "Create ZIP file for upload? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}📦 Creating ZIP file...${NC}"
        cd build
        zip -r ../indowater-frontend.zip .
        cd ..
        echo -e "${GREEN}✅ ZIP file created: indowater-frontend.zip${NC}"
        ZIP_SIZE=$(du -sh indowater-frontend.zip | cut -f1)
        echo -e "${GREEN}📊 ZIP Size: ${ZIP_SIZE}${NC}"
    fi
else
    echo ""
    echo -e "${RED}❌ Build failed! Please check the errors above.${NC}"
    exit 1
fi

echo ""
echo "======================================"
echo "📚 Documentation:"
echo "======================================"
echo "See DEPLOYMENT_RENDER_GUIDE.md for detailed instructions"
echo ""

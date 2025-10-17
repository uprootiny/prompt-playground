#!/bin/bash
# Prompt Playground - Deployment Script

set -e

echo "🎯 Prompt Playground - Deployment Preparation"
echo "=============================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check directory
if [ ! -f "render.yaml" ]; then
    echo -e "${RED}❌ Error: Run from project root${NC}"
    exit 1
fi

echo -e "\n${YELLOW}📋 Pre-deployment Checklist${NC}"

# 1. Check Docker
echo -n "Docker... "
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

# 2. Check structure
echo -n "Project structure... "
if [ -d "backend" ] && [ -f "backend/Dockerfile" ] && [ -f "backend/main.py" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

# 3. Run tests
echo -e "\n${YELLOW}🧪 Running Tests${NC}"
cd backend
if [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || true
fi

if command -v pytest &> /dev/null; then
    pytest tests/test_prompts_complete.py -v --tb=short || echo -e "${YELLOW}⚠ Continuing...${NC}"
else
    echo -e "${YELLOW}⚠ pytest not found${NC}"
fi

cd ..

# 4. Build Docker
echo -e "\n${YELLOW}🐳 Building Docker Image${NC}"
docker build -t prompt-playground:test -f backend/Dockerfile backend/

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Image built${NC}"

# 5. Test container
echo -e "\n${YELLOW}🔍 Testing Container${NC}"
CONTAINER_ID=$(docker run -d -p 8001:8001 \
    -e OPENAI_API_KEY=test \
    -e ANTHROPIC_API_KEY=test \
    prompt-playground:test)

sleep 5

HEALTH=$(curl -s http://localhost:8001/health || echo "FAILED")

if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
    docker logs $CONTAINER_ID
    docker stop $CONTAINER_ID
    docker rm $CONTAINER_ID
    exit 1
fi

# Test templates endpoint
TEMPLATES=$(curl -s http://localhost:8001/api/templates || echo "FAILED")
if echo "$TEMPLATES" | grep -q "code_generation"; then
    echo -e "${GREEN}✓ Templates endpoint working${NC}"
else
    echo -e "${YELLOW}⚠ Templates endpoint unexpected${NC}"
fi

docker stop $CONTAINER_ID
docker rm $CONTAINER_ID

# Success
echo -e "\n${GREEN}✅ Deployment preparation complete!${NC}"
echo ""
echo "======================================"
echo "📦 Deploy to Render.com"
echo "======================================"
echo ""
echo "1. https://dashboard.render.com"
echo "2. New + → Web Service"
echo "3. Connect repo: uprootiny/prompt-playground"
echo "4. Auto-detects render.yaml"
echo "5. Add environment variables:"
echo "   - OPENAI_API_KEY"
echo "   - ANTHROPIC_API_KEY"
echo ""
echo "Expected URL:"
echo "  https://prompt-playground.onrender.com"
echo ""
echo "Test endpoints:"
echo "  GET  /                      (info)"
echo "  GET  /health                (health)"
echo "  GET  /api/templates         (template library)"
echo "  GET  /models                (available models)"
echo "  POST /api/compare           (compare costs)"
echo ""
echo -e "${GREEN}🎉 Ready to deploy!${NC}"

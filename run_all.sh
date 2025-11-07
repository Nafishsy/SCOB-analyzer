#!/bin/bash

# SCOB Legal RAG System - Complete Startup Script
# This script starts all components: Weaviate, Backend API, and Frontend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}SCOB Legal RAG System Startup${NC}"
echo -e "${BLUE}======================================${NC}\n"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo "Creating .env file..."
    cat > .env << 'EOF'
OPENAI_API_KEY=your-openai-api-key-here
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=
EOF
    echo -e "${YELLOW}Please edit .env and add your OpenAI API key${NC}\n"
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    jobs -p | xargs kill 2>/dev/null || true
    exit 0
}

trap cleanup EXIT INT TERM

# 1. Start Weaviate
echo -e "${BLUE}1. Starting Weaviate (Vector Database)...${NC}"
if check_port 8080; then
    echo -e "${YELLOW}   ⚠️  Port 8080 is already in use${NC}"
    echo "   Weaviate might already be running"
else
    echo -e "${GREEN}   ✓ Starting Weaviate container...${NC}"
    docker-compose up -d
fi

# Wait for Weaviate to be ready
echo -e "${YELLOW}   Waiting for Weaviate to be ready...${NC}"
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8080/v1/meta > /dev/null 2>&1; then
        echo -e "${GREEN}   ✓ Weaviate is ready${NC}\n"
        break
    fi
    sleep 1
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}   ✗ Weaviate failed to start${NC}"
    exit 1
fi

# 2. Start Backend API
echo -e "${BLUE}2. Starting Backend API Server...${NC}"
if check_port 8000; then
    echo -e "${RED}   ✗ Port 8000 is already in use${NC}"
    echo "   Kill the process and try again:"
    echo "   lsof -i :8000 | grep LISTEN | awk '{print \$2}' | xargs kill -9"
    exit 1
fi

echo -e "${GREEN}   ✓ Starting API on port 8000...${NC}"
python backend_api.py > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for API to be ready
echo -e "${YELLOW}   Waiting for API to be ready...${NC}"
max_attempts=15
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}   ✓ API is ready${NC}\n"
        break
    fi
    sleep 1
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}   ✗ API failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# 3. Start Frontend
echo -e "${BLUE}3. Starting React Frontend...${NC}"
if check_port 3000; then
    echo -e "${YELLOW}   ⚠️  Port 3000 is already in use${NC}"
    echo "   The frontend server might already be running"
else
    echo -e "${GREEN}   ✓ Starting frontend on port 3000...${NC}"
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
fi

# Summary
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}✓ SCOB Legal RAG System Started${NC}"
echo -e "${GREEN}======================================${NC}\n"

echo -e "${BLUE}Access the application at:${NC}"
echo -e "  ${YELLOW}Frontend:  http://localhost:3000${NC}"
echo -e "  ${YELLOW}API Docs:  http://localhost:8000/docs${NC}"
echo -e "  ${YELLOW}Weaviate:  http://localhost:8080${NC}\n"

echo -e "${BLUE}Components:${NC}"
echo -e "  ${GREEN}✓${NC} Weaviate (Vector Database)"
echo -e "  ${GREEN}✓${NC} Backend API Server"
echo -e "  ${GREEN}✓${NC} React Frontend\n"

echo -e "${BLUE}Tips:${NC}"
echo -e "  • Open http://localhost:3000 in your browser"
echo -e "  • Upload PDFs from the Upload page"
echo -e "  • Search legal questions from the Search page"
echo -e "  • View uploaded documents on the Documents page\n"

echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Keep the script running
wait

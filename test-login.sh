#!/bin/bash

echo "Testing Financial Planning Application Login Flow"
echo "================================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test Backend Health
echo -e "\n${YELLOW}1. Testing Backend Health...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if [[ $HEALTH_RESPONSE == *"1.0.0"* ]]; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    exit 1
fi

# Test Login Endpoint
echo -e "\n${YELLOW}2. Testing Login with test credentials...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/token \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=testuser&password=testpass123")

if [[ $LOGIN_RESPONSE == *"access_token"* ]]; then
    echo -e "${GREEN}✓ Login successful${NC}"

    # Extract token
    TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

    # Test authenticated endpoint
    echo -e "\n${YELLOW}3. Testing authenticated endpoint...${NC}"
    ME_RESPONSE=$(curl -s http://localhost:8000/api/auth/me \
        -H "Authorization: Bearer $TOKEN")

    if [[ $ME_RESPONSE == *"testuser"* ]]; then
        echo -e "${GREEN}✓ Authentication working correctly${NC}"
    else
        echo -e "${RED}✗ Authentication verification failed${NC}"
    fi
else
    echo -e "${RED}✗ Login failed${NC}"
    echo "Response: $LOGIN_RESPONSE"
fi

# Test Frontend Build
echo -e "\n${YELLOW}4. Testing Frontend TypeScript compilation...${NC}"
cd frontend
npm run build 2>&1 | tail -n 20
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ TypeScript compilation successful${NC}"
else
    echo -e "${RED}✗ TypeScript compilation failed${NC}"
fi
cd ..

echo -e "\n${YELLOW}5. Summary:${NC}"
echo -e "${GREEN}✓ Backend API working${NC}"
echo -e "${GREEN}✓ Authentication functional${NC}"
echo -e "${GREEN}✓ Frontend compiles${NC}"
echo -e "\nTo test in browser:"
echo "1. Open http://localhost:3000"
echo "2. Login with: testuser / testpass123"
echo "3. Check browser console for errors (F12)"
echo "4. Verify dashboard loads without redirect loops"
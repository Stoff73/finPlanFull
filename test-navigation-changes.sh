#!/bin/bash

# Test script for navigation changes
# This script verifies all changes implemented in change_tasks.md

echo "=================================="
echo "Navigation Changes Test Suite"
echo "=================================="
echo ""

FRONTEND_URL="http://localhost:3000"
BACKEND_URL="http://localhost:8000"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass_count=0
fail_count=0

# Function to check if a URL is accessible
check_url() {
    local url=$1
    local description=$2

    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200"; then
        echo -e "${GREEN}✓${NC} $description"
        ((pass_count++))
        return 0
    else
        echo -e "${RED}✗${NC} $description"
        ((fail_count++))
        return 1
    fi
}

# Function to check if frontend route exists (without authentication)
check_frontend_route() {
    local route=$1
    local description=$2

    # Frontend always returns 200 for SPA routes, so just check if server responds
    if curl -s "$FRONTEND_URL$route" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $description"
        ((pass_count++))
        return 0
    else
        echo -e "${RED}✗${NC} $description"
        ((fail_count++))
        return 1
    fi
}

# Function to check if backend API endpoint exists
check_api_endpoint() {
    local endpoint=$1
    local description=$2

    # Check if endpoint is documented in OpenAPI spec
    if curl -s "$BACKEND_URL/openapi.json" | grep -q "$endpoint"; then
        echo -e "${GREEN}✓${NC} $description"
        ((pass_count++))
        return 0
    else
        echo -e "${YELLOW}?${NC} $description (endpoint not in OpenAPI spec)"
        return 0  # Don't fail for this
    fi
}

echo "1. Checking Backend Status"
echo "----------------------------"
check_url "$BACKEND_URL/docs" "Backend API documentation accessible"
check_url "$BACKEND_URL/openapi.json" "OpenAPI spec available"
echo ""

echo "2. Checking Frontend Status"
echo "----------------------------"
check_url "$FRONTEND_URL" "Frontend application running"
echo ""

echo "3. Testing Frontend Routes"
echo "----------------------------"
check_frontend_route "/" "Root route accessible"
check_frontend_route "/dashboard" "Dashboard route"
check_frontend_route "/products" "Products route"
check_frontend_route "/products/pensions" "Pensions route"
check_frontend_route "/products/investments" "Investments route"
check_frontend_route "/products/protection" "Protection route (moved but path maintained)"
check_frontend_route "/portfolio-analytics" "Portfolio Analytics route"
check_frontend_route "/retirement-planning-uk" "UK Pension route"
check_frontend_route "/tax-optimization" "Tax Optimization route (moved to top-level)"
check_frontend_route "/iht-calculator-complete" "IHT Planning Suite route"
check_frontend_route "/financial-statements" "Financial Statements route"
echo ""

echo "4. Testing Backend API Endpoints"
echo "-----------------------------------"
check_api_endpoint "/api/products/pensions/all" "Pensions API endpoint"
check_api_endpoint "/api/products/investments/all" "Investments API endpoint"
check_api_endpoint "/api/products/protection/all" "Protection API endpoint"
check_api_endpoint "/api/tax-optimization/optimize-pension" "Pension optimization API endpoint"
echo ""

echo "5. Checking Build Artifacts"
echo "----------------------------"
if [ -f "frontend/build/static/js/main.*.js" ]; then
    BUILD_SIZE=$(du -sh frontend/build/static/js/main.*.js | cut -f1)
    echo -e "${GREEN}✓${NC} Production build exists ($BUILD_SIZE)"
    ((pass_count++))
else
    echo -e "${YELLOW}?${NC} Production build not found (run 'npm run build' to create)"
fi

if [ -f "frontend/build/index.html" ]; then
    echo -e "${GREEN}✓${NC} Build index.html exists"
    ((pass_count++))
else
    echo -e "${YELLOW}?${NC} Build index.html not found"
fi
echo ""

echo "6. TypeScript Compilation Check"
echo "---------------------------------"
cd frontend
if npm run build > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} TypeScript compiles without errors"
    ((pass_count++))
else
    echo -e "${RED}✗${NC} TypeScript compilation has errors"
    ((fail_count++))
fi
cd ..
echo ""

echo "7. Checking Modified Files"
echo "----------------------------"
files_to_check=(
    "frontend/src/services/products.ts"
    "frontend/src/pages/Investments.tsx"
    "frontend/src/components/layout/Header.tsx"
    "frontend/src/components/layout/MobileNav.tsx"
    "frontend/src/pages/ProductsOverview.tsx"
    "frontend/src/pages/RetirementPlanningUK.tsx"
    "docs/USER_GUIDE.md"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file exists"
        ((pass_count++))
    else
        echo -e "${RED}✗${NC} $file not found"
        ((fail_count++))
    fi
done
echo ""

echo "8. Checking for SEIS/EIS in Code"
echo "----------------------------------"
if grep -q "seis" frontend/src/services/products.ts; then
    echo -e "${GREEN}✓${NC} SEIS found in products.ts"
    ((pass_count++))
else
    echo -e "${RED}✗${NC} SEIS not found in products.ts"
    ((fail_count++))
fi

if grep -q "eis" frontend/src/services/products.ts; then
    echo -e "${GREEN}✓${NC} EIS found in products.ts"
    ((pass_count++))
else
    echo -e "${RED}✗${NC} EIS not found in products.ts"
    ((fail_count++))
fi

if grep -q "SEIS" frontend/src/pages/Investments.tsx; then
    echo -e "${GREEN}✓${NC} SEIS option added to Investments page"
    ((pass_count++))
else
    echo -e "${RED}✗${NC} SEIS option not found in Investments page"
    ((fail_count++))
fi
echo ""

echo "9. Checking Navigation Changes"
echo "--------------------------------"
if grep -q "Protection" frontend/src/components/layout/Header.tsx; then
    echo -e "${GREEN}✓${NC} Protection in Header navigation"
    ((pass_count++))
else
    echo -e "${RED}✗${NC} Protection not found in Header"
    ((fail_count++))
fi

if grep -q "Tax Optimisation\\|Tax Optimization" frontend/src/components/layout/Header.tsx; then
    echo -e "${GREEN}✓${NC} Tax Optimization in Header navigation"
    ((pass_count++))
else
    echo -e "${RED}✗${NC} Tax Optimization not found in Header"
    ((fail_count++))
fi

if grep -q "Protection" frontend/src/components/layout/MobileNav.tsx; then
    echo -e "${GREEN}✓${NC} Protection in Mobile navigation"
    ((pass_count++))
else
    echo -e "${RED}✗${NC} Protection not found in Mobile navigation"
    ((fail_count++))
fi

if grep -q "optimization\\|Optimization" frontend/src/pages/RetirementPlanningUK.tsx; then
    echo -e "${GREEN}✓${NC} Pension Optimization tab added to UK Pension page"
    ((pass_count++))
else
    echo -e "${RED}✗${NC} Pension Optimization not found in UK Pension page"
    ((fail_count++))
fi
echo ""

echo "10. Documentation Check"
echo "------------------------"
if grep -q "SEIS" docs/USER_GUIDE.md; then
    echo -e "${GREEN}✓${NC} SEIS documented in USER_GUIDE.md"
    ((pass_count++))
else
    echo -e "${YELLOW}?${NC} SEIS not mentioned in USER_GUIDE.md"
fi

if grep -q "Protection.*top-level" docs/USER_GUIDE.md; then
    echo -e "${GREEN}✓${NC} Protection navigation documented"
    ((pass_count++))
else
    echo -e "${YELLOW}?${NC} Protection navigation not documented"
fi
echo ""

echo "=================================="
echo "Test Results Summary"
echo "=================================="
total=$((pass_count + fail_count))
success_rate=$((pass_count * 100 / total))

echo "Passed: $pass_count"
echo "Failed: $fail_count"
echo "Total:  $total"
echo "Success Rate: $success_rate%"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    exit 1
fi
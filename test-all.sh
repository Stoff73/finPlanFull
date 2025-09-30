#!/bin/bash
echo "========================================="
echo "FULL APPLICATION TEST SUITE"
echo "========================================="

# Make test scripts executable
chmod +x frontend/test.sh backend/test.sh

# Test Frontend
echo ""
echo "Testing Frontend..."
echo "-----------------------------------------"
cd frontend
./test.sh
FRONTEND_RESULT=$?
cd ..

# Test Backend
echo ""
echo "Testing Backend..."
echo "-----------------------------------------"
cd backend
./test.sh
BACKEND_RESULT=$?
cd ..

# Summary
echo ""
echo "========================================="
echo "TEST SUMMARY"
echo "========================================="

if [ $FRONTEND_RESULT -eq 0 ] && [ $BACKEND_RESULT -eq 0 ]; then
    echo "✅ ALL TESTS PASSED!"
    echo "The application is ready for deployment."
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    if [ $FRONTEND_RESULT -ne 0 ]; then
        echo "  - Frontend tests failed"
    fi
    if [ $BACKEND_RESULT -ne 0 ]; then
        echo "  - Backend tests failed"
    fi
    echo "Please fix the issues before marking as complete."
    exit 1
fi
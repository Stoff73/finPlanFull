# Comprehensive Testing Framework

## **CRITICAL: NO CODE IS COMPLETE WITHOUT PASSING TESTS**

This testing framework is **MANDATORY** for all development work. No feature, fix, or change should be considered complete without passing all relevant tests.

## Frontend Testing (React + TypeScript)

### 1. Type Checking
```bash
# Must run without errors before ANY commit
npm run typecheck
```

### 2. Linting
```bash
# Must pass all linting rules
npm run lint
```

### 3. Unit Tests
```bash
# All tests must pass
npm test
```

### 4. Build Test
```bash
# Must build successfully
npm run build
```

### 5. Development Server Test
```bash
# Must compile without errors
npm start
# Check browser console for runtime errors
# Verify all routes work correctly
```

## Backend Testing (FastAPI + Python)

### 1. Type Checking
```bash
# Install mypy if not present
pip install mypy

# Run type checking
mypy app/
```

### 2. Linting
```bash
# Install ruff if not present
pip install ruff

# Run linting
ruff check app/
```

### 3. Unit Tests
```bash
# Install pytest if not present
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

### 4. API Testing
```bash
# Test endpoints manually
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Test authentication
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

### 5. Import Test
```bash
# Verify all imports work
python -c "from app.main import app; print('✓ Imports successful')"
```

## Integration Testing

### 1. Full Stack Test
```bash
# Start both services
./start.sh

# Verify both are running
curl http://localhost:8000/health  # Backend
curl http://localhost:3000          # Frontend
```

### 2. Authentication Flow
1. Open http://localhost:3000
2. Navigate to login
3. Enter test credentials
4. Verify redirect to dashboard
5. Check for console errors
6. Test logout functionality

### 3. API Integration
- Test all CRUD operations
- Verify error handling
- Check data persistence
- Test edge cases

## Testing Checklist

Before marking ANY task as complete:

- [ ] **TypeScript compilation**: No errors in frontend
- [ ] **Python imports**: All modules import correctly
- [ ] **Linting**: Both frontend and backend pass linting
- [ ] **Dev servers**: Both start without errors
- [ ] **Browser console**: No runtime errors
- [ ] **API endpoints**: Return expected responses
- [ ] **UI rendering**: All components display correctly
- [ ] **Navigation**: All routes work
- [ ] **Forms**: Submit without errors
- [ ] **Error states**: Properly handled and displayed

## Automated Test Scripts

### Frontend Test Script
Create `frontend/test.sh`:
```bash
#!/bin/bash
echo "Running Frontend Tests..."
npm run typecheck || exit 1
npm run lint || exit 1
npm test -- --watchAll=false || exit 1
npm run build || exit 1
echo "✓ All frontend tests passed"
```

### Backend Test Script
Create `backend/test.sh`:
```bash
#!/bin/bash
echo "Running Backend Tests..."
source venv/bin/activate
python -c "from app.main import app" || exit 1
ruff check app/ || exit 1
pytest -v || exit 1
echo "✓ All backend tests passed"
```

### Full Test Script
Create `test-all.sh`:
```bash
#!/bin/bash
echo "Running Full Test Suite..."
cd frontend && ./test.sh || exit 1
cd ../backend && ./test.sh || exit 1
echo "✓ All tests passed successfully"
```

## Common Issues and Fixes

### TypeScript Errors
- Missing type definitions: Create or update `.d.ts` files
- Theme type errors: Ensure `styled.d.ts` matches theme structure
- Prop type errors: Use correct prop names with transient props ($prefix)

### Python Import Errors
- Check `__init__.py` files exist
- Verify import paths are correct
- Ensure all dependencies in requirements.txt

### API Errors
- Check CORS configuration
- Verify authentication headers
- Ensure database is initialized

## Testing Rules

1. **NO SHORTCUTS**: Always run full test suite
2. **TEST FIRST**: Write tests before implementation when possible
3. **FIX IMMEDIATELY**: Don't commit broken code
4. **DOCUMENT FAILURES**: Record and fix all test failures
5. **VERIFY IN BROWSER**: Always check the actual UI

## Continuous Testing

During development:
1. Run type checking after every file change
2. Test in browser after UI changes
3. Test API endpoints after backend changes
4. Run full test suite before marking complete

## Quality Gates

Code is NOT ready if:
- TypeScript has compilation errors
- Python has import errors
- Linting fails
- Dev servers won't start
- Console shows errors
- UI doesn't render
- API returns errors
- Tests don't pass

**REMEMBER: Quality over speed. Working code over broken features.**
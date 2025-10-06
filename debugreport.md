# Authentication & Bug Analysis Report

## Executive Summary

After comprehensive analysis of the financial planning application codebase, I've identified **critical authentication inconsistencies** that are the root cause of 401 Unauthorized errors during navigation. The application uses **two parallel authentication systems** (axios and fetch) that operate independently, creating race conditions and token synchronization issues. Additionally, there are **19 high-priority issues** across the codebase including inconsistent API patterns, missing error handling, token storage issues, and code quality concerns.

**Primary Issue**: The application has a **dual authentication system** where:
1. `authService` (auth.ts) uses axios with global headers
2. Module services use fetch with localStorage
3. These systems don't communicate, causing token desync

**Impact**: Users experience 401 errors when navigating because some services retrieve the token from authService's memory while others fetch from localStorage, creating race conditions on page load.

## Root Cause: 401 Errors

### Primary Issue: Dual Authentication System

The application uses **TWO separate HTTP client libraries** for authentication:

1. **Axios (auth.ts)** - Sets token globally via `axios.defaults.headers.common['Authorization']`
   - Used by: `authService.getCurrentUser()`, `authService.login()`, `authService.register()`
   - Token stored: In-memory (`this.token`) AND localStorage

2. **Fetch API (module services)** - Retrieves token from localStorage per-request
   - Used by: All 5 module services (protection, savings, investment, retirement, IHT)
   - Some functions use centralized `fetchJSON` helper (api.ts)
   - Other functions fetch directly from localStorage

**File: `/Users/CSJ/Desktop/finPlanFull/frontend/src/services/auth.ts`**
```typescript
// Lines 19-30
private token: string | null = null;

constructor() {
  this.token = localStorage.getItem('access_token');
  if (this.token) {
    this.setAuthHeader(this.token);  // ⚠️ Sets axios global header
  }
}

private setAuthHeader(token: string) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;  // ⚠️ Axios only
}
```

**File: `/Users/CSJ/Desktop/finPlanFull/frontend/src/services/modules/protection.ts`**
```typescript
// Lines 35-50 - INCONSISTENT: Bypasses authService entirely
export async function getProducts(): Promise<ProtectionProduct[]> {
  const token = localStorage.getItem('access_token');  // ⚠️ Direct localStorage access

  const response = await fetch(`${API_BASE_URL}/api/modules/protection/products`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,  // ⚠️ Manual header construction
    },
  });
  // ...
}
```

### Evidence

**1. Inconsistent Token Retrieval**
   - `auth.ts` maintains token in memory (`this.token`)
   - Module services directly access `localStorage.getItem('access_token')`
   - `api.ts` helper uses fallback: `authService.getToken() || localStorage.getItem('access_token')`

**2. Axios vs Fetch Split**
   - Axios: 6 calls (auth.ts, RetirementPlanning.tsx, FinancialProjections.tsx, MonteCarloSimulation.tsx, PensionDashboardWidget.tsx)
   - Fetch: 40+ calls across all module services

**3. Recent Fix Attempted (But Incomplete)**
   - Commit `52683dae`: "Fix 401 Unauthorized errors - centralize auth token handling"
   - Created `api.ts` with centralized helpers (fetchJSON, postJSON, putJSON, deleteJSON)
   - **ONLY updated getDashboard() and getSummary()** in each module
   - **LEFT 30+ other functions** still using direct localStorage access

**4. Example of Inconsistency in Same File**

   `/Users/CSJ/Desktop/finPlanFull/frontend/src/services/modules/protection.ts`:
   ```typescript
   // Line 21 - USES centralized helper ✅
   export async function getDashboard(): Promise<ModuleDashboardData> {
     return fetchJSON<ModuleDashboardData>('/api/modules/protection/dashboard');
   }

   // Line 34 - BYPASSES helper, direct localStorage ❌
   export async function getProducts(): Promise<ProtectionProduct[]> {
     const token = localStorage.getItem('access_token');
     const response = await fetch(...)
   }
   ```

### Impact

**User Experience**:
- 401 errors on page navigation (especially after login)
- Inconsistent authentication state across the app
- Token may be set in axios but not retrieved by fetch calls
- Race conditions on initial page load

**Technical Impact**:
- Maintenance nightmare: Two separate auth patterns to maintain
- Difficult to debug: Token issues manifest differently depending on which HTTP client is used
- Token refresh would need to update BOTH systems
- Unit tests would need to mock BOTH axios and fetch

## Authentication System Analysis

### Current Implementation

#### Frontend Authentication Flow

1. **Login Process** (auth.ts):
   ```
   User enters credentials
   → authService.login() called
   → Axios POST to /api/auth/token
   → Token stored in localStorage
   → Token set in axios.defaults.headers
   → Token stored in authService.token (memory)
   ```

2. **Protected API Calls**:
   ```
   Two paths:

   Path A (Axios):
   → Request made via axios
   → Token automatically attached from axios.defaults.headers

   Path B (Fetch):
   → Token retrieved from localStorage
   → Token manually added to request headers
   ```

3. **Authentication Check** (App.tsx):
   ```typescript
   // Lines 87-103
   const checkAuth = async () => {
     if (authService.isAuthenticated()) {  // Checks in-memory token
       try {
         const user = await authService.getCurrentUser();  // Uses axios
         setUserName(user.full_name || user.username);
         setIsAuthenticated(true);
       } catch (error) {
         authService.logout();
         setIsAuthenticated(false);
       }
     }
     setLoading(false);
   };
   ```

#### Backend Authentication Flow

**Consistent and Correct**:
- All protected endpoints use `Depends(get_current_user)`
- JWT validation in `/backend/app/api/auth/auth.py` (lines 18-42)
- Token expiration: 30 minutes (config.py line 19)
- OAuth2PasswordBearer scheme properly configured

**File: `/Users/CSJ/Desktop/finPlanFull/backend/app/api/auth/auth.py`**
```python
# Lines 15-42 - CORRECT IMPLEMENTATION ✅
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    # ... validation logic
```

### Issues Found

#### Critical Issues (P0)

**1. Dual HTTP Client Pattern**
- **Severity**: Critical
- **Files**:
  - `/frontend/src/services/auth.ts` (axios)
  - `/frontend/src/services/modules/*.ts` (fetch)
  - `/frontend/src/pages/*.tsx` (mixed)
- **Issue**: Two separate HTTP libraries maintaining separate auth state
- **Impact**: Token synchronization issues, race conditions

**2. Inconsistent Token Retrieval**
- **Severity**: Critical
- **Files**: All 5 module service files
- **Issue**:
  - getDashboard() uses `fetchJSON` helper (gets token from authService)
  - getProducts(), getAnalytics(), create/update/delete use direct `localStorage.getItem()`
- **Impact**: Race condition where getDashboard() works but getProducts() fails

**3. Wrong Token Key in ProtectionDashboard**
- **Severity**: Critical
- **File**: `/frontend/src/pages/modules/protection/ProtectionDashboard.tsx:48`
- **Issue**:
  ```typescript
  const token = localStorage.getItem('token');  // ❌ WRONG KEY
  // Should be: localStorage.getItem('access_token')
  ```
- **Impact**: **Always fails authentication** - this page cannot work at all

**4. No Token Refresh Mechanism**
- **Severity**: Critical
- **Issue**: Token expires in 30 minutes, no refresh logic
- **Impact**: User forced to re-login every 30 minutes

#### High Priority Issues (P1)

**5. Missing Error Handling for 401 Responses**
- **Severity**: High
- **Files**: All module service files
- **Issue**: No automatic logout or redirect on 401
- **Expected**: 401 should clear token and redirect to login
- **Actual**: Error thrown, user sees error message

**6. Axios Used in React Components**
- **Severity**: High
- **Files**:
  - RetirementPlanning.tsx (line 213)
  - FinancialProjections.tsx (lines 261, 288)
  - MonteCarloSimulation.tsx (lines 199, 224)
  - PensionDashboardWidget.tsx (line 167)
- **Issue**: Direct axios usage in components, bypasses service layer
- **Impact**: Inconsistent error handling, harder to maintain

**7. API URL Hardcoded in Components**
- **Severity**: High
- **File**: `/frontend/src/pages/modules/protection/ProtectionDashboard.tsx:49`
- **Issue**:
  ```typescript
  const response = await fetch('http://localhost:8000/api/modules/protection/dashboard', {
  ```
- **Impact**: Won't work in production, ignores REACT_APP_API_URL env var

**8. No Loading/Error States in API Helpers**
- **Severity**: High
- **File**: `/frontend/src/utils/api.ts`
- **Issue**: fetchJSON/postJSON throw errors, no loading state management
- **Impact**: Each component must implement own loading/error handling

**9. Token Stored Insecurely**
- **Severity**: High
- **Issue**: Token in localStorage (XSS vulnerable)
- **Better**: httpOnly cookie (XSS-proof) or sessionStorage (limited to tab)
- **Impact**: Token accessible to any JavaScript, vulnerable to XSS attacks

**10. Missing CSRF Protection**
- **Severity**: High
- **Issue**: No CSRF tokens for state-changing operations
- **Impact**: Vulnerable to CSRF attacks

### Inconsistencies

#### Authentication Patterns

| Pattern | Used By | Files |
|---------|---------|-------|
| Axios + global headers | auth.ts | 1 |
| Fetch + centralized helper | getDashboard/getSummary | 10 functions |
| Fetch + direct localStorage | All other module functions | 30+ functions |
| Axios in components | Legacy pages | 5 files |

#### Token Storage Keys

| Key | Used By |
|-----|---------|
| `access_token` ✅ | auth.ts, api.ts, most module services |
| `token` ❌ | ProtectionDashboard.tsx (WRONG) |

#### API Base URL Construction

| Pattern | Files |
|---------|-------|
| `process.env.REACT_APP_API_URL` | auth.ts, api.ts, module services |
| Hardcoded `http://localhost:8000` | ProtectionDashboard.tsx, docs.ts |

## Additional Bugs & Issues

### Critical Issues (P0 - Must Fix Immediately)

**BUG-001: Wrong localStorage Key Breaks Protection Dashboard**
- **File**: `/frontend/src/pages/modules/protection/ProtectionDashboard.tsx:48`
- **Line**: 48
- **Issue**: Uses `'token'` instead of `'access_token'`
- **Impact**: **Protection Dashboard cannot authenticate - always fails**
- **Fix**: Change `localStorage.getItem('token')` to `localStorage.getItem('access_token')`

**BUG-002: Dual HTTP Client Creates Token Desync**
- **Files**: auth.ts vs all module services
- **Issue**: Axios and Fetch maintain separate auth state
- **Impact**: Race conditions, intermittent 401 errors
- **Fix**: Standardize on ONE HTTP client library

**BUG-003: Incomplete Centralized Auth Migration**
- **Files**: All 5 module service files
- **Issue**: Only getDashboard/getSummary use centralized api.ts helper, rest bypass it
- **Impact**: 80% of API calls still vulnerable to token issues
- **Fix**: Migrate all functions to use centralized helpers

**BUG-004: No Token Expiration Handling**
- **Issue**: 30-minute token expiry, no refresh, no warning
- **Impact**: User gets 401 after 30 minutes, forced to re-login
- **Fix**: Implement token refresh OR session extension OR expiry warning

### High Priority Issues (P1 - Should Fix Soon)

**BUG-005: No Global 401 Error Handler**
- **Files**: All API service files
- **Issue**: Each file throws errors differently, no central 401 handler
- **Impact**: Inconsistent UX when token expires
- **Fix**: Add axios/fetch interceptor to handle 401 globally

**BUG-006: Axios Used Directly in Components**
- **Files**: RetirementPlanning.tsx (line 213), FinancialProjections.tsx (lines 261, 288), MonteCarloSimulation.tsx (lines 199, 224), PensionDashboardWidget.tsx (line 167)
- **Issue**: Components bypass service layer
- **Impact**: Duplicate code, inconsistent error handling
- **Fix**: Move all API calls to service layer

**BUG-007: Hardcoded API URLs**
- **File**: ProtectionDashboard.tsx:49, docs.ts:1
- **Issue**: Hardcoded `http://localhost:8000` ignores env variables
- **Impact**: Won't work in production
- **Fix**: Use `process.env.REACT_APP_API_URL` everywhere

**BUG-008: Missing User Data Persistence**
- **File**: App.tsx:90-98
- **Issue**: User data fetched on every mount but not stored
- **Impact**: Extra API call on every refresh
- **Fix**: Store user data in localStorage or context

**BUG-009: Auth State in Multiple Places**
- **Files**: App.tsx (isAuthenticated state), authService (token + isAuthenticated)
- **Issue**: Auth state duplicated between App and authService
- **Impact**: Can get out of sync
- **Fix**: Single source of truth (React Context or Zustand)

**BUG-010: No CORS Error Handling**
- **Issue**: CORS configured in backend but no client-side error handling
- **Impact**: CORS errors look like network errors to user
- **Fix**: Add specific CORS error detection and messaging

**BUG-011: Inconsistent Error Messages**
- **Files**: All module services
- **Issue**: Some use `errorData.detail`, some use generic messages
- **Impact**: Inconsistent UX
- **Fix**: Standardize error message extraction

**BUG-012: Missing Request Timeout**
- **Files**: All fetch calls
- **Issue**: No timeout configured, requests can hang forever
- **Impact**: Poor UX on slow networks
- **Fix**: Add AbortController with timeout to all fetch calls

**BUG-013: localStorage Used for Sensitive Data**
- **Issue**: JWT token in localStorage (XSS vulnerable)
- **Impact**: Security risk if XSS attack occurs
- **Fix**: Consider httpOnly cookies or sessionStorage

### Medium Priority Issues (P2 - Should Fix When Possible)

**BUG-014: No Request Cancellation**
- **Issue**: Component unmounts don't cancel in-flight requests
- **Impact**: Memory leaks, race conditions, setState on unmounted component
- **Fix**: Use AbortController for all fetch requests

**BUG-015: Duplicate API Base URL Definitions**
- **Files**: Every service file defines `API_BASE_URL`
- **Issue**: Duplicate code, 8+ definitions of same constant
- **Fix**: Single shared constant in config file

**BUG-016: No Request/Response Logging**
- **Issue**: Hard to debug API issues in production
- **Impact**: Can't trace issues without browser DevTools
- **Fix**: Add optional request/response logging

**BUG-017: Missing Type Safety on API Responses**
- **Files**: Module services
- **Issue**: Response types asserted but not validated at runtime
- **Impact**: Runtime errors if backend changes response structure
- **Fix**: Add runtime validation with Zod or similar

**BUG-018: Console.log Statements in Production Code**
- **Files**: docs.ts (lines 94, 139, 181, 221)
- **Issue**: Debug logs left in production code
- **Impact**: Performance, security (may leak sensitive data)
- **Fix**: Remove or wrap in DEBUG flag

**BUG-019: No API Request Retry Logic**
- **Issue**: Network failures immediately fail, no retry
- **Impact**: Poor UX on flaky networks
- **Fix**: Add exponential backoff retry for failed requests

### Low Priority Issues (P3 - Nice to Have Fixes)

**BUG-020: Inconsistent Async/Await Usage**
- **Files**: Various
- **Issue**: Some functions use async/await, others use .then()
- **Impact**: Code style inconsistency
- **Fix**: Standardize on async/await

**BUG-021: No API Response Caching**
- **Issue**: Same data fetched multiple times
- **Impact**: Unnecessary network requests
- **Fix**: Implement caching strategy (React Query, SWR, or custom)

**BUG-022: Unused API Utility Functions**
- **File**: api.ts
- **Issue**: fetchJSON, postJSON, putJSON, deleteJSON created but barely used
- **Impact**: Wasted effort, confusing codebase
- **Fix**: Migrate all API calls to use these helpers

**BUG-023: No API Rate Limiting**
- **Issue**: Client can spam API with requests
- **Impact**: Server load, potential DoS
- **Fix**: Add client-side rate limiting/throttling

**BUG-024: Missing Loading States in Module Pages**
- **Files**: Multiple module dashboard pages
- **Issue**: Some pages show "Loading..." text, others show nothing
- **Impact**: Inconsistent UX
- **Fix**: Standardized loading component

## Detailed Task List

### Phase 1: Authentication Fixes (Critical)

#### Task 1.1: Fix Critical Token Key Bug
- **Priority**: P0 - CRITICAL
- **File**: `/Users/CSJ/Desktop/finPlanFull/frontend/src/pages/modules/protection/ProtectionDashboard.tsx:48`
- **Issue**: Uses wrong localStorage key `'token'` instead of `'access_token'`
- **Fix**:
  ```typescript
  // BEFORE (line 48):
  const token = localStorage.getItem('token');

  // AFTER:
  const token = localStorage.getItem('access_token');
  ```
- **Expected Outcome**: Protection Dashboard can authenticate and load data
- **Test**: Navigate to /protection, verify dashboard loads without 401 error

#### Task 1.2: Standardize on Single HTTP Client
- **Priority**: P0 - CRITICAL
- **Files**:
  - `/frontend/src/services/auth.ts`
  - All module service files
  - Component files using axios
- **Issue**: Application uses both axios and fetch, causing dual auth state
- **Fix Option A** (Recommended): Standardize on Fetch
  ```typescript
  // In auth.ts:
  // 1. Remove axios import and usage
  // 2. Replace axios calls with fetch
  // 3. Remove axios.defaults.headers manipulation
  // 4. Use centralized api.ts helpers

  // BEFORE:
  private setAuthHeader(token: string) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  async login(username: string, password: string): Promise<void> {
    const response = await axios.post<LoginResponse>(...)
  }

  // AFTER:
  async login(username: string, password: string): Promise<void> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/api/auth/token`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data: LoginResponse = await response.json();
    this.token = data.access_token;
    localStorage.setItem('access_token', this.token);
  }
  ```
- **Expected Outcome**: Single HTTP client (Fetch API), consistent token handling
- **Test**: Login, navigate between modules, verify no 401 errors

#### Task 1.3: Complete Centralized Auth Helper Migration
- **Priority**: P0 - CRITICAL
- **Files**: All 5 module service files:
  - `/frontend/src/services/modules/protection.ts`
  - `/frontend/src/services/modules/savings.ts`
  - `/frontend/src/services/modules/investment.ts`
  - `/frontend/src/services/modules/retirement.ts`
  - `/frontend/src/services/modules/iht.ts`
- **Issue**: Only getDashboard/getSummary use centralized helpers, 30+ other functions bypass them
- **Fix**: Convert all functions to use centralized helpers
  ```typescript
  // BEFORE (protection.ts lines 34-50):
  export async function getProducts(): Promise<ProtectionProduct[]> {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`${API_BASE_URL}/api/modules/protection/products`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to fetch protection products');
    }

    return response.json();
  }

  // AFTER:
  export async function getProducts(): Promise<ProtectionProduct[]> {
    return fetchJSON<ProtectionProduct[]>('/api/modules/protection/products');
  }
  ```
- **Functions to Update** (per module - 30+ total):
  - getProducts/getAccounts/getPortfolio/getPensions/getGifts
  - getAnalytics
  - createProduct/createAccount/createInvestment/createPension/createGift
  - updateProduct/updateAccount/updateInvestment/updatePension/updateGift
  - deleteProduct/deleteAccount/deleteInvestment/deletePension/deleteGift
- **Expected Outcome**: All API calls use consistent auth token retrieval
- **Test**: Test all CRUD operations in each module

#### Task 1.4: Implement Global 401 Error Handler
- **Priority**: P0 - CRITICAL
- **File**: `/frontend/src/utils/api.ts`
- **Issue**: No automatic logout/redirect on 401 errors
- **Fix**: Add 401 handling to centralized helpers
  ```typescript
  // In api.ts, update fetchWithAuth:
  export async function fetchWithAuth(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        ...getAuthHeaders(),
        ...options.headers,
      },
    });

    // NEW: Handle 401 globally
    if (response.status === 401) {
      // Clear auth state
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');

      // Redirect to login
      window.location.href = '/login';

      throw new Error('Session expired. Please login again.');
    }

    return response;
  }
  ```
- **Expected Outcome**: All 401 errors automatically log user out and redirect to login
- **Test**:
  1. Login
  2. Manually expire token (wait 30min or modify localStorage)
  3. Try to navigate
  4. Should auto-redirect to login with error message

#### Task 1.5: Implement Token Refresh or Session Extension
- **Priority**: P0 - CRITICAL
- **Files**:
  - `/backend/app/api/auth/auth.py` (new endpoint)
  - `/frontend/src/services/auth.ts` (refresh logic)
  - `/frontend/src/utils/api.ts` (auto-refresh on 401)
- **Issue**: Token expires in 30 minutes with no refresh
- **Fix Option A** - Token Refresh:
  ```python
  # backend/app/api/auth/auth.py
  @router.post("/refresh", response_model=Token)
  async def refresh_token(
      current_user: Annotated[User, Depends(get_current_user)]
  ):
      """Refresh access token"""
      access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
      access_token = create_access_token(
          data={"sub": current_user.username, "user_id": current_user.id},
          expires_delta=access_token_expires
      )
      return {"access_token": access_token, "token_type": "bearer"}
  ```

  ```typescript
  // frontend/src/services/auth.ts
  async refreshToken(): Promise<void> {
    const response = await fetch(`${API_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });

    if (response.ok) {
      const data: LoginResponse = await response.json();
      this.token = data.access_token;
      localStorage.setItem('access_token', this.token);
    } else {
      this.logout();
      throw new Error('Token refresh failed');
    }
  }

  // frontend/src/utils/api.ts - update fetchWithAuth
  if (response.status === 401) {
    // Try to refresh token once
    try {
      await authService.refreshToken();
      // Retry original request with new token
      return fetchWithAuth(endpoint, options);
    } catch {
      // Refresh failed, logout
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
  }
  ```
- **Fix Option B** - Activity-Based Extension:
  - Extend token expiry on each authenticated request
  - Backend sends new token in response header
  - Frontend updates token automatically
- **Expected Outcome**: User stays logged in during active use
- **Test**:
  1. Login
  2. Use app continuously for > 30 minutes
  3. Should not be logged out

### Phase 2: Code Quality & Consistency (High Priority)

#### Task 2.1: Remove Axios from Components
- **Priority**: P1 - HIGH
- **Files**:
  - `/frontend/src/pages/RetirementPlanning.tsx:213`
  - `/frontend/src/pages/FinancialProjections.tsx:261,288`
  - `/frontend/src/pages/MonteCarloSimulation.tsx:199,224`
  - `/frontend/src/components/pension/PensionDashboardWidget.tsx:167`
- **Issue**: Components make direct axios API calls, bypassing service layer
- **Fix**: Move API calls to service layer
  ```typescript
  // BEFORE (RetirementPlanning.tsx:213):
  const response = await axios.get('/api/products/retirement/projection', {
    params: { retirement_age: retirementAge, expected_return: expectedReturn }
  });

  // AFTER:
  // 1. Create service function in services/products.ts:
  export async function getRetirementProjection(
    retirementAge: number,
    expectedReturn: number
  ): Promise<ProjectionData> {
    return fetchJSON<ProjectionData>(
      `/api/products/retirement/projection?retirement_age=${retirementAge}&expected_return=${expectedReturn}`
    );
  }

  // 2. Use in component:
  import { getRetirementProjection } from '../services/products';

  const projection = await getRetirementProjection(retirementAge, expectedReturn);
  ```
- **Expected Outcome**: All API calls go through service layer, consistent error handling
- **Test**: Test each page's functionality after refactor

#### Task 2.2: Fix Hardcoded API URLs
- **Priority**: P1 - HIGH
- **Files**:
  - `/frontend/src/pages/modules/protection/ProtectionDashboard.tsx:49`
  - `/frontend/src/services/docs.ts:1`
- **Issue**: Hardcoded `http://localhost:8000` ignores environment variables
- **Fix**:
  ```typescript
  // BEFORE (ProtectionDashboard.tsx:49):
  const response = await fetch('http://localhost:8000/api/modules/protection/dashboard', {

  // AFTER:
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const response = await fetch(`${API_BASE_URL}/api/modules/protection/dashboard`, {

  // OR BETTER: Use centralized helper
  import { fetchJSON } from '../../../utils/api';
  const data = await fetchJSON('/api/modules/protection/dashboard');
  ```
- **Expected Outcome**: App works in all environments (dev, staging, prod)
- **Test**: Build for production, verify API calls use correct URL

#### Task 2.3: Consolidate API Base URL Constants
- **Priority**: P1 - HIGH
- **Files**: All service files (8+ files)
- **Issue**: `API_BASE_URL` defined separately in each service file
- **Fix**:
  ```typescript
  // Create /frontend/src/config/api.ts:
  export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Update all service files:
  // BEFORE:
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // AFTER:
  import { API_BASE_URL } from '../../config/api';
  ```
- **Expected Outcome**: Single source of truth for API URL
- **Test**: Change env variable, verify all services use new URL

#### Task 2.4: Add Request Timeout to All Fetch Calls
- **Priority**: P1 - HIGH
- **File**: `/frontend/src/utils/api.ts`
- **Issue**: Requests can hang forever on slow networks
- **Fix**:
  ```typescript
  // In api.ts, update fetchWithAuth:
  export async function fetchWithAuth(
    endpoint: string,
    options: RequestInit = {},
    timeout: number = 30000  // 30 second default
  ): Promise<Response> {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          ...getAuthHeaders(),
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (response.status === 401) {
        // ... 401 handling
      }

      return response;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error.name === 'AbortError') {
        throw new Error('Request timeout - please check your connection');
      }

      throw error;
    }
  }
  ```
- **Expected Outcome**: Requests timeout after 30s with clear error message
- **Test**:
  1. Simulate slow network (Chrome DevTools throttling)
  2. Make API call
  3. Should timeout after 30s with error message

#### Task 2.5: Implement Request Cancellation on Component Unmount
- **Priority**: P1 - HIGH
- **Files**: All pages making API calls in useEffect
- **Issue**: In-flight requests continue after component unmounts
- **Fix**:
  ```typescript
  // Example pattern for all pages:
  useEffect(() => {
    const controller = new AbortController();

    async function fetchData() {
      try {
        // Pass signal to fetch calls
        const data = await fetchWithAuth('/api/endpoint', {
          signal: controller.signal
        });
        setData(data);
      } catch (error) {
        if (error.name !== 'AbortError') {
          setError(error.message);
        }
      }
    }

    fetchData();

    // Cleanup: cancel request on unmount
    return () => controller.abort();
  }, []);
  ```
- **Expected Outcome**: No memory leaks, no setState warnings
- **Test**:
  1. Navigate to page
  2. Immediately navigate away
  3. Check console for warnings
  4. Should be none

#### Task 2.6: Standardize Error Message Extraction
- **Priority**: P1 - HIGH
- **Files**: All module service files
- **Issue**: Inconsistent error message patterns
- **Fix**:
  ```typescript
  // In api.ts, add helper:
  export function extractErrorMessage(error: any, defaultMessage: string): string {
    if (error.detail) return error.detail;
    if (error.message) return error.message;
    if (typeof error === 'string') return error;
    return defaultMessage;
  }

  // Use in all catch blocks:
  // BEFORE:
  const errorData = await response.json().catch(() => ({}));
  throw new Error(errorData.detail || 'Failed to fetch protection products');

  // AFTER:
  const errorData = await response.json().catch(() => ({}));
  throw new Error(extractErrorMessage(errorData, 'Failed to fetch protection products'));
  ```
- **Expected Outcome**: Consistent error messages across app
- **Test**: Trigger various errors, verify consistent messaging

#### Task 2.7: Move Auth State to React Context
- **Priority**: P1 - HIGH
- **Files**:
  - `/frontend/src/App.tsx` (currently manages isAuthenticated)
  - `/frontend/src/services/auth.ts` (currently manages token)
  - Create `/frontend/src/context/AuthContext.tsx`
- **Issue**: Auth state duplicated between App and authService
- **Fix**:
  ```typescript
  // Create context/AuthContext.tsx:
  interface AuthContextType {
    isAuthenticated: boolean;
    user: UserData | null;
    token: string | null;
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
    checkAuth: () => Promise<void>;
  }

  export const AuthContext = createContext<AuthContextType | undefined>(undefined);

  export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState<UserData | null>(null);
    const [token, setToken] = useState<string | null>(
      localStorage.getItem('access_token')
    );

    // Implement login, logout, checkAuth
    // ...

    return (
      <AuthContext.Provider value={{ isAuthenticated, user, token, login, logout, checkAuth }}>
        {children}
      </AuthContext.Provider>
    );
  }

  export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used within AuthProvider');
    return context;
  }

  // Update App.tsx:
  function App() {
    return (
      <AuthProvider>
        <CustomThemeProvider>
          <RouterProvider router={router} />
        </CustomThemeProvider>
      </AuthProvider>
    );
  }
  ```
- **Expected Outcome**: Single source of truth for auth state
- **Test**: Login, verify state updates everywhere simultaneously

#### Task 2.8: Remove Console.log Statements
- **Priority**: P1 - HIGH
- **Files**: `/frontend/src/services/docs.ts:94,139,181,221`
- **Issue**: Debug logs in production code
- **Fix**:
  ```typescript
  // BEFORE:
  console.error('Error fetching documentation list:', error);

  // AFTER - Option A: Remove entirely
  // (no code)

  // AFTER - Option B: Conditional logging
  if (process.env.NODE_ENV === 'development') {
    console.error('Error fetching documentation list:', error);
  }

  // AFTER - Option C: Logging service
  import { logger } from '../utils/logger';
  logger.error('Error fetching documentation list:', error);
  ```
- **Expected Outcome**: No console logs in production builds
- **Test**: Build for production, open console, should be clean

### Phase 3: Security Improvements (Medium Priority)

#### Task 3.1: Implement Token Storage in httpOnly Cookie
- **Priority**: P2 - MEDIUM
- **Files**:
  - `/backend/app/api/auth/auth.py` (set cookie in response)
  - `/frontend/src/services/auth.ts` (remove localStorage)
- **Issue**: Token in localStorage vulnerable to XSS
- **Fix**:
  ```python
  # backend/app/api/auth/auth.py
  from fastapi import Response

  @router.post("/token")
  async def login(
      response: Response,  # Add response parameter
      form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
      db: Session = Depends(get_db)
  ):
      # ... validation

      access_token = create_access_token(...)

      # Set httpOnly cookie
      response.set_cookie(
          key="access_token",
          value=access_token,
          httponly=True,
          secure=True,  # HTTPS only
          samesite="lax",
          max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
      )

      return {"access_token": access_token, "token_type": "bearer"}
  ```

  ```typescript
  // frontend/src/services/auth.ts
  // REMOVE localStorage.setItem('access_token', ...)
  // Cookie automatically sent with requests
  ```
- **Expected Outcome**: Token not accessible to JavaScript, XSS-proof
- **Test**: Login, verify cookie set, verify requests work without localStorage

#### Task 3.2: Add CSRF Protection
- **Priority**: P2 - MEDIUM
- **Files**: Backend auth endpoints
- **Issue**: No CSRF tokens for state-changing operations
- **Fix**:
  ```python
  # Install: pip install fastapi-csrf-protect
  from fastapi_csrf_protect import CsrfProtect

  # Add to main.py:
  @app.post("/api/csrf-token")
  async def get_csrf_token(csrf_protect: CsrfProtect = Depends()):
      response = JSONResponse(content={"csrf_token": csrf_protect.generate_csrf()})
      csrf_protect.set_csrf_cookie(response)
      return response

  # Protect state-changing endpoints:
  @router.post("/token")
  async def login(
      csrf_protect: CsrfProtect = Depends(),
      ...
  ):
      csrf_protect.validate_csrf(request)
      # ... rest of login
  ```
- **Expected Outcome**: CSRF attacks prevented
- **Test**: Attempt CSRF attack, should be blocked

#### Task 3.3: Add Request/Response Logging
- **Priority**: P2 - MEDIUM
- **File**: `/frontend/src/utils/api.ts`
- **Issue**: Hard to debug API issues in production
- **Fix**:
  ```typescript
  // Create utils/logger.ts:
  export const logger = {
    log: (message: string, data?: any) => {
      if (process.env.NODE_ENV === 'development' || process.env.REACT_APP_ENABLE_LOGGING) {
        console.log(`[${new Date().toISOString()}] ${message}`, data);
      }
    },
    error: (message: string, error?: any) => {
      if (process.env.NODE_ENV === 'development' || process.env.REACT_APP_ENABLE_LOGGING) {
        console.error(`[${new Date().toISOString()}] ${message}`, error);
      }
      // In production, send to error tracking service (Sentry, etc.)
    }
  };

  // In api.ts, add logging:
  export async function fetchWithAuth(...) {
    logger.log(`API Request: ${options.method || 'GET'} ${endpoint}`);

    const response = await fetch(...);

    if (!response.ok) {
      logger.error(`API Error: ${response.status} ${endpoint}`, await response.text());
    } else {
      logger.log(`API Success: ${response.status} ${endpoint}`);
    }

    return response;
  }
  ```
- **Expected Outcome**: API calls logged in development, can enable in production for debugging
- **Test**: Make API calls, verify logs appear in console

### Phase 4: Performance & Optimization (Low Priority)

#### Task 4.1: Implement API Response Caching
- **Priority**: P3 - LOW
- **Files**: All service files
- **Issue**: Same data fetched multiple times
- **Fix Option A** - Use React Query:
  ```typescript
  // Install: npm install @tanstack/react-query

  // Setup in App.tsx:
  import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000, // 5 minutes
        cacheTime: 10 * 60 * 1000, // 10 minutes
      },
    },
  });

  function App() {
    return (
      <QueryClientProvider client={queryClient}>
        {/* ... */}
      </QueryClientProvider>
    );
  }

  // Use in components:
  import { useQuery } from '@tanstack/react-query';

  function Dashboard() {
    const { data, isLoading, error } = useQuery({
      queryKey: ['dashboard'],
      queryFn: () => getDashboard(),
    });
  }
  ```
- **Fix Option B** - Custom Cache:
  - Extend SimpleCache in docs.ts to be reusable
  - Add cache layer to api.ts helpers
- **Expected Outcome**: Reduced API calls, faster page loads
- **Test**:
  1. Navigate to page (API call made)
  2. Navigate away and back (no API call, cached data used)
  3. Wait 5 minutes
  4. Navigate back (new API call, cache refreshed)

#### Task 4.2: Add API Request Rate Limiting
- **Priority**: P3 - LOW
- **File**: `/frontend/src/utils/api.ts`
- **Issue**: Client can spam API with requests
- **Fix**:
  ```typescript
  // Create utils/rateLimiter.ts:
  class RateLimiter {
    private requests: Map<string, number[]> = new Map();
    private limit: number;
    private window: number;

    constructor(limit: number = 10, windowMs: number = 1000) {
      this.limit = limit;
      this.window = windowMs;
    }

    canMakeRequest(key: string): boolean {
      const now = Date.now();
      const requests = this.requests.get(key) || [];

      // Remove old requests outside window
      const recentRequests = requests.filter(time => now - time < this.window);

      if (recentRequests.length >= this.limit) {
        return false;
      }

      recentRequests.push(now);
      this.requests.set(key, recentRequests);
      return true;
    }
  }

  const rateLimiter = new RateLimiter(10, 1000); // 10 requests per second

  // In api.ts:
  export async function fetchWithAuth(endpoint: string, ...) {
    if (!rateLimiter.canMakeRequest(endpoint)) {
      throw new Error('Rate limit exceeded. Please slow down.');
    }
    // ... rest of fetch
  }
  ```
- **Expected Outcome**: Client-side rate limiting prevents API spam
- **Test**: Make rapid API calls, verify rate limit kicks in

#### Task 4.3: Add Loading Skeleton Components
- **Priority**: P3 - LOW
- **Files**: All module dashboard pages
- **Issue**: Inconsistent loading states
- **Fix**:
  ```typescript
  // Create components/common/Skeleton.tsx:
  export const SkeletonCard = () => (
    <Card>
      <SkeletonLine width="60%" />
      <SkeletonLine width="40%" />
      <SkeletonLine width="80%" />
    </Card>
  );

  // Use in pages:
  if (loading) {
    return (
      <>
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </>
    );
  }
  ```
- **Expected Outcome**: Consistent, polished loading experience
- **Test**: Navigate to pages, verify skeleton appears while loading

#### Task 4.4: Implement Runtime Response Validation
- **Priority**: P3 - LOW
- **Files**: All service files
- **Issue**: No runtime validation of API responses
- **Fix**:
  ```typescript
  // Install: npm install zod
  import { z } from 'zod';

  // Define schemas:
  const ProtectionProductSchema = z.object({
    id: z.number(),
    name: z.string(),
    provider: z.string(),
    value: z.number(),
    // ... all fields
  });

  // Use in service:
  export async function getProducts(): Promise<ProtectionProduct[]> {
    const data = await fetchJSON('/api/modules/protection/products');
    return z.array(ProtectionProductSchema).parse(data);
  }
  ```
- **Expected Outcome**: Runtime errors if backend changes response structure
- **Test**: Mock invalid API response, verify Zod throws validation error

## Testing Strategy

### Unit Tests

**Authentication Tests** (auth.test.ts - already exists):
- ✅ Test login success
- ✅ Test login failure
- ✅ Test getCurrentUser with valid token
- ✅ Test getCurrentUser with expired token (401)
- ✅ Test logout
- ⚠️ ADD: Test token refresh
- ⚠️ ADD: Test token expiration handling

**API Helper Tests** (api.test.ts - create):
- Test getAuthHeaders retrieves token correctly
- Test fetchWithAuth adds auth header
- Test 401 handling triggers logout
- Test timeout handling
- Test request cancellation

**Service Tests** (modules/*.test.ts - create):
- Test getDashboard with valid data
- Test getProducts handles errors
- Test createProduct sends correct payload
- Test updateProduct merges data correctly
- Test deleteProduct confirms deletion

### Integration Tests

**Authentication Flow**:
1. Login with valid credentials → Token stored → User data fetched
2. Navigate to protected route → Token sent → Data loaded
3. Token expires → 401 received → Auto-logout → Redirect to login
4. Token refresh → New token stored → Request retried

**Module Navigation**:
1. Login → Dashboard loads all module summaries
2. Click Protection module → Dashboard loads without 401
3. Click Savings module → Dashboard loads without 401
4. Click Investment module → Dashboard loads without 401
5. Navigate back to main dashboard → Summaries still cached

**CRUD Operations**:
1. Create protection product → API success → Product appears in list
2. Update protection product → API success → Product updated
3. Delete protection product → API success → Product removed
4. Verify all operations use consistent auth

### E2E Tests (Playwright - already implemented)

**Existing Tests** (from test plan):
- Authentication flow
- Module navigation
- Dashboard loading
- Product CRUD operations

**Add Tests For**:
- Token expiration handling
- 401 error handling
- Network timeout handling
- Concurrent request handling

### Manual Testing Checklist

#### Authentication
- [ ] Login with valid credentials
- [ ] Login with invalid credentials (verify error)
- [ ] Token persists across page refresh
- [ ] Token expires after 30 minutes (or refreshes)
- [ ] Logout clears token and redirects
- [ ] 401 error triggers automatic logout
- [ ] Can re-login after logout

#### Module Navigation
- [ ] Dashboard loads all module summaries without 401
- [ ] Protection module loads without 401
- [ ] Savings module loads without 401
- [ ] Investment module loads without 401
- [ ] Retirement module loads without 401
- [ ] IHT Planning module loads without 401
- [ ] Navigate between modules rapidly (no race conditions)

#### API Calls
- [ ] All CRUD operations work in each module
- [ ] Error messages displayed consistently
- [ ] Loading states appear correctly
- [ ] Timeout after 30 seconds on slow network
- [ ] Requests canceled when navigating away
- [ ] No console errors

#### Cross-Browser
- [ ] Test in Chrome
- [ ] Test in Firefox
- [ ] Test in Safari
- [ ] Test in Edge

#### Performance
- [ ] Dashboard loads in < 2 seconds
- [ ] Module pages load in < 1 second
- [ ] No memory leaks (check DevTools memory tab)
- [ ] No excessive re-renders (check React DevTools)

## Prevention Recommendations

### 1. Establish Coding Standards

**Create `/frontend/FRONTEND_STANDARDS.md`**:
```markdown
# Frontend Coding Standards

## Authentication
- ✅ DO: Use centralized API helpers (api.ts) for all API calls
- ✅ DO: Use authService for all auth operations
- ❌ DON'T: Access localStorage directly for tokens
- ❌ DON'T: Use axios in components
- ❌ DON'T: Hardcode API URLs

## API Calls
- ✅ DO: All API calls through service layer
- ✅ DO: Handle errors consistently using extractErrorMessage
- ✅ DO: Add timeout and cancellation to all requests
- ❌ DON'T: Make fetch/axios calls directly in components

## Error Handling
- ✅ DO: Display user-friendly error messages
- ✅ DO: Log errors for debugging
- ✅ DO: Handle 401 globally (automatic logout)
- ❌ DON'T: Swallow errors silently

## State Management
- ✅ DO: Use React Context for global state (auth, theme)
- ✅ DO: Use local state for component-specific data
- ✅ DO: Cancel requests on component unmount
- ❌ DON'T: Duplicate state in multiple places

## Code Quality
- ✅ DO: Use TypeScript strict mode
- ✅ DO: Add types for all API responses
- ✅ DO: Remove console.log before commit
- ❌ DON'T: Use 'any' type
```

### 2. Add Pre-Commit Hooks

**Install Husky + Lint-Staged**:
```bash
npm install -D husky lint-staged

# In package.json:
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}

# Initialize husky:
npx husky install
npx husky add .husky/pre-commit "npx lint-staged"
```

**Add ESLint Rules**:
```javascript
// .eslintrc.js
module.exports = {
  rules: {
    // Prevent console.log in production
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn',

    // Prevent axios usage outside auth.ts
    'no-restricted-imports': [
      'error',
      {
        paths: [{
          name: 'axios',
          message: 'Use centralized API helpers from utils/api.ts instead'
        }]
      }
    ],

    // Prevent direct localStorage access in most files
    'no-restricted-globals': [
      'error',
      {
        name: 'localStorage',
        message: 'Use authService.getToken() instead of direct localStorage access'
      }
    ],

    // Enforce proper cleanup in useEffect
    'react-hooks/exhaustive-deps': 'error',
  }
};
```

### 3. Add Architecture Decision Records (ADRs)

**Create `/docs/adr/0001-authentication-architecture.md`**:
```markdown
# ADR 0001: Authentication Architecture

## Status: Accepted

## Context
Application needs secure, consistent authentication across all API calls.

## Decision
- Use Fetch API (not axios) for all HTTP requests
- Centralized auth helpers in utils/api.ts
- Single source of truth: AuthContext
- Token stored in httpOnly cookie (not localStorage)
- Automatic 401 handling with logout + redirect

## Consequences
- All API calls must use centralized helpers
- Cannot use axios in application code
- Token not accessible to JavaScript (XSS-proof)
- Token automatically sent with all requests (cookie-based)

## Compliance
- All new API calls must use fetchJSON/postJSON/putJSON/deleteJSON
- No direct fetch or axios calls in components
- No direct localStorage access for tokens
```

### 4. Add Code Review Checklist

**Create `/docs/CODE_REVIEW_CHECKLIST.md`**:
```markdown
# Code Review Checklist

## Authentication & API Calls
- [ ] API calls use centralized helpers (api.ts)?
- [ ] No direct axios usage?
- [ ] No hardcoded API URLs?
- [ ] Error handling consistent?
- [ ] Loading states implemented?
- [ ] Request cancellation on unmount?

## Security
- [ ] No sensitive data in console.log?
- [ ] Token not exposed?
- [ ] Input validation added?
- [ ] SQL injection prevented (backend)?
- [ ] XSS prevented?

## Performance
- [ ] No unnecessary re-renders?
- [ ] Large lists virtualized?
- [ ] Images optimized?
- [ ] Bundle size impact checked?

## Testing
- [ ] Unit tests added?
- [ ] Integration tests added?
- [ ] Manual testing performed?
- [ ] Edge cases covered?

## Documentation
- [ ] Code comments for complex logic?
- [ ] README updated if needed?
- [ ] API documentation updated?
```

### 5. Set Up Automated Testing

**CI/CD Pipeline** (GitHub Actions):
```yaml
# .github/workflows/pr-checks.yml
name: PR Checks

on: [pull_request]

jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: cd frontend && npm install
      - name: Lint
        run: cd frontend && npm run lint
      - name: Type check
        run: cd frontend && npm run type-check
      - name: Unit tests
        run: cd frontend && npm test -- --coverage
      - name: Build
        run: cd frontend && npm run build

  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: cd backend && pip install -r requirements.txt
      - name: Run tests
        run: cd backend && pytest --cov=app tests/

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start services
        run: docker-compose up -d
      - name: Run Playwright tests
        run: cd frontend && npm run test:e2e
```

### 6. Implement Monitoring & Alerting

**Frontend Error Tracking**:
```typescript
// Setup Sentry or similar
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  integrations: [
    new Sentry.BrowserTracing(),
    new Sentry.Replay(),
  ],

  // Track API errors
  beforeSend(event, hint) {
    const error = hint.originalException;

    // Alert on authentication errors
    if (error.message?.includes('401')) {
      Sentry.captureMessage('Authentication Error', 'error');
    }

    return event;
  }
});
```

**Backend Monitoring**:
```python
# Add request logging middleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger.info(f"{request.method} {request.url}")

        response = await call_next(request)

        if response.status_code >= 400:
            logger.error(f"{request.method} {request.url} -> {response.status_code}")

        return response

app.add_middleware(LoggingMiddleware)
```

### 7. Regular Security Audits

**Schedule Quarterly**:
1. Run `npm audit` and fix vulnerabilities
2. Review authentication implementation
3. Check for exposed secrets (use git-secrets)
4. Penetration testing (if budget allows)
5. Update dependencies
6. Review access logs for suspicious activity

### 8. Documentation Maintenance

**Keep Updated**:
- `/Users/CSJ/Desktop/finPlanFull/CLAUDE.md` - Development guidelines
- `/Users/CSJ/Desktop/finPlanFull/docs/ARCHITECTURE.md` - System architecture
- `/Users/CSJ/Desktop/finPlanFull/docs/API_DOCUMENTATION.md` - API endpoints
- `/Users/CSJ/Desktop/finPlanFull/frontend/FRONTEND_STANDARDS.md` - Frontend standards

**Add Missing**:
- Authentication flow diagram
- API call sequence diagrams
- Error handling flowcharts
- Deployment guide
- Troubleshooting guide

## Appendix

### Files Reviewed (Complete List)

#### Frontend Files (42 files)
**Services** (11 files):
- `/frontend/src/services/auth.ts`
- `/frontend/src/services/products.ts`
- `/frontend/src/services/docs.ts`
- `/frontend/src/services/modules/protection.ts`
- `/frontend/src/services/modules/savings.ts`
- `/frontend/src/services/modules/investment.ts`
- `/frontend/src/services/modules/retirement.ts`
- `/frontend/src/services/modules/iht.ts`
- `/frontend/src/services/modules/dashboard.ts`
- `/frontend/src/utils/api.ts`
- `/frontend/src/context/ThemeContext.tsx`

**Pages** (16 files):
- `/frontend/src/pages/Dashboard.tsx`
- `/frontend/src/pages/LearningCentre.tsx`
- `/frontend/src/pages/RetirementPlanningUK.tsx`
- `/frontend/src/pages/RetirementPlanning.tsx`
- `/frontend/src/pages/TaxOptimization.tsx`
- `/frontend/src/pages/FinancialProjections.tsx`
- `/frontend/src/pages/MonteCarloSimulation.tsx`
- `/frontend/src/pages/IHTCalculator.tsx`
- `/frontend/src/pages/IHTCalculatorEnhanced.tsx`
- `/frontend/src/pages/Chat.tsx`
- `/frontend/src/pages/modules/protection/ProtectionDashboard.tsx`
- `/frontend/src/pages/modules/protection/ProtectionProducts.tsx`
- `/frontend/src/pages/modules/protection/ProtectionAnalytics.tsx`
- `/frontend/src/pages/modules/savings/SavingsDashboard.tsx`
- `/frontend/src/pages/modules/savings/SavingsAccounts.tsx`
- `/frontend/src/pages/modules/savings/SavingsGoals.tsx`

**Core** (6 files):
- `/frontend/src/App.tsx`
- `/frontend/src/index.tsx`
- `/frontend/src/components/ErrorBoundary.tsx`
- `/frontend/src/components/ExportButtons.tsx`
- `/frontend/src/components/pension/PensionDashboardWidget.tsx`
- `/frontend/src/components/modules/protection/ProtectionProductForm.tsx`

**Tests** (3 files):
- `/frontend/src/__tests__/services/auth.test.ts`
- `/frontend/src/__tests__/pages/Dashboard.test.tsx`
- `/frontend/src/__tests__/setupTests.ts`

**Config** (6 files):
- `/frontend/package.json`
- `/frontend/package-lock.json`
- `/frontend/tsconfig.json`
- `/frontend/.eslintrc.js`
- `/frontend/.prettierrc`
- `/frontend/public/index.html`

#### Backend Files (15 files)
**API** (10 files):
- `/backend/app/api/auth/auth.py`
- `/backend/app/api/modules/protection/protection.py`
- `/backend/app/api/modules/protection/products.py`
- `/backend/app/api/modules/savings/savings.py`
- `/backend/app/api/modules/investment/investment.py`
- `/backend/app/api/modules/retirement/retirement.py`
- `/backend/app/api/modules/iht/iht.py`
- `/backend/app/api/dashboard.py`
- `/backend/app/api/docs.py`
- `/backend/app/main.py`

**Core** (5 files):
- `/backend/app/core/config.py`
- `/backend/app/core/security.py`
- `/backend/app/database.py`
- `/backend/app/db/base.py`
- `/backend/app/models/user.py`

#### Documentation Files (8 files)
- `/Users/CSJ/Desktop/finPlanFull/CLAUDE.md`
- `/Users/CSJ/Desktop/finPlanFull/README.md`
- `/Users/CSJ/Desktop/finPlanFull/docs/ARCHITECTURE.md`
- `/Users/CSJ/Desktop/finPlanFull/docs/API_DOCUMENTATION.md`
- `/Users/CSJ/Desktop/finPlanFull/docs/DEVELOPER_DOCUMENTATION.md`
- `/Users/CSJ/Desktop/finPlanFull/docs/IHT_USER_GUIDE.md`
- `/Users/CSJ/Desktop/finPlanFull/features.md`
- `/Users/CSJ/Desktop/finPlanFull/frontend/.git/COMMIT_EDITMSG`

**Total Files Analyzed**: 65 files

### Code Patterns to Follow

#### Authentication Pattern (Correct)
```typescript
// Use centralized API helper
import { fetchJSON, postJSON, putJSON, deleteJSON } from '../../utils/api';

export async function getProducts(): Promise<Product[]> {
  return fetchJSON<Product[]>('/api/modules/protection/products');
}

export async function createProduct(product: ProductInput): Promise<Product> {
  return postJSON<Product>('/api/modules/protection/products', product);
}
```

#### Error Handling Pattern (Correct)
```typescript
try {
  const data = await fetchJSON('/api/endpoint');
  setData(data);
  setError(null);
} catch (error) {
  setError(error instanceof Error ? error.message : 'An error occurred');
  // Optionally log to error tracking service
  logger.error('Failed to fetch data', error);
}
```

#### Component API Call Pattern (Correct)
```typescript
function MyComponent() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchData() {
      try {
        setLoading(true);
        setError(null);

        const result = await fetchJSON('/api/endpoint', {
          signal: controller.signal
        });

        setData(result);
      } catch (error) {
        if (error.name !== 'AbortError') {
          setError(error.message);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchData();

    return () => controller.abort();
  }, []);

  if (loading) return <LoadingSkeleton />;
  if (error) return <ErrorMessage>{error}</ErrorMessage>;
  if (!data) return null;

  return <div>{/* Render data */}</div>;
}
```

### Code Patterns to Avoid

#### ❌ Direct localStorage Access
```typescript
// BAD - Don't do this
const token = localStorage.getItem('access_token');
fetch('/api/endpoint', {
  headers: { Authorization: `Bearer ${token}` }
});

// GOOD - Do this instead
import { fetchJSON } from '../../utils/api';
const data = await fetchJSON('/api/endpoint');
```

#### ❌ Axios in Components
```typescript
// BAD - Don't do this
import axios from 'axios';

function MyComponent() {
  useEffect(() => {
    axios.get('/api/endpoint').then(response => {
      setData(response.data);
    });
  }, []);
}

// GOOD - Do this instead
import { fetchJSON } from '../utils/api';

function MyComponent() {
  useEffect(() => {
    fetchJSON('/api/endpoint').then(data => {
      setData(data);
    });
  }, []);
}
```

#### ❌ Hardcoded API URLs
```typescript
// BAD - Don't do this
fetch('http://localhost:8000/api/endpoint');

// GOOD - Do this instead
import { fetchJSON } from '../../utils/api';
fetchJSON('/api/endpoint');  // URL automatically prepended
```

#### ❌ Inconsistent Error Handling
```typescript
// BAD - Different patterns everywhere
// Pattern 1:
.catch(err => console.error(err));

// Pattern 2:
.catch(err => setError(err.message || 'Error'));

// Pattern 3:
.catch(err => throw new Error(err.detail || 'Failed'));

// GOOD - Consistent pattern
.catch(err => {
  const message = extractErrorMessage(err, 'Operation failed');
  setError(message);
  logger.error('Operation failed', err);
});
```

#### ❌ No Request Cleanup
```typescript
// BAD - Request continues after unmount
useEffect(() => {
  fetch('/api/endpoint').then(data => setData(data));
}, []);

// GOOD - Request canceled on unmount
useEffect(() => {
  const controller = new AbortController();

  fetch('/api/endpoint', { signal: controller.signal })
    .then(data => setData(data))
    .catch(err => {
      if (err.name !== 'AbortError') {
        setError(err.message);
      }
    });

  return () => controller.abort();
}, []);
```

---

## Summary

This financial planning application has **4 critical authentication bugs** causing 401 errors:

1. **Dual HTTP client system** (axios + fetch) with separate auth state
2. **Incomplete migration** to centralized auth helpers (only 20% complete)
3. **Wrong token storage key** in ProtectionDashboard (breaks entire page)
4. **No token refresh mechanism** (users forced to re-login every 30 min)

Additionally, there are **19 high-priority issues** including security vulnerabilities, missing error handling, code quality concerns, and architectural inconsistencies.

**Recommended Approach**:
1. **Phase 1 (Week 1)**: Fix critical auth bugs (Tasks 1.1-1.5)
2. **Phase 2 (Week 2)**: Code quality & consistency (Tasks 2.1-2.8)
3. **Phase 3 (Week 3)**: Security improvements (Tasks 3.1-3.3)
4. **Phase 4 (Ongoing)**: Performance optimization (Tasks 4.1-4.4)

**Estimated Effort**:
- Critical fixes: 3-5 days
- High priority: 5-7 days
- Medium priority: 3-4 days
- Low priority: 2-3 days
- **Total**: 13-19 days

**Risk**: Medium - Critical bugs must be fixed before production deployment. Current authentication system is fragile and vulnerable to race conditions and security issues.

**Next Steps**:
1. Review this report with team
2. Prioritize tasks based on business needs
3. Create tickets in project management system
4. Assign tasks to developers
5. Set up automated testing and monitoring
6. Begin Phase 1 implementation

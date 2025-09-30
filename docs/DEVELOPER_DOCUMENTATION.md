# Developer Documentation

**Financial Planning Application - Developer Guide**

Version 1.0.0 | Last Updated: 2025-09-30

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Getting Started](#getting-started)
5. [Backend Development](#backend-development)
6. [Frontend Development](#frontend-development)
7. [Database Schema](#database-schema)
8. [API Development](#api-development)
9. [Testing](#testing)
10. [Deployment](#deployment)
11. [Contributing Guidelines](#contributing-guidelines)
12. [Code Standards](#code-standards)

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React 19.1.1 + TypeScript + Styled Components       │  │
│  │  - Component Library (Button, Card, Input, etc.)    │  │
│  │  - Pages (Dashboard, IHT, Pensions, etc.)           │  │
│  │  - Context (Auth, Theme)                            │  │
│  │  - Services (API calls, Auth management)            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI (Python 3.9+)                               │  │
│  │  - REST Endpoints (Auth, IHT, Pensions, etc.)      │  │
│  │  - JWT Authentication                               │  │
│  │  - Request Validation (Pydantic)                    │  │
│  │  - CORS Configuration                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓ SQLAlchemy ORM
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Services                                            │  │
│  │  - IHT Calculator (iht_calculator.py)               │  │
│  │  - Pension Calculator (pension_calculator.py)       │  │
│  │  - Monte Carlo (monte_carlo.py)                     │  │
│  │  - Tax Optimizer (tax_optimizer.py)                 │  │
│  │  - Portfolio Rebalancer (portfolio_rebalancer.py)   │  │
│  │  - Projection Engine (projection_engine.py)         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓ SQL Queries
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SQLite Database                                     │  │
│  │  - User data                                         │  │
│  │  - Financial statements                              │  │
│  │  - IHT profiles and gifts                           │  │
│  │  - Pension schemes                                   │  │
│  │  - Products (investments, protection)               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns

**Backend**:
- **Repository Pattern**: Database access abstraction
- **Service Layer**: Business logic separation
- **Dependency Injection**: FastAPI's built-in DI
- **Factory Pattern**: Database session creation
- **Strategy Pattern**: Tax calculation strategies

**Frontend**:
- **Component Composition**: Reusable UI components
- **Container/Presentational**: Separation of concerns
- **Context API**: Global state management
- **Custom Hooks**: Reusable logic
- **Render Props**: Component flexibility

---

## Technology Stack

### Backend

**Core Framework**:
- **FastAPI 0.104+**: Modern Python web framework
- **Python 3.9+**: Programming language
- **Uvicorn**: ASGI server

**Database**:
- **SQLAlchemy 2.0+**: ORM
- **SQLite**: Development database
- **Alembic**: Database migrations (future)

**Authentication**:
- **python-jose**: JWT tokens
- **passlib**: Password hashing
- **bcrypt**: Hashing algorithm

**Validation**:
- **Pydantic 2.0+**: Data validation
- **email-validator**: Email validation

**Development**:
- **pytest**: Testing framework
- **pytest-cov**: Code coverage
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking

### Frontend

**Core Framework**:
- **React 19.1.1**: UI library
- **TypeScript 5.0+**: Type-safe JavaScript
- **React Router 6**: Navigation

**Styling**:
- **Styled Components 6.0+**: CSS-in-JS
- **CSS Grid/Flexbox**: Layout

**Data Visualization**:
- **Recharts 2.8+**: Charts and graphs
- **React Icons**: Icon library

**State Management**:
- **React Context API**: Global state
- **React Hooks**: Local state

**Development**:
- **Create React App**: Build tooling
- **Jest**: Testing framework
- **React Testing Library**: Component testing
- **ESLint**: Linting
- **Prettier**: Code formatting

### DevOps

**Containerization**:
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Production web server

**CI/CD**:
- **GitHub Actions**: Automated workflows
- **pytest**: Backend tests
- **Jest**: Frontend tests
- **Docker builds**: Container creation

---

## Project Structure

```
finPlanFull/
├── backend/                      # Backend FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # Database connection
│   │   ├── api/                 # API endpoints
│   │   │   ├── auth/
│   │   │   │   ├── auth.py      # Authentication endpoints
│   │   │   │   └── models.py    # Auth schemas
│   │   │   ├── iht.py           # IHT calculator endpoints
│   │   │   ├── iht_refactored.py # Enhanced IHT endpoints
│   │   │   ├── financial.py     # Financial statements
│   │   │   ├── products.py      # Product management
│   │   │   ├── pension/         # Pension endpoints
│   │   │   │   ├── pension_uk.py
│   │   │   │   ├── pension_schemes.py
│   │   │   │   └── pension_optimization.py
│   │   │   ├── simulations.py   # Monte Carlo simulations
│   │   │   ├── projections.py   # Financial projections
│   │   │   ├── tax_optimization.py
│   │   │   ├── rebalancing.py
│   │   │   ├── chat.py          # AI chat endpoints
│   │   │   └── export.py        # Export endpoints
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── iht.py
│   │   │   ├── financial.py
│   │   │   ├── products.py
│   │   │   ├── pension.py
│   │   │   ├── chat.py
│   │   │   └── bank_account.py
│   │   └── services/            # Business logic
│   │       ├── iht_calculator.py
│   │       ├── monte_carlo.py
│   │       ├── tax_optimizer.py
│   │       ├── portfolio_rebalancer.py
│   │       └── projection_engine.py
│   ├── tests/                   # Backend tests
│   │   ├── test_auth.py
│   │   ├── test_iht.py
│   │   ├── test_iht_enhanced.py
│   │   ├── test_pension.py
│   │   ├── test_export.py
│   │   └── test_integration.py
│   ├── seed_data.py             # Database seeding
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Backend container
│   └── pytest.ini               # Pytest configuration
│
├── frontend/                    # Frontend React application
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── index.tsx            # React entry point
│   │   ├── App.tsx              # Main app component
│   │   ├── components/          # Reusable components
│   │   │   ├── common/          # Common UI components
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── LoadingSpinner.tsx
│   │   │   │   ├── Breadcrumb.tsx
│   │   │   │   └── ThemeToggle.tsx
│   │   │   ├── layout/          # Layout components
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── MobileNav.tsx
│   │   │   │   ├── Container.tsx
│   │   │   │   └── Grid.tsx
│   │   │   ├── iht/             # IHT components
│   │   │   │   ├── GiftTimelineVisualization.tsx
│   │   │   │   ├── EstatePlanningScenarios.tsx
│   │   │   │   ├── GiftHistoryManager.tsx
│   │   │   │   ├── TrustManager.tsx
│   │   │   │   ├── ExemptionTracker.tsx
│   │   │   │   ├── ValuationTools.tsx
│   │   │   │   ├── IHTCompliance.tsx
│   │   │   │   ├── MultipleMarriageTracker.tsx
│   │   │   │   ├── DownsizingAddition.tsx
│   │   │   │   ├── GiftWithReservationTracker.tsx
│   │   │   │   └── IHTDashboardWidget.tsx
│   │   │   └── pension/         # Pension components
│   │   │       ├── AnnualAllowanceGauge.tsx
│   │   │       ├── TaxReliefCalculator.tsx
│   │   │       ├── SchemeCard.tsx
│   │   │       └── PensionDashboardWidget.tsx
│   │   ├── pages/               # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── IHTCalculator.tsx
│   │   │   ├── IHTCalculatorEnhanced.tsx
│   │   │   ├── IHTCalculatorComplete.tsx
│   │   │   ├── IHTCompliance.tsx
│   │   │   ├── FinancialStatements.tsx
│   │   │   ├── RetirementPlanningUK.tsx
│   │   │   ├── PortfolioAnalytics.tsx
│   │   │   ├── ProductsOverview.tsx
│   │   │   ├── MonteCarloSimulation.tsx
│   │   │   ├── FinancialProjections.tsx
│   │   │   ├── TaxOptimization.tsx
│   │   │   ├── PortfolioRebalancing.tsx
│   │   │   ├── BankAccounts.tsx
│   │   │   └── Chat.tsx
│   │   ├── context/             # React context
│   │   │   ├── AuthContext.tsx
│   │   │   └── ThemeContext.tsx
│   │   ├── services/            # API services
│   │   │   └── auth.ts
│   │   ├── styles/              # Styling
│   │   │   ├── theme.ts
│   │   │   ├── GlobalStyles.ts
│   │   │   └── responsive.ts
│   │   ├── types/               # TypeScript types
│   │   │   └── styled.d.ts
│   │   └── __tests__/           # Frontend tests
│   │       ├── components/
│   │       └── services/
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── nginx.conf
│
├── docs/                        # Documentation
│   ├── README.md
│   ├── API_DOCUMENTATION.md
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_DOCUMENTATION.md
│   ├── ARCHITECTURE.md
│   ├── IHT_USER_GUIDE.md
│   ├── IHT_CALCULATION_METHODOLOGY.md
│   ├── IHT_COMPLIANCE_CHECKLIST.md
│   └── TESTING_FRAMEWORK.md
│
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI/CD
│
├── docker-compose.yml           # Docker orchestration
├── start.sh                     # Development startup script
├── CLAUDE.md                    # AI instructions
├── tasks.md                     # Task tracking
├── iht.md                       # IHT specification
├── pensionacc.md                # Pension specification
└── README.md                    # Project README
```

---

## Getting Started

### Prerequisites

**Required**:
- Python 3.9 or higher
- Node.js 16 or higher
- npm or yarn
- Git

**Optional**:
- Docker & Docker Compose
- PostgreSQL (for production)

### Initial Setup

1. **Clone the Repository**:
```bash
git clone <repository-url>
cd finPlanFull
```

2. **Backend Setup**:
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./financial_planning.db
OPENAI_API_KEY=your-openai-key-optional
EOF

# Initialize database and seed data
python seed_data.py
```

3. **Frontend Setup**:
```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file (optional)
cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000
EOF
```

4. **Start Development Servers**:
```bash
# From project root
./start.sh

# Or manually:
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm start
```

5. **Access Application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker Setup

```bash
# Build and start all services
docker-compose up --build

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

---

## Backend Development

### Creating New API Endpoints

**1. Define Pydantic Models** (`app/api/<module>/models.py`):
```python
from pydantic import BaseModel, Field
from typing import Optional

class CalculationRequest(BaseModel):
    value: float = Field(..., gt=0, description="Value must be positive")
    option: Optional[str] = None

class CalculationResponse(BaseModel):
    result: float
    details: dict
```

**2. Create Endpoint** (`app/api/<module>/routes.py`):
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.auth.auth import get_current_user
from .models import CalculationRequest, CalculationResponse

router = APIRouter()

@router.post("/calculate", response_model=CalculationResponse)
async def calculate(
    request: CalculationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate something.

    - **value**: Input value
    - **option**: Optional parameter
    """
    try:
        # Your logic here
        result = request.value * 2

        return CalculationResponse(
            result=result,
            details={"message": "Success"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**3. Register Router** (`app/main.py`):
```python
from app.api.<module>.routes import router as module_router

app.include_router(module_router, prefix="/api/module", tags=["Module"])
```

### Creating Database Models

**1. Define Model** (`app/models/<model>.py`):
```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class MyModel(Base):
    __tablename__ = "my_models"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    value = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="my_models")
```

**2. Update User Model** (`app/models/user.py`):
```python
class User(Base):
    # ... existing fields ...

    # Add relationship
    my_models = relationship("MyModel", back_populates="user")
```

**3. Create Tables**:
```python
# In app/database.py or seed script
from app.models.<model> import MyModel

Base.metadata.create_all(bind=engine)
```

### Creating Services

**Structure** (`app/services/my_service.py`):
```python
from typing import List, Dict, Optional
from datetime import datetime, date

class MyService:
    """
    Service for business logic.
    """

    def __init__(self):
        self.config = {}

    def calculate_something(
        self,
        input_value: float,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Perform calculation.

        Args:
            input_value: The input value
            options: Optional configuration

        Returns:
            Dictionary with results
        """
        # Business logic here
        result = input_value * 2

        return {
            "result": result,
            "timestamp": datetime.utcnow(),
            "status": "success"
        }

    def _private_helper(self, value: float) -> float:
        """Private helper method."""
        return value * 1.5
```

### Error Handling

**Custom Exceptions**:
```python
from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ValidationException(HTTPException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

# Usage
if not resource:
    raise NotFoundException(detail=f"Item {id} not found")
```

**Global Exception Handler**:
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )
```

### Authentication

**Protected Endpoints**:
```python
from app.api.auth.auth import get_current_user
from app.models.user import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}
```

**Optional Authentication**:
```python
from typing import Optional

async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    if not token:
        return None
    return await get_current_user(token)
```

---

## Frontend Development

### Creating Components

**Functional Component with TypeScript**:
```typescript
import React from 'react';
import styled from 'styled-components';

interface MyComponentProps {
  title: string;
  value: number;
  onUpdate?: (newValue: number) => void;
  optional?: boolean;
}

const MyComponent: React.FC<MyComponentProps> = ({
  title,
  value,
  onUpdate,
  optional = false
}) => {
  const [localValue, setLocalValue] = React.useState(value);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(e.target.value);
    setLocalValue(newValue);
    onUpdate?.(newValue);
  };

  return (
    <Container>
      <Title>{title}</Title>
      <Input
        type="number"
        value={localValue}
        onChange={handleChange}
      />
      {optional && <OptionalText>Optional</OptionalText>}
    </Container>
  );
};

const Container = styled.div`
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.background};
  border-radius: 8px;
`;

const Title = styled.h3`
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const Input = styled.input`
  width: 100%;
  padding: ${props => props.theme.spacing.sm};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 4px;
`;

const OptionalText = styled.span`
  color: ${props => props.theme.colors.textSecondary};
  font-size: ${props => props.theme.typography.fontSizeSmall};
`;

export default MyComponent;
```

### Custom Hooks

**Example Hook** (`src/hooks/useMyHook.ts`):
```typescript
import { useState, useEffect } from 'react';

interface UseMyHookOptions {
  initialValue?: number;
  autoUpdate?: boolean;
}

const useMyHook = (options: UseMyHookOptions = {}) => {
  const [value, setValue] = useState(options.initialValue || 0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (options.autoUpdate) {
      // Auto-update logic
      const interval = setInterval(() => {
        setValue(prev => prev + 1);
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [options.autoUpdate]);

  const update = async (newValue: number) => {
    setLoading(true);
    setError(null);

    try {
      // API call or logic
      setValue(newValue);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return {
    value,
    loading,
    error,
    update
  };
};

export default useMyHook;
```

### API Integration

**Service Pattern** (`src/services/myService.ts`):
```typescript
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface MyRequest {
  value: number;
  option?: string;
}

interface MyResponse {
  result: number;
  details: Record<string, any>;
}

class MyService {
  private getAuthHeader() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async calculate(request: MyRequest): Promise<MyResponse> {
    try {
      const response = await axios.post(
        `${API_URL}/api/module/calculate`,
        request,
        { headers: this.getAuthHeader() }
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Request failed');
      }
      throw error;
    }
  }

  async get(id: number): Promise<MyResponse> {
    const response = await axios.get(
      `${API_URL}/api/module/${id}`,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }
}

export default new MyService();
```

**Using in Component**:
```typescript
import React, { useState, useEffect } from 'react';
import myService from '../services/myService';

const MyPage: React.FC = () => {
  const [data, setData] = useState<MyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCalculate = async (value: number) => {
    setLoading(true);
    setError(null);

    try {
      const result = await myService.calculate({ value });
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <button onClick={() => handleCalculate(100)}>Calculate</button>
      {data && <div>Result: {data.result}</div>}
    </div>
  );
};
```

### State Management

**Context Pattern**:
```typescript
// src/context/MyContext.tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface MyContextValue {
  state: number;
  updateState: (value: number) => void;
}

const MyContext = createContext<MyContextValue | undefined>(undefined);

export const MyProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, setState] = useState(0);

  const updateState = (value: number) => {
    setState(value);
  };

  return (
    <MyContext.Provider value={{ state, updateState }}>
      {children}
    </MyContext.Provider>
  );
};

export const useMyContext = () => {
  const context = useContext(MyContext);
  if (!context) {
    throw new Error('useMyContext must be used within MyProvider');
  }
  return context;
};
```

### Styling

**Theme Usage**:
```typescript
import styled from 'styled-components';

const StyledComponent = styled.div`
  /* Access theme */
  color: ${props => props.theme.colors.primary};
  padding: ${props => props.theme.spacing.md};
  font-size: ${props => props.theme.typography.fontSize};

  /* Responsive */
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    padding: ${props => props.theme.spacing.sm};
  }

  /* Hover state */
  &:hover {
    background: ${props => props.theme.colors.primaryLight};
  }
`;
```

**Transient Props** (avoid passing to DOM):
```typescript
interface StyledProps {
  $variant: 'primary' | 'secondary';
  $size: 'small' | 'large';
}

const Button = styled.button<StyledProps>`
  background: ${props => props.$variant === 'primary'
    ? props.theme.colors.primary
    : props.theme.colors.secondary};
  padding: ${props => props.$size === 'large'
    ? props.theme.spacing.lg
    : props.theme.spacing.sm};
`;

// Usage - $ prefix prevents passing to DOM
<Button $variant="primary" $size="large">Click</Button>
```

---

## Database Schema

### Core Tables

**users**:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    risk_tolerance VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**iht_profiles**:
```sql
CREATE TABLE iht_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    estate_value FLOAT NOT NULL,
    property_value FLOAT,
    spouse_nrb_used FLOAT DEFAULT 0,
    charitable_donation FLOAT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**gifts**:
```sql
CREATE TABLE gifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    iht_profile_id INTEGER,
    amount FLOAT NOT NULL,
    gift_date DATE NOT NULL,
    recipient_relationship VARCHAR,
    gift_type VARCHAR DEFAULT 'PET',
    exemptions_used TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (iht_profile_id) REFERENCES iht_profiles(id)
);
```

**enhanced_pensions**:
```sql
CREATE TABLE enhanced_pensions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    provider VARCHAR,
    scheme_type VARCHAR NOT NULL,
    current_value FLOAT DEFAULT 0,
    annual_contribution FLOAT DEFAULT 0,
    employer_match_percentage FLOAT DEFAULT 0,
    relief_method VARCHAR DEFAULT 'relief_at_source',
    mpaa_triggered BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Relationships

```
users (1) ──→ (N) iht_profiles
users (1) ──→ (N) gifts
users (1) ──→ (N) enhanced_pensions
users (1) ──→ (N) products
users (1) ──→ (N) balance_sheets
users (1) ──→ (N) profit_loss_statements
users (1) ──→ (N) bank_accounts
users (1) ──→ (N) chat_messages

iht_profiles (1) ──→ (N) gifts
bank_accounts (1) ──→ (N) transactions
```

---

## API Development

### Best Practices

**1. Use Pydantic for Validation**:
```python
from pydantic import BaseModel, Field, validator

class MyModel(BaseModel):
    value: float = Field(..., gt=0, description="Must be positive")

    @validator('value')
    def validate_value(cls, v):
        if v > 1000000:
            raise ValueError('Value too large')
        return v
```

**2. Return Proper HTTP Status Codes**:
```python
from fastapi import status

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(...):
    ...

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(...):
    ...
```

**3. Use Response Models**:
```python
@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    return item  # Pydantic handles serialization
```

**4. Document Endpoints**:
```python
@router.post(
    "/calculate",
    response_model=CalculationResponse,
    summary="Calculate IHT",
    description="Comprehensive IHT calculation with UK tax rules",
    response_description="IHT calculation results with breakdown"
)
async def calculate_iht(...):
    """
    Calculate Inheritance Tax:

    - **estate_value**: Total estate value
    - **gifts**: List of gifts in last 7 years
    - Returns: Complete IHT calculation
    """
    ...
```

**5. Handle Database Sessions**:
```python
from app.database import get_db
from sqlalchemy.orm import Session

@router.get("/items")
async def get_items(db: Session = Depends(get_db)):
    try:
        items = db.query(Item).all()
        return items
    finally:
        db.close()
```

---

## Testing

### Backend Testing

**Unit Test Example** (`tests/test_my_service.py`):
```python
import pytest
from app.services.my_service import MyService

class TestMyService:
    def setup_method(self):
        self.service = MyService()

    def test_calculate_positive_value(self):
        result = self.service.calculate_something(100)
        assert result["result"] == 200
        assert result["status"] == "success"

    def test_calculate_zero_value(self):
        with pytest.raises(ValueError):
            self.service.calculate_something(0)

    @pytest.mark.parametrize("input,expected", [
        (10, 20),
        (50, 100),
        (100, 200)
    ])
    def test_multiple_values(self, input, expected):
        result = self.service.calculate_something(input)
        assert result["result"] == expected
```

**API Test Example** (`tests/test_api.py`):
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():
    response = client.post(
        "/api/auth/token",
        data={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_endpoint():
    # Login first
    login_response = client.post(
        "/api/auth/token",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/api/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

**Running Tests**:
```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_my_service.py

# Run with coverage
pytest --cov=app tests/

# Run verbose
pytest -v

# Run specific test
pytest tests/test_my_service.py::TestMyService::test_calculate_positive_value
```

### Frontend Testing

**Component Test** (`src/__tests__/components/MyComponent.test.tsx`):
```typescript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import MyComponent from '../../components/MyComponent';

describe('MyComponent', () => {
  it('renders with title', () => {
    render(<MyComponent title="Test" value={100} />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('calls onUpdate when value changes', () => {
    const handleUpdate = jest.fn();
    render(
      <MyComponent
        title="Test"
        value={100}
        onUpdate={handleUpdate}
      />
    );

    const input = screen.getByRole('spinbutton');
    fireEvent.change(input, { target: { value: '200' } });

    expect(handleUpdate).toHaveBeenCalledWith(200);
  });
});
```

**Service Test** (`src/__tests__/services/myService.test.ts`):
```typescript
import myService from '../../services/myService';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('MyService', () => {
  it('calculates successfully', async () => {
    mockedAxios.post.mockResolvedValue({
      data: { result: 200, details: {} }
    });

    const result = await myService.calculate({ value: 100 });

    expect(result.result).toBe(200);
    expect(mockedAxios.post).toHaveBeenCalledWith(
      expect.stringContaining('/calculate'),
      { value: 100 },
      expect.any(Object)
    );
  });
});
```

**Running Tests**:
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific file
npm test MyComponent.test.tsx

# Run in watch mode
npm test -- --watch
```

---

## Deployment

### Production Build

**Backend**:
```bash
# Install production dependencies only
pip install --no-dev -r requirements.txt

# Run with gunicorn (production ASGI server)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Frontend**:
```bash
# Build for production
npm run build

# Output in build/ directory
# Serve with nginx or static hosting
```

### Docker Deployment

**Build Images**:
```bash
# Build backend
docker build -t finplan-backend ./backend

# Build frontend
docker build -t finplan-frontend ./frontend

# Or use docker-compose
docker-compose build
```

**Run Containers**:
```bash
docker-compose up -d
```

### Environment Variables

**Backend** (`.env`):
```bash
SECRET_KEY=<long-random-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql://user:pass@host:5432/dbname
OPENAI_API_KEY=<your-key>
CORS_ORIGINS=https://yourdomain.com
```

**Frontend** (`.env.production`):
```bash
REACT_APP_API_URL=https://api.yourdomain.com
```

### Database Migration

**For Production with PostgreSQL**:
```bash
# Install alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

---

## Contributing Guidelines

### Git Workflow

**1. Create Feature Branch**:
```bash
git checkout -b feature/my-feature
```

**2. Make Changes**:
```bash
# Make your changes
git add .
git commit -m "feat: add my feature"
```

**3. Push and Create PR**:
```bash
git push origin feature/my-feature
# Create pull request on GitHub
```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples**:
```
feat(iht): add trust manager component
fix(pension): correct AA taper calculation
docs(api): update endpoint documentation
refactor(services): simplify tax optimizer
test(iht): add taper relief tests
```

### Code Review Checklist

- [ ] Code follows style guide
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation updated
- [ ] No console errors
- [ ] TypeScript compiles without errors
- [ ] Backend imports work
- [ ] Commits are atomic and well-described

---

## Code Standards

### Python (Backend)

**Style Guide**: PEP 8

**Formatting**:
```bash
# Format with black
black app/

# Lint with flake8
flake8 app/

# Type check with mypy
mypy app/
```

**Code Example**:
```python
from typing import List, Optional, Dict
from datetime import datetime


class MyClass:
    """
    Class docstring.

    Attributes:
        value: Description of value
    """

    def __init__(self, value: float):
        self.value = value

    def calculate(
        self,
        input_data: List[float],
        options: Optional[Dict] = None
    ) -> float:
        """
        Calculate something.

        Args:
            input_data: List of input values
            options: Optional configuration

        Returns:
            Calculated result

        Raises:
            ValueError: If input_data is empty
        """
        if not input_data:
            raise ValueError("input_data cannot be empty")

        return sum(input_data) * self.value
```

### TypeScript (Frontend)

**Style Guide**: Airbnb React/TypeScript

**Formatting**:
```bash
# Format with prettier
npm run format

# Lint with ESLint
npm run lint

# Type check
npm run type-check
```

**Code Example**:
```typescript
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

/**
 * Component description.
 */
interface MyComponentProps {
  /** Title to display */
  title: string;
  /** Current value */
  value: number;
  /** Callback when value changes */
  onUpdate?: (value: number) => void;
}

/**
 * MyComponent renders a form with calculations.
 */
const MyComponent: React.FC<MyComponentProps> = ({
  title,
  value,
  onUpdate
}) => {
  const [localValue, setLocalValue] = useState<number>(value);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const newValue = parseFloat(e.target.value);
    setLocalValue(newValue);
    onUpdate?.(newValue);
  };

  return (
    <Container>
      <Title>{title}</Title>
      <Input
        type="number"
        value={localValue}
        onChange={handleChange}
      />
    </Container>
  );
};

const Container = styled.div`
  padding: 16px;
`;

const Title = styled.h3`
  margin-bottom: 8px;
`;

const Input = styled.input`
  width: 100%;
`;

export default MyComponent;
```

---

## Useful Commands

### Backend

```bash
# Start development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Format code
black app/

# Lint code
flake8 app/

# Type check
mypy app/

# Create database
python seed_data.py

# Python shell with app context
python -i -c "from app.main import app; from app.database import SessionLocal; db = SessionLocal()"
```

### Frontend

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

### Docker

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild specific service
docker-compose build backend

# Run command in container
docker-compose exec backend python seed_data.py
```

---

## Resources

**FastAPI**:
- Docs: https://fastapi.tiangolo.com/
- Tutorial: https://fastapi.tiangolo.com/tutorial/

**React**:
- Docs: https://react.dev/
- TypeScript: https://www.typescriptlang.org/docs/

**SQLAlchemy**:
- Docs: https://docs.sqlalchemy.org/
- Tutorial: https://docs.sqlalchemy.org/en/20/tutorial/

**Testing**:
- pytest: https://docs.pytest.org/
- Jest: https://jestjs.io/docs/getting-started
- React Testing Library: https://testing-library.com/react

---

*Last Updated: 2025-09-30*
*Version: 1.0.0*
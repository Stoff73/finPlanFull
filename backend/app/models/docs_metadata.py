"""
Documentation metadata for Learning Centre.

This module defines metadata for all documentation files including:
- Title, category, description
- Tags for search and filtering
- Related documents (cross-references)
- Version information
"""

from typing import List, Optional
from datetime import datetime

class DocMetadata:
    """Metadata structure for a documentation file."""

    def __init__(
        self,
        name: str,
        title: str,
        category: str,
        description: str,
        tags: List[str],
        related: Optional[List[str]] = None,
        version: str = "1.0",
        icon: str = "📄"
    ):
        self.name = name
        self.title = title
        self.category = category
        self.description = description
        self.tags = tags
        self.related = related or []
        self.version = version
        self.icon = icon


# Documentation categories
CATEGORIES = {
    "getting_started": {
        "name": "Getting Started",
        "icon": "📘",
        "description": "New user guides and setup instructions"
    },
    "iht_planning": {
        "name": "IHT Planning",
        "icon": "💰",
        "description": "Inheritance tax guides and compliance"
    },
    "pension_planning": {
        "name": "Pension Planning",
        "icon": "🏦",
        "description": "UK pension features and calculations"
    },
    "financial_management": {
        "name": "Financial Management",
        "icon": "📊",
        "description": "Balance sheets, P&L, cash flow"
    },
    "tax_optimization": {
        "name": "Tax Optimization",
        "icon": "🎯",
        "description": "Tax planning and optimization guides"
    },
    "developer_resources": {
        "name": "Developer Resources",
        "icon": "👨‍💻",
        "description": "API, architecture, development guides"
    },
    "compliance": {
        "name": "Compliance",
        "icon": "📋",
        "description": "HMRC forms, checklists, compliance tools"
    },
    "video_tutorials": {
        "name": "Video Tutorials",
        "icon": "🎥",
        "description": "27 video scripts across 6 series (~160 minutes)"
    },
    "help_support": {
        "name": "Help & Support",
        "icon": "❓",
        "description": "FAQ, troubleshooting, contact support"
    }
}


# Metadata for all documentation files
DOCS_METADATA = {
    "USER_GUIDE.md": DocMetadata(
        name="USER_GUIDE.md",
        title="User Guide",
        category="getting_started",
        description="Complete user guide covering all features: Dashboard, IHT Calculator, Pension Planning, Financial Statements, Tax Optimization, Portfolio Management, AI Chat Assistant, and Settings.",
        tags=["user guide", "getting started", "features", "dashboard", "iht", "pensions", "financial statements", "portfolio", "chat"],
        related=["IHT_USER_GUIDE.md", "VIDEO_TUTORIALS.md", "API_DOCUMENTATION.md"],
        icon="📘"
    ),

    "IHT_USER_GUIDE.md": DocMetadata(
        name="IHT_USER_GUIDE.md",
        title="IHT Calculator User Guide",
        category="iht_planning",
        description="Comprehensive guide to using the UK Inheritance Tax Calculator including asset management, gift tracking, trust management, and tax optimization strategies.",
        tags=["iht", "inheritance tax", "calculator", "estates", "gifts", "trusts", "nil-rate band", "taper relief"],
        related=["IHT_CALCULATION_METHODOLOGY.md", "IHT_COMPLIANCE_CHECKLIST.md", "USER_GUIDE.md"],
        icon="💰"
    ),

    "IHT_CALCULATION_METHODOLOGY.md": DocMetadata(
        name="IHT_CALCULATION_METHODOLOGY.md",
        title="IHT Calculation Methodology",
        category="iht_planning",
        description="Technical documentation of UK IHT calculation methods including nil-rate bands, residence nil-rate band (RNRB), taper relief, business/agricultural property relief, and trust charges.",
        tags=["iht", "calculations", "methodology", "nil-rate band", "rnrb", "taper relief", "bpr", "apr", "trusts", "tax year 2024/25"],
        related=["IHT_USER_GUIDE.md", "IHT_COMPLIANCE_CHECKLIST.md"],
        icon="💰"
    ),

    "IHT_COMPLIANCE_CHECKLIST.md": DocMetadata(
        name="IHT_COMPLIANCE_CHECKLIST.md",
        title="IHT Compliance Checklist",
        category="compliance",
        description="Complete IHT400 compliance checklist with HMRC form guidance, payment calculations, deadline tracking, and required documentation for inheritance tax returns.",
        tags=["iht", "compliance", "iht400", "hmrc", "forms", "checklist", "deadlines", "documentation"],
        related=["IHT_USER_GUIDE.md", "IHT_CALCULATION_METHODOLOGY.md"],
        icon="📋"
    ),

    "VIDEO_TUTORIALS.md": DocMetadata(
        name="VIDEO_TUTORIALS.md",
        title="Video Tutorials",
        category="video_tutorials",
        description="Collection of 27 video tutorial scripts organized into 6 series: Getting Started (4 videos), IHT Calculator (6 videos), Pension Planning (5 videos), Financial Management (4 videos), Advanced Features (5 videos), and Tips & Tricks (3 videos). Total duration approximately 160 minutes.",
        tags=["video tutorials", "training", "getting started", "iht", "pensions", "financial statements", "advanced features", "tips"],
        related=["USER_GUIDE.md", "IHT_USER_GUIDE.md"],
        icon="🎥"
    ),

    "API_DOCUMENTATION.md": DocMetadata(
        name="API_DOCUMENTATION.md",
        title="API Documentation",
        category="developer_resources",
        description="Complete REST API reference including authentication, IHT calculations, financial statements, products, pensions, banking, chat, export, and simulations endpoints with request/response examples.",
        tags=["api", "rest", "endpoints", "authentication", "development", "integration", "swagger"],
        related=["ARCHITECTURE.md", "DEVELOPER_DOCUMENTATION.md"],
        icon="👨‍💻"
    ),

    "ARCHITECTURE.md": DocMetadata(
        name="ARCHITECTURE.md",
        title="System Architecture",
        category="developer_resources",
        description="System architecture documentation covering backend (FastAPI), frontend (React/TypeScript), database (SQLAlchemy ORM), authentication (JWT), deployment (Docker), and architectural patterns.",
        tags=["architecture", "system design", "fastapi", "react", "typescript", "database", "deployment", "development"],
        related=["API_DOCUMENTATION.md", "DEVELOPER_DOCUMENTATION.md"],
        icon="👨‍💻"
    ),

    "DEVELOPER_DOCUMENTATION.md": DocMetadata(
        name="DEVELOPER_DOCUMENTATION.md",
        title="Developer Documentation",
        category="developer_resources",
        description="Developer guide covering setup, development workflow, testing, code style, database management, troubleshooting, and contribution guidelines.",
        tags=["development", "setup", "testing", "coding standards", "git", "contribution", "troubleshooting"],
        related=["ARCHITECTURE.md", "API_DOCUMENTATION.md"],
        icon="👨‍💻"
    ),

    "README.md": DocMetadata(
        name="README.md",
        title="Getting Started - README",
        category="getting_started",
        description="Project overview, quick start guide, features summary, installation instructions, and links to comprehensive documentation.",
        tags=["readme", "overview", "quick start", "installation", "features", "getting started"],
        related=["USER_GUIDE.md", "DEVELOPER_DOCUMENTATION.md"],
        icon="📘"
    )
}


def get_doc_metadata(doc_name: str) -> Optional[DocMetadata]:
    """Get metadata for a specific document."""
    return DOCS_METADATA.get(doc_name)


def get_all_docs_metadata() -> List[DocMetadata]:
    """Get metadata for all documents."""
    return list(DOCS_METADATA.values())


def get_docs_by_category(category: str) -> List[DocMetadata]:
    """Get all documents in a specific category."""
    return [doc for doc in DOCS_METADATA.values() if doc.category == category]


def search_docs_metadata(query: str) -> List[DocMetadata]:
    """Search documents by title, description, or tags."""
    query_lower = query.lower()
    results = []

    for doc in DOCS_METADATA.values():
        # Search in title
        if query_lower in doc.title.lower():
            results.append(doc)
            continue

        # Search in description
        if query_lower in doc.description.lower():
            results.append(doc)
            continue

        # Search in tags
        if any(query_lower in tag.lower() for tag in doc.tags):
            results.append(doc)
            continue

    return results
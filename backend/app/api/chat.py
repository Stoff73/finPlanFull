from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import openai
from pydantic import BaseModel

from app.database import get_db
from app.models.chat import ChatMessage, ChatSession
from app.models.user import User
from app.api.auth.auth import get_current_user
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

# Configure OpenAI
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY

# Request/Response models
class ChatMessageCreate(BaseModel):
    content: str
    session_id: Optional[int] = None

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    intent: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class ChatSessionResponse(BaseModel):
    id: int
    session_title: Optional[str] = None
    total_messages: int
    created_at: datetime
    is_active: bool

    class Config:
        orm_mode = True

class ExtractedData(BaseModel):
    income: Optional[dict] = None
    expenses: Optional[dict] = None
    assets: Optional[dict] = None
    goals: Optional[List[dict]] = None
    questions: Optional[List[str]] = None

# Helper functions
def classify_intent(message: str) -> tuple[str, float]:
    """Classify the intent of a user message"""
    message_lower = message.lower()

    if any(word in message_lower for word in ['iht', 'inheritance', 'estate', 'tax']):
        return 'iht_query', 0.9
    elif any(word in message_lower for word in ['balance sheet', 'profit', 'loss', 'cash flow', 'income statement']):
        return 'financial_statement', 0.9
    elif any(word in message_lower for word in ['pension', 'retirement', 'retire']):
        return 'retirement_planning', 0.85
    elif any(word in message_lower for word in ['invest', 'portfolio', 'stocks', 'shares', 'isa']):
        return 'investment_advice', 0.85
    elif any(word in message_lower for word in ['save', 'savings', 'budget']):
        return 'savings_advice', 0.8
    elif any(word in message_lower for word in ['protect', 'insurance', 'life cover']):
        return 'protection_advice', 0.8
    else:
        return 'general_advice', 0.7

def extract_financial_data(message: str) -> dict:
    """Extract financial data from user message"""
    extracted = {
        'income': {},
        'expenses': {},
        'assets': {},
        'goals': [],
        'questions': []
    }

    # Simple extraction logic - in production, use NLP or OpenAI function calling
    lines = message.split('\n')
    for line in lines:
        line_lower = line.lower()
        # Check for income mentions
        if 'salary' in line_lower or 'income' in line_lower:
            # Try to extract amounts
            import re
            amounts = re.findall(r'£?(\d+(?:,\d{3})*(?:\.\d{2})?)', line)
            if amounts:
                extracted['income']['mentioned'] = amounts[0].replace(',', '')

        # Check for questions
        if '?' in line:
            extracted['questions'].append(line.strip())

    return extracted

async def generate_ai_response(user_message: str, intent: str, context: dict = None) -> str:
    """Generate AI response using OpenAI API"""
    if not settings.OPENAI_API_KEY:
        # Fallback response when OpenAI is not configured
        responses = {
            'iht_query': "I can help you with inheritance tax planning. Based on current UK rates, the nil-rate band is £325,000 and the residence nil-rate band is £175,000. Would you like me to calculate your potential IHT liability?",
            'financial_statement': "I can help you understand your financial statements. Your balance sheet shows your assets and liabilities, while your P&L shows income and expenses. What specific aspect would you like to explore?",
            'retirement_planning': "Let me help you with retirement planning. Consider factors like your target retirement age, expected expenses, and current pension contributions. What's your retirement goal?",
            'investment_advice': "I can provide guidance on investments. Remember to consider your risk tolerance, time horizon, and diversification. What are your investment objectives?",
            'protection_advice': "Protection planning is important for financial security. Life insurance and critical illness cover can protect your family. What concerns do you have?",
            'general_advice': "I'm here to help with your financial planning needs. I can assist with tax planning, investments, retirement, and more. What would you like to discuss?"
        }
        return responses.get(intent, responses['general_advice'])

    try:
        # Build system prompt based on intent
        system_prompts = {
            'iht_query': "You are a UK inheritance tax planning expert. Provide accurate, helpful advice based on current UK IHT rules and rates.",
            'financial_statement': "You are a financial analyst helping users understand their personal financial statements.",
            'retirement_planning': "You are a retirement planning advisor helping users plan for their retirement.",
            'investment_advice': "You are an investment advisor providing balanced, risk-aware investment guidance.",
            'general_advice': "You are a comprehensive financial planning assistant."
        }

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompts.get(intent, system_prompts['general_advice'])},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        # Fallback to simple response
        return "I understand you need help with financial planning. While I'm having trouble connecting to my AI service, I can still help you navigate the application features."

# API Endpoints
@router.post("/send", response_model=ChatMessageResponse)
async def send_message(
    message: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a chat message and get AI response"""

    # Get or create session
    if message.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == message.session_id,
            ChatSession.user_id == current_user.id,
            ChatSession.is_active == True
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        # Create new session
        session = ChatSession(
            user_id=current_user.id,
            session_title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            total_messages=0,
            total_tokens=0
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # Classify intent
    intent, confidence = classify_intent(message.content)

    # Extract financial data
    extracted_data = extract_financial_data(message.content)

    # Save user message
    user_msg = ChatMessage(
        user_id=current_user.id,
        role="user",
        content=message.content,
        intent=intent,
        confidence_score=confidence,
        extracted_data=extracted_data,
        is_processed=True
    )
    db.add(user_msg)

    # Generate AI response
    ai_response_content = await generate_ai_response(
        message.content,
        intent,
        context=session.context
    )

    # Save AI response
    ai_msg = ChatMessage(
        user_id=current_user.id,
        role="assistant",
        content=ai_response_content,
        intent=intent,
        is_processed=True
    )
    db.add(ai_msg)

    # Update session
    session.total_messages += 2
    session.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(ai_msg)

    return ai_msg

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get user's chat sessions"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.created_at.desc()).limit(limit).all()

    return sessions

@router.get("/messages/{session_id}", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a specific session"""
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id,
        ChatMessage.created_at >= session.created_at
    ).order_by(ChatMessage.created_at).all()

    return messages

@router.delete("/sessions/{session_id}")
async def close_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Close a chat session"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.is_active = False
    session.closed_at = datetime.utcnow()
    db.commit()

    return {"message": "Session closed successfully"}

@router.get("/extract/{message_id}")
async def get_extracted_data(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get extracted financial data from a message"""
    message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.user_id == current_user.id
    ).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return {
        "message_id": message.id,
        "intent": message.intent,
        "confidence": message.confidence_score,
        "extracted_data": message.extracted_data
    }
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

class TicketCategory(Enum):
    TECHNICAL = "technical"
    BILLING = "billing"
    FEATURE = "feature"
    ACCESS = "access"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class SupportTicket:
    id: str
    subject: str
    content: str
    customer_info: Dict[str, Any]

@dataclass
class TicketAnalysis:
    category : TicketCategory
    priority : Priority
    key_points : List[str]
    required_expertise : List[str]
    suggested_response_type : str

@dataclass
class ResponseSuggestion:
    response_text : str
    confidence_score : float
    requires_approval : bool
    suggested_actions : List[str]

@dataclass
class TicketResolution:
    ticket_id: str
    response_text: str
    status: str  # "completed", "needs_approval", "failed"
    error: Optional[str]
    analysis: Optional[Any]
    response: Optional[Any]
    context_snapshot: Dict[str, Any]
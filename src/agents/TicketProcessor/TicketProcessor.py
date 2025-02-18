from src.models import SupportTicket, TicketResolution

from TicketAnalysisAgent import TicketAnalysisAgent
from ResponseAgent import ResponseAgent

class TicketProcessor:
    def __init__(self):
        self.analysis_agent = TicketAnalysisAgent()
        self.response_agent = ResponseAgent()
        self.context = {}

    async def process_ticket(
        self,
        ticket: SupportTicket,
    ) -> TicketResolution:
        """
        Implement:
        1. Workflow Management:
           - Sequential processing
           - Context maintenance
           - Response validation
        
        2. Error Handling:
           - Invalid inputs
           - API failures
           - Response quality issues
        """
        pass

import asyncio
from dataclasses import dataclass
from typing import Dict, Any, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SupportTicket:
    id: str
    subject: str
    content: str
    customer_info: Dict[str, Any]

@dataclass
class TicketResolution:
    ticket_id: str
    response_text: str
    status: str  # "completed", "needs_approval", "failed"
    error: Optional[str]
    analysis: Optional[Any]
    response: Optional[Any]
    context_snapshot: Dict[str, Any]

class TicketProcessor:
    def __init__(self, max_retries: int = 3):
        self.analysis_agent = TicketAnalysisAgent()
        self.response_agent = ResponseAgent()
        self.context = {
            "customer_history": {},
            "system_state": {
                "last_processed": None,
                "consecutive_failures": 0
            }
        }
        self.max_retries = max_retries

    async def process_ticket(
        self,
        ticket: SupportTicket
    ) -> TicketResolution:
        resolution = TicketResolution(
            ticket_id=ticket.id,
            response_text="",
            status="failed",
            error=None,
            analysis=None,
            response=None,
            context_snapshot=self.context.copy()
        )

        try:
            # Validate input
            self._validate_ticket(ticket)

            # Update context
            self._update_context(ticket)

            # Analysis phase with retries
            analysis = await self._retry_analysis(ticket)
            resolution.analysis = analysis

            # Response generation
            response = await self._generate_response(analysis, ticket)
            resolution.response = response

            # Validate response
            self._validate_response(response)

            # Finalize
            resolution.response_text = response.response_text
            resolution.status = "needs_approval" if response.requires_approval else "completed"
            self._update_system_state(success=True)

        except Exception as e:
            logger.error(f"Processing failed for {ticket.id}: {str(e)}")
            resolution.error = str(e)
            self._update_system_state(success=False)
            return resolution

        return resolution

    def _validate_ticket(self, ticket: SupportTicket):
        """Ensure required ticket fields exist"""
        if not ticket.content.strip():
            raise ValueError("Empty ticket content")
        if not isinstance(ticket.customer_info, dict):
            raise TypeError("Invalid customer info format")

    def _update_context(self, ticket: SupportTicket):
        """Maintain customer history and system state"""
        customer_id = ticket.customer_info.get("customer_id")
        if customer_id:
            self.context["customer_history"].setdefault(customer_id, [])
            self.context["customer_history"][customer_id].append({
                "timestamp": asyncio.get_event_loop().time(),
                "ticket_id": ticket.id,
                "subject": ticket.subject
            })

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((RuntimeError, TimeoutError)),
        reraise=True
    )
    async def _retry_analysis(self, ticket: SupportTicket):
        """Retryable analysis operation"""
        try:
            return await self.analysis_agent.analyze_ticket(
                ticket.content,
                self._get_customer_history(ticket)
            )
        except Exception as e:
            logger.warning(f"Analysis retry failed: {str(e)}")
            raise

    def _get_customer_history(self, ticket: SupportTicket) -> Dict[str, Any]:
        """Retrieve relevant customer context"""
        customer_id = ticket.customer_info.get("customer_id")
        return {
            "previous_tickets": self.context["customer_history"].get(customer_id, []),
            "customer_profile": ticket.customer_info
        }

    async def _generate_response(
        self,
        analysis: Any,
        ticket: SupportTicket
    ) -> Any:
        """Generate response with fallback"""
        try:
            return await self.response_agent.generate_response(
                analysis,
                self._load_templates(),
                self._get_response_context(ticket)
            )
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            raise

    def _load_templates(self) -> Dict[str, str]:
        """Mock template loading - implement actual loading logic"""
        return {
            "technical_response": "Technical issue template...",
            "billing_response": "Billing inquiry template..."
        }

    def _get_response_context(self, ticket: SupportTicket) -> Dict[str, Any]:
        """Build response context"""
        return {
            "customer_info": ticket.customer_info,
            "system_status": self.context["system_state"],
            "previous_responses": self._get_previous_responses(ticket)
        }

    def _validate_response(self, response: Any):
        """Quality checks for generated response"""
        if not response.response_text.strip():
            raise ValueError("Empty response generated")
            
        if response.confidence_score < 0.4:
            raise ValueError(f"Low confidence response: {response.confidence_score}")

    def _update_system_state(self, success: bool):
        """Track system health metrics"""
        if success:
            self.context["system_state"]["consecutive_failures"] = 0
            self.context["system_state"]["last_processed"] = asyncio.get_event_loop().time()
        else:
            self.context["system_state"]["consecutive_failures"] += 1

    def _get_previous_responses(self, ticket: SupportTicket) -> List[dict]:
        """Retrieve historical responses for context"""
        customer_id = ticket.customer_info.get("customer_id")
        return self.context["customer_history"].get(customer_id, [])[-3:]  # Last 3 tickets
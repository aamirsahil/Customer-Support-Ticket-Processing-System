from src.models import SupportTicket, TicketResolution, TicketAnalysis

from src.agents.TicketAnalysisAgent import TicketAnalysisAgent
from src.agents.ResponseAgent import ResponseAgent

import logging
import asyncio
import spacy
from typing import List, Dict, Any

# configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
nlp = spacy.load("en_core_web_sm")

class TicketProcessor:
    def __init__(self, max_retries: int = 3):
        self.analysis_agent = TicketAnalysisAgent()
        self.response_agent = ResponseAgent()
        self.context = {
            "customer_history" : {},
            "system_state": {
                "last_processed": None,
                "consecutive_failures": 0
            }
            }
        self.max_retries = max_retries

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
            # update context
            self._update_context(ticket)

            # analysis generation
            analysis = await self._generate_analysis(ticket)
            resolution.analysis = analysis

            # response generation
            response = await self._generate_response(analysis, ticket)
            resolution.response = response

            # finalize
            resolution.response_text = response.response_text
            resolution.status = "needs_approval" if response.requires_approval else "completed"
            self._update_system_state(success=True)

        except Exception as e:
            logger.error(f"Processing failed for {ticket.id}: {str(e)}")
            resolution.error = str(e)
            self._update_system_state(success=False)
            return resolution

        return resolution
        
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

    async def _generate_analysis(self, ticket: SupportTicket) -> TicketAnalysis:
        """Analyse Ticket"""
        try:
            ticket_text = f"<|role|> {ticket.customer_info.get('role', '')} <|role|>"\
                        + f"<|subject|> {ticket.subject} <|subject|>"\
                        + f"<|content|> {ticket.content} <|content|>"
            
            return await self.analysis_agent.analyze_ticket(
                ticket_text,
                self._get_customer_history(ticket)
            )
        except Exception as e:
            logger.warning(f"Analysis retry failed: {str(e)}")
            raise

    def _get_customer_history(self, ticket: SupportTicket) -> Dict[str, Any]:
        """Retrieve relevant customer context"""
        customer_id = ticket.customer_info.get("customer_id", "")
        return {
            "previous_tickets": self.context["customer_history"].get(customer_id, []),
            "customer_profile": ticket.customer_info
        }

    async def _generate_response(
        self,
        analysis: TicketAnalysis,
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

    def _load_templates(self, path: str = "./src/config/templates.py") -> Dict[str, str]:
        """Load templates from a Python module"""
        try:
            from importlib.util import spec_from_file_location, module_from_spec
            spec = spec_from_file_location("templates", path)
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.RESPONSE_TEMPLATES
        except Exception as e:
            raise RuntimeError(f"Failed to load templates: {str(e)}")
        
    def _get_response_context(self, ticket: SupportTicket) -> Dict[str, Any]:
        """Build response context"""
        return {
            "customer_info": self._extract_customer_info(ticket),
            "system_status": self.context["system_state"],
            "previous_responses": self._get_previous_responses(ticket)
        }
    
    def _extract_customer_info(self, ticket: SupportTicket) -> Dict[str, str]:
        return {
            "customer_id" : ticket.customer_info.get("customer_id", 0),
            "customer_name" : self._extract_customer_name(ticket)
        }
    
    def _extract_customer_name(self, ticket: SupportTicket) -> str:
        # process the text with spaCy
        doc = nlp(ticket.content)

        # extract person names using Named Entity Recognition (NER)
        customer_names = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
        return ', '.join(customer_names)
    
    def _get_previous_responses(self, ticket: SupportTicket) -> List[dict]:
        """Retrieve historical responses for context"""
        customer_id = ticket.customer_info.get("customer_id", 0)
        return self.context["customer_history"].get(customer_id, [])[-3:] # last 3 tickets
        
    def _update_system_state(self, success: bool):
        """Track system health metrics"""
        if success:
            self.context["system_state"]["consecutive_failures"] = 0
            self.context["system_state"]["last_processed"] = asyncio.get_event_loop().time()
        else:
            self.context["system_state"]["consecutive_failures"] += 1
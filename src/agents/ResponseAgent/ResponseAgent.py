from src.models import ResponseSuggestion, TicketAnalysis, Priority, TicketCategory

from typing import Dict, Any, List
import spacy
from jinja2 import Template
import textstat
from textblob import TextBlob

class ResponseAgent:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.approval_triggers = ["credit", "refund", "compensation", "legal"]

    async def generate_response(
        self,
        ticket_analysis: TicketAnalysis,
        response_templates: Dict[str, str],
        context: Dict[str, Any]
    ) -> ResponseSuggestion:
        """
        Features:
        1. Template Selection:
           - Match appropriate template
           - Customize based on context
           - Include relevant information
        
        2. Response Customization:
           - Personalization
           - Technical detail level
           - Action items
        
        Return:
        {
            "response_text": str,
            "confidence_score": float,
            "requires_approval": bool,
            "suggested_actions": List[str]
        }
        """
        # select and customize template
        template = self._select_template(ticket_analysis, response_templates)
        filled_template = self._customize_template(
            template,
            ticket_analysis,
            context
        )

        # finding confidence and approval
        confidence = self._calculate_confidence(filled_template, ticket_analysis)
        requires_approval = self._requires_approval(filled_template, ticket_analysis, confidence)
        actions = self._generate_actions(ticket_analysis, context)

        return ResponseSuggestion(
            response_text=filled_template,
            confidence_score=confidence,
            requires_approval=requires_approval,
            suggested_actions=actions
        )
    
    def _select_template(
        self,
        analysis: TicketAnalysis,
        templates: Dict[str, str]
    ) -> str:
        """Select Template based on suggested response type, use category value for fallback"""
        # exact match
        template_key = analysis.suggested_response_type
        if template_key in templates:
            return templates[template_key]
        
        # category-based match
        category_template = f"{analysis.category.value}"
        if category_template in templates:
            return templates[category_template]
        
        # fallback to general response
        return templates.get("general", "Thank you for your inquiry. We are looking into it.")
    
    def _customize_template(
        self,
        template: str,
        analysis: TicketAnalysis,
        context: Dict[str, Any]
    ) -> str:
        """Customize template based on customer information"""
        # extract entities for templating
        customer_name = self._extract_customer_name(context)
        # expected update based on priority
        eta_map = {
            Priority.CRITICAL: "Immediate to 24 hours.",
            Priority.HIGH: "Within 2 to 3 days.",
            Priority.MEDIUM: "Within 1 to 2 weeks.",
            Priority.LOW: "Within 1 month or as resources permit."
        }
        variables = {
            "name": customer_name or "valued customer",
            "priority": analysis.priority.name.lower(),
            "key_points": ", ".join(analysis.key_points[:3]),
            "expertise": analysis.required_expertise[0] if analysis.required_expertise else "our team",
            "issue_type": analysis.category.name.lower(),
            "eta": eta_map[analysis.priority],
            "feedback_channel": "email",
            **context.get("customer_info", {})
        }
        
        # render template with error handling
        try:
            return Template(template).render(**variables)
        except:
            print("hi")
            return template  # fallback to raw template
        
    def _extract_customer_name(self, context: Dict[str, Any]) -> str:
        """Extract customer name if present"""
        if "customer_name" in context.get("customer_info", {}):
            return context["customer_info"]["customer_name"]
        
        # fallback to NER extraction from ticket history
        if "previous_tickets" in context:
            doc = self.nlp("\n".join(context["previous_tickets"]))
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text
        return ""
    
    def _calculate_confidence(
        self,
        response: str,
        analysis: TicketAnalysis
    ) -> float:
        """Calculate confidence based on readability and sentiment"""
        # base confidence based on priority
        confidence = 0.7 if analysis.priority.value < 3 else 0.5
        
        # adjust based on text metrics
        readability = textstat.flesch_reading_ease(response)
        confidence += 0.2 if readability > 60 else -0.1
        
        # reduce confidence if response is negative 
        response_sentiment = TextBlob(response).sentiment.polarity
        confidence += 0.1 * response_sentiment
        
        return max(0, min(1, confidence))
    
    def _requires_approval(
        self,
        response: str,
        analysis: TicketAnalysis,
        confidence: float
    ) -> bool:
        """Check if the response requires approval before sending"""
        # high priority always requires approval
        if analysis.priority == Priority.CRITICAL:
            return True
            
        # content based approval triggers
        if any(trigger in response.lower() for trigger in self.approval_triggers):
            return True
            
        # low confidence threshold
        return confidence < 0.6

    def _generate_actions(
        self,
        analysis: TicketAnalysis,
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate suggested actions based on priority and category"""
        actions = []
        
        # category-specific actions
        if analysis.category == TicketCategory.TECHNICAL:
            actions.extend(["Run diagnostics", "Check server logs"])
        elif analysis.category == TicketCategory.BILLING:
            actions.append("Verify payment records")
            
        # priority-based actions
        if analysis.priority.value > 2:
            actions.append("Escalate to senior staff")
            
        # customer tier actions
        if context.get("customer_info", {}).get("plan", "user").lower() == "enterprise":
            actions.append("Schedule dedicated support call")
            
        return actions if actions else ["Monitor ticket status"]
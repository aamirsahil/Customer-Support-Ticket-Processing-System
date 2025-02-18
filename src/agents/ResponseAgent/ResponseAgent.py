from src.models import ResponseSuggestion, TicketAnalysis, Priority, TicketCategory

from typing import Dict, Any, List
import spacy
from jinja2 import Template
import textstat
from textblob import TextBlob

class ResponseAgent:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.tech_jargon = ["SLA", "API", "latency", "throughput"]
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
        
        final_text = self._adjust_technical_level(
            filled_template,
            context.get("customer_info", {})
        )
        final_text = self._personlize_greeting(final_text, context)

        # finding confidence and approval
        confidence = self._calculate_confidence(final_text, ticket_analysis)
        requires_approval = self._requires_approval(final_text, ticket_analysis)
        actions = self._generate_actions(ticket_analysis, context)

        return ResponseSuggestion(
            response_text=final_text,
            confidence_score=confidence,
            requires_approval=requires_approval,
            suggested_actions=actions
        )
    
    def _select_template(
        self,
        analysis: TicketAnalysis,
        templates: Dict[str, str]
    ) -> str:
        # exact match
        template_key = analysis.suggested_response_type
        if template_key in templates:
            return templates[template_key]
        
        # category-based match
        category_template = f"{analysis.category.value}_response"
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
        # extract entities for templating
        customer_name = self._extract_customer_name(context)
        variables = {
            "name": customer_name or "valued customer",
            "priority": analysis.priority.name.lower(),
            "key_points": ", ".join(analysis.key_points[:3]),
            "expertise": analysis.required_expertise[0] if analysis.required_expertise else "our team",
            **context.get("customer_info", {})
        }
        
        # render template with error handling
        try:
            return Template(template).render(**variables)
        except:
            return template  # fallback to raw template
        
    def _extract_customer_name(self, context: Dict[str, Any]) -> str:
        if "customer_name" in context.get("customer_info", {}):
            return context["customer_info"]["customer_name"]
        
        # Fallback to NER extraction from ticket history
        if "previous_tickets" in context:
            doc = self.nlp("\n".join(context["previous_tickets"]))
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text
        return ""
    
    def _adjust_technical_level(
        self,
        text: str,
        customer_info: Dict[str, Any]
    ) -> str:
        role = customer_info.get("role", "").lower()
        if any(t in role for t in ["engineer", "developer", "cto"]):
            return text  # Keep technical terms
        
        # Simplify technical jargon
        for term in self.tech_jargon:
            text = text.replace(term, self._explain_term(term))
        return text
    
    def _explain_term(self, term: str) -> str:
        explanations = {
            "SLA": "service level agreement",
            "API": "application interface",
            "latency": "response time",
            "throughput": "processing capacity"
        }
        return explanations.get(term, term)
    
    def _personalize_greeting(self, text: str, context: Dict[str, Any]) -> str:
        if "{name}" not in text:
            name = self._extract_customer_name(context)
            if name:
                return f"Dear {name},\n\n{text}"
        return text
    
    def _calculate_confidence(
        self,
        response: str,
        analysis: TicketAnalysis
    ) -> float:
        # Base confidence on template match
        confidence = 0.7 if analysis.priority.value < 3 else 0.5
        
        # Adjust based on text metrics
        readability = textstat.flesch_reading_ease(response)
        confidence += 0.2 if readability > 60 else -0.1
        
        # Sentiment alignment
        response_sentiment = TextBlob(response).sentiment.polarity
        confidence += 0.1 * (1 - abs(analysis.sentiment - response_sentiment))
        
        return max(0, min(1, confidence))
    
    def _requires_approval(
        self,
        response: str,
        analysis: TicketAnalysis
    ) -> bool:
        # High priority always requires approval
        if analysis.priority == Priority.URGENT:
            return True
            
        # Content-based approval triggers
        if any(trigger in response.lower() for trigger in self.approval_triggers):
            return True
            
        # Low confidence threshold
        return self._calculate_confidence(response, analysis) < 0.6

    def _generate_actions(
        self,
        analysis: TicketAnalysis,
        context: Dict[str, Any]
    ) -> List[str]:
        actions = []
        
        # Category-specific actions
        if analysis.category == TicketCategory.TECHNICAL:
            actions.extend(["Run diagnostics", "Check server logs"])
        elif analysis.category == TicketCategory.BILLING:
            actions.append("Verify payment records")
            
        # Priority-based actions
        if analysis.priority.value > 2:
            actions.append("Escalate to senior staff")
            
        # Customer tier actions
        if context.get("customer_info", {}).get("plan") == "Enterprise":
            actions.append("Schedule dedicated support call")
            
        return actions if actions else ["Monitor ticket status"]
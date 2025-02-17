# import sys
# import os

# # Get the parent directory of the current script
# parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# # Append the parent directory to sys.path
# sys.path.append(parent_dir)

from models import TicketCategory, Priority, TicketAnalysis
from typing import List, Optional, Dict, Any
import re
import spacy
from transformers import pipeline

nlp = spacy.load("en_core_web_sm")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

class TicketAnalysisAgent:
    def __init__(self):
        self.urgency_pattern = re.compile(
            r"\b(ASAP|urgent|immediately|critical|emmergency|right away)\b",
            re.IGNORECASE
        )

        self.impact_words = {
            "payroll" : 2.0,
            "revenue" : 1.8,
            "sales" : 1.5,
            "demo" : 1.5,
            "client" : 1.3
        }

        self.role_weights = {
            "ceo" : 2.0, "cfo" : 2.0, "cto" : 2.0,
            "director" : 1.7, "manager" : 1.3
        }

    async def analyze_ticket(
        self,
        ticket_content: str,
        customer_history: Optional[Dict[str, Any]] = None
    ) -> TicketAnalysis:
        """
        Implement:
        1. Ticket Classification:
           - Technical Issue
           - Billing Question
           - Feature Request
           - Account Access
        
        2. Priority Assessment:
           - Urgency detection
           - Impact evaluation
           - SLA requirements
        
        Return:
        {
            "category": str,
            "priority": int,
            "key_points": List[str],
            "required_expertise": List[str],
            "suggested_response_type": str
        }
        """
        # clean and preprocess ticket_content
        clean_text = self._preprocess_text(ticket_content)

        # classify text
        category = await self._classify_ticket(clean_text)

        # detect urgency
        urgency_indicators = self._detect_urgency(clean_text)

        # calculate priority
        priority = self._calculate_priority(
            clean_text,
            urgency_indicators,
            customer_history
        )

        # extract key poits
        key_points = self._extract_key_points(clean_text)

        # determine required expertise
        required_expertise = self._determine_expertise(clean_text)

        # suggested response type
        suggested_response_type = self._suggest_respnse_type(category, priority)

        return TicketAnalysis(
            category = category,
            priority = priority,
            key_points = key_points,
            required_expertise = required_expertise,
            suggested_respose_type = suggested_response_type
        )

    def _preprocess_text(self, text : str) -> str:
        clean_text = text.lower().replace("\n", " ").strip()
        return clean_text

    def _classify_ticket(self, text : str) -> TicketCategory:
        labels = [label.value for label in TicketCategory]
        result = classifier(text, labels)
        
        return TicketCategory(result['labels'][0])


    def _keyword_classification(self, text: str) -> TicketCategory:
        keywords = {
            TicketCategory.TECHNICAL: ["error", "bug", "crash", "slow"],
            TicketCategory.BILLING: ["invoice", "charge", "payment", "fee"],
            TicketCategory.FEATURE: ["request", "suggest", "add", "new feature"],
            TicketCategory.ACCESS: ["login", "access", "password", "permission"]
        }
        
        for category, terms in keywords.items():
            if any(term in text for term in terms):
                return category
        return TicketCategory.TECHNICAL  # Default
    
    def _calculate_priority(
            self,
            text: str,
            urgency_indicators: List[str],
            customer_info: Optional[dict]
        ) -> Priority:
            base_score = 1.0
            role = customer_info.get("role", "").lower() if customer_info else ""
            
            # Urgency boost
            base_score += len(urgency_indicators) * 0.5
            
            # Role boost
            role_boost = next(
                (v for k, v in self.role_weights.items() if k in role),
                1.0
            )
            base_score *= role_boost
            
            # Business impact boost
            impact = max(
                [v for k, v in self.impact_keywords.items() if k in text],
                default=1.0
                )
            base_score *= impact
            
            # Cap and convert to Priority enum
            final_score = min(max(round(base_score), 4))
            return Priority(final_score)
    
    def _extract_key_points(self, text: str) -> List[str]:
        doc = nlp(text)
        return [
            chunk.text for chunk in doc.noun_chunks
            if chunk.root.pos_ in ["NOUN", "PROPN"]
        ][:5]  # Return top 5 key points

    def _determine_expertise(
        self,
        category: TicketCategory,
        key_points: List[str]
    ) -> List[str]:
        expertise_map = {
            TicketCategory.TECHNICAL: ["backend", "frontend", "devops"],
            TicketCategory.BILLING: ["finance", "billing_specialist"],
            TicketCategory.FEATURE: ["product", "engineering"],
            TicketCategory.ACCESS: ["security", "iam"]
        }
        return expertise_map.get(category, ["general"])

    def _detect_urgency(self, text: str) -> List[str]:
        return list(set(self.urgency_pattern.findall(text)))
    
    def _suggest_response_type(
        self,
        category: TicketCategory,
        priority: Priority
    ) -> str:
        if priority.value >= Priority.HIGH.value:
            return "immediate_call_back"
        return {
            TicketCategory.TECHNICAL: "technical_response",
            TicketCategory.BILLING: "billing_documentation",
            TicketCategory.FEATURE: "feature_acknowledgement",
            TicketCategory.ACCESS: "security_verification"
        }.get(category, "general_response")
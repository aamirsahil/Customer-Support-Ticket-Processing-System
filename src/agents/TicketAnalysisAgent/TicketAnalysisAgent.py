from src.models import TicketAnalysis, TicketCategory, Priority

from typing import List, Optional, Dict, Any
import re
import yake
from transformers import pipeline

kw_extractor = yake.KeywordExtractor()
classifier = None#pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

class TicketAnalysisAgent:
    def __init__(self):
        # urgency word patterns
        self.urgency_pattern = re.compile(
            r"\b(asap|urgent|immediately|critical|emmergency|right away|severe|403)\b",
            re.IGNORECASE
        )
        # buisiness impact words
        self.impact_words = {
            "payroll" : 2.0,
            "revenue" : 1.8,
            "sales" : 1.5,
            "demo" : 1.5,
            "client" : 1.3
        }
        # customer role weights
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
        # category = self._classify_ticket(clean_text)
        category = TicketCategory.ACCESS
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
        required_expertise = self._determine_expertise(category)

        # suggested response type
        suggested_response_type = self._suggest_response_type(category, priority)

        return TicketAnalysis(
            category = category,
            priority = priority,
            key_points = key_points,
            required_expertise = required_expertise,
            suggested_response_type = suggested_response_type
        )

    def _preprocess_text(self, text : str) -> str:
        clean_text = text.lower().replace("\n", " ").strip()
        # replace 2+ spaces with single space
        clean_text = re.sub(r' {2,}', ' ', clean_text)
        return clean_text

    def _classify_ticket(self, text : str) -> TicketCategory:
        labels = [label.value for label in TicketCategory]
        result = classifier(text, labels)
        
        # threshold for model confidence
        if result["scores"][0] > 0.7:
            return TicketCategory(result["labels"][0])
        
        # fallback to keyword matching
        return self._keyword_classification(text)
    
    def _detect_urgency(self, text: str) -> List[str]:
        return list(set(self.urgency_pattern.findall(text)))

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
        return TicketCategory.TECHNICAL  # default
    
    def _calculate_priority(
            self,
            text: str,
            urgency_indicators: List[str],
            customer_info: Optional[dict]
        ) -> Priority:
            base_score = 1.0
            
            # urgency score added to base
            base_score += len(urgency_indicators) * 0.5
            
            # role score multiplied to base
            role_score = max(
                [v for k, v in self.role_weights.items() if k in text],
                default=1.0
                )
            base_score *= role_score
            
            # business impact score multiplied to base
            impact_score = max(
                [v for k, v in self.impact_words.items() if k in text],
                default=1.0
                )
            base_score *= impact_score
            
            # cap and convert to Priority enum
            final_score = min(round(base_score), 4)
            return Priority(final_score)
    
    def _extract_key_points(self, text: str) -> List[str]:
        keywords = kw_extractor.extract_keywords(text)
        key_points = [keyword for keyword, score in sorted(keywords, key=lambda x: x[1], reverse=True)]
        return key_points[:10]  # return top 10 key points

    def _determine_expertise(
        self,
        category: TicketCategory,
    ) -> List[str]:
        expertise_map = {
            TicketCategory.TECHNICAL: ["backend", "frontend", "devops"],
            TicketCategory.BILLING: ["finance", "billing_specialist"],
            TicketCategory.FEATURE: ["product", "engineering"],
            TicketCategory.ACCESS: ["security", "iam"]
        }
        return expertise_map.get(category, ["general"])
    
    def _suggest_response_type(
        self,
        category: TicketCategory,
        priority: Priority
    ) -> str:
        if priority.value >= Priority.HIGH.value:
            return "immediate_call_back"
        return {
            TicketCategory.TECHNICAL: "technical",
            TicketCategory.BILLING: "billing",
            TicketCategory.FEATURE: "feature",
            TicketCategory.ACCESS: "access"
        }.get(category, "general")
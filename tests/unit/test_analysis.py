import pytest
from src.agents.TicketAnalysisAgent import TicketAnalysisAgent
from src.models import TicketCategory

def test_classify_ticket():
    # arrange
    ticket_analysis_agent = TicketAnalysisAgent()
    text = "Hello, I received invoice #12345, and there are charges listed that I don't recognize. Could you please provide a detailed breakdown of these charges?"

    # act
    result = ticket_analysis_agent._classify_ticket(text)

    # assert
    expected = TicketCategory.BILLING
    assert result == expected, f"Expected classification to be {expected}, but got {result}"
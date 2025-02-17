from src.agents.TicketAnalysisAgent.TicketAnalysisAgent import TicketAnalysisAgent

def test():
    ticket_analysis_agent = TicketAnalysisAgent()
    text = "i need to know how much the product cost"
    print(ticket_analysis_agent._classify_ticket(text))
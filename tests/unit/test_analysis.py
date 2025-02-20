import pytest
from src.agents.TicketAnalysisAgent import TicketAnalysisAgent
from src.models import TicketCategory
import json

ticket_analysis_agent = TicketAnalysisAgent()

# function to get ticket sample text
def open_ticket_sample():
    
    with open('tests/data/test_template/ticket_sample.json', 'r') as file:
        data = json.load(file)
    
    text = f"""<|role|> {data[0]['customer_info']['role']} <|role|>
            <|subject|> {data[0]['subject']} <|subject|>
            <|content|> {data[0]['content']} <|content|>""" 
    
    return text

# testing preprocess text
def test_preprocess_text():
    # arrange
    text = open_ticket_sample()
    # act
    result = ticket_analysis_agent._preprocess_text(text)
    # assert
    expected = """<|role|> admin <|role|>
                <|subject|> cannot access admin dashboard <|subject|>
                <|content|> hi support, since this morning i can't access the admin dashboard. i keep getting a 403 error. i need this fixed asap as i need to process payroll today.  thanks, john smith finance director <|content|>"""
    
    assert result == expected, f"Expected = {expected} || Result = {result}"

# testing _classify_ticket()
def test_classify_ticket():
    # arrange
    text = open_ticket_sample()
    # act
    result = ticket_analysis_agent._classify_ticket(text)
    # assert
    expected = TicketCategory.ACCESS
    assert result == expected, f"Expected = {expected} || Result {result}"

# testing urgency detection
def test_detect_urgency():
    # arrange
    text = open_ticket_sample()
    # act
    result = ticket_analysis_agent._detect_urgency(text)
    # assert
    expected = ['403', 'asap']
    assert result == expected, f"Expected = {expected} || Result = {result}"

def test_calculate_priority():
    # arrange
    text = open_ticket_sample()
    dummy_urgency_indicators = ['403', 'asap']
    dummy_customer_info = {"role" : "finance director"}

    priority = ticket_analysis_agent._calculate_priority(
                text,
                dummy_urgency_indicators)
    
    assert priority.ty 
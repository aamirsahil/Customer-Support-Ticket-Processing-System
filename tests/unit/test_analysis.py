import pytest
from src.agents.TicketAnalysisAgent import TicketAnalysisAgent
from src.models import TicketCategory
import json

ticket_analysis_agent = TicketAnalysisAgent()

# function to get ticket sample text
def open_ticket_sample():
    
    with open('..data/test_template/ticket_sample.json', 'r') as file:
        data = json.load(file)
    
    text = f"<|role|> {data[0]['customer_info']['role']} <|role|>
            <|subject|> {data[0]['subject']} <|subject|>
            <|content|> {data[0]['content']} <|content|>" 
    
    return text

# testing preprocess text
def test_preprocess_text():
    # arrange
    text = open_ticket_sample()
    # act
    result = ticket_analysis_agent._preprocess_text(text)
    # assert
    expected = "<|role|> cto <|role|>\
                <|subject|> urgent: production database offline <|subject|>\
                <|content|> critical outage! production database cluster down since 2:00 am. customers can't place orders. contact: +44 7890 123456  -sent from mobile <|content|>"
    
    assert result == expected, f"Expected = {expected} || Result = {result}"

# testing _classify_ticket()
def test_classify_ticket():
    # arrange
    text = open_ticket_sample()
    # act
    result = ticket_analysis_agent._classify_ticket(text)
    # assert
    expected = TicketCategory.TECHNICAL
    assert result == expected, f"Expected = {expected} || Result {result}"

# testing urgency detection
def test_detect_urgency():
    # arrange
    text = open_ticket_sample()
    # act
    result = ticket_analysis_agent._detect_urgency(text)
    # assert
    expected = ['urgent', 'critical']
    assert result == expected, f"Expected = {expected} || Result = {result}"

def test_calculate_priority():
    # arrange
    text = open_ticket_sample()
    dummy_urgency_indicators = ['urgent', 'critical']

    priority = ticket_analysis_agent._calculate_priority(
                text,
                dummy_urgency_indicators)
    
    assert priority.ty 
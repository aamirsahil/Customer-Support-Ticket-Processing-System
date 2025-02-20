import os
import sys

# insert the project root directory into sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.agents.TicketProcessor import TicketProcessor
from src.models.ticket_models import SupportTicket

import asyncio
from datetime import datetime

# test implementation
async def test_integration():
    # initialize processor agent
    processor = TicketProcessor()

    # Define test ticket
    test_ticket = SupportTicket(
        id="TKT-001",
        subject="Cannot access admin dashboard",
        content="""
        Hi Support,
        Since this morning I can't access the admin dashboard. 
        I keep getting a 403 error. Need this fixed ASAP for payroll    .
        
        Thanks,
        John Smith
        """,
        customer_info={
            "customer_id": "001",
            "role": "Finance Director",
            "plan": "Enterprise",
            "company_size": "250+"
        }
    )

    # Process ticket
    start_time = datetime.now()
    result = await processor.process_ticket(test_ticket)
    processing_time = datetime.now() - start_time

    # Print results
    print(f"\n{'='*40} Ticket Processing Report {'='*40}")
    print(f"Ticket ID: {result.ticket_id}")
    print(f"Processing Time: {processing_time.total_seconds():.2f}s")
    print(f"\nAnalysis Results:")
    print(f"Category: {result.analysis.category.name}")
    print(f"Priority: {result.analysis.priority.name}")
    print(f"Key Points: {result.analysis.key_points}")
    
    print(f"\nGenerated Response:")
    print(f"{result.response_text}")
    
    print(f"\nAdditional information:")
    print(f"Confidence: {result.response.confidence_score:.2f}")
    print(f"Requires Approval: {result.response.requires_approval}")
    print(f"Suggested Actions: {result.response.suggested_actions}")

# run the test
asyncio.run(test_integration())
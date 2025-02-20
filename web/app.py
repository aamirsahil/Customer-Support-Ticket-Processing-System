import sys
import os

# Add the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask, render_template, request, redirect, url_for
from dataclasses import asdict
import asyncio
from src.agents.TicketProcessor import TicketProcessor
from src.models import SupportTicket

app = Flask(__name__)

# Simple in-memory storage for demo purposes
support_tickets = []
processed_tickets = []


@app.route('/')
def index():
    return render_template('index.html', tickets=processed_tickets)

@app.route('/add-ticket', methods=['GET', 'POST'])
def add_ticket():
    if request.method == 'POST':
        # Create support ticket from form data
        ticket_data = {
            "id": f"TKT-{len(processed_tickets)+1:03d}",
            "subject": request.form['subject'],
            "content": request.form['content'],
            "customer_info": {
                "customer_id": request.form.get('id', 0),
                "company_type": request.form['company_type'],
                "role": request.form.get('role', 'User'),
                "plan": request.form.get('plan', 'Standard')
            }
        }
        support_tickets.append(ticket_data)
        # Process ticket asynchronously
        result = asyncio.run(process_ticket_async(ticket_data))
        processed_tickets.append(result)
        
        return redirect(url_for('index'))
    
    return render_template('add_ticket.html')

@app.route('/ticket/<ticket_id>')
def view_ticket(ticket_id):
    ticket = next((t for t in processed_tickets if t['ticket_id'] == ticket_id), None)
    original_ticket = next((t for t in support_tickets if t['id'] == ticket_id), None)
    return render_template('view_ticket.html', ticket=ticket, original_ticket=original_ticket)

async def process_ticket_async(ticket_data):
    processor = TicketProcessor()
    support_ticket = SupportTicket(**ticket_data)
    resolution = await processor.process_ticket(support_ticket)
    return asdict(resolution)

if __name__ == '__main__':
    app.run(debug=True)
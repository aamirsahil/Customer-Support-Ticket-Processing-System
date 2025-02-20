RESPONSE_TEMPLATES = {
    "access": """
    Hello {{name}},
    
    I understand you're having trouble accessing the {{feature}}. Let me help you resolve this.
    
    Diagnosis: {{diagnosis}}
    
    Resolution Steps:
    {{resolution_steps}}
    
    Priority: {{priority}}
    ETA: {{eta}}
    
    Please let me know if you need any clarification.
    
    Best regards,
    Baguette Support
    """,
    
    "billing": """
    Hi {{name}},
    
    Thank you for your inquiry about {{billing_topic}}.
    
    Explanation:
    {{explanation}}
    
    Next Steps:
    {{next_steps}}
    
    If you have any questions, don't hesitate to ask.
    
    Best regards,
    Baguette Billing Team
    """,
    
    "technical": """
    Dear {{name}},
    
    We've identified this as a {{technical_category}} issue.
    
    Technical Details:
    {{technical_details}}
    
    Our team is {{resolution_plan}}.
    
    Best regards,
    Technical Support Team
    """,

    "feature_request": """
    Hi {{name}},
    
    Thank you for suggesting {{feature_name}}!
    
    Our product team will review this request:
    - Request details: {{feature_details}}
    - Priority: {{priority}}
    - Similar existing features: {{similar_features}}
    
    {{details_request}}
    
    Next Steps:
    1. We'll add this to our feature backlog
    2. You'll receive updates via {{feedback_channel}}
    3. Expected review timeline: {{review_timeline}}
    
    Best regards,
    Product Team
    """,
    
    "immediate_call_back": """
    URGENT: {{name}}
    
    We're prioritizing your {{issue_type}} request.
    
    Next Steps:
    - Senior agent will call within {{eta}}
    - Contact number: {{contact_number}}
    - Reference: {{ticket_id}}
    
    Please ensure availability for:
    {{callback_availability}}
    
    On-call engineer: {{agent_name}}
    Current system status: {{system_status}}
    """,
    
    "general_response": """
    Hello {{name}},
    
    Thank you for contacting support regarding {{inquiry_type}}.
    
    We're currently:
    {{current_status}}
    
    Next Updates:
    {{next_steps}}
    
    We'll provide another update by {{eta}}.
    
    Best regards,
    Support Team
    """
}
```markdown
# AI Customer Support Ticket Processing System

An automated ticket processing system using AI agents for classification, prioritization, and response generation.

---

## Features

- **Ticket Classification:** Automatically classify tickets into 4 categories(BILLING, TECHNICAL, ACCESS, FEATURE).
- **Priority Assessment:** Detect urgency and assign priority levels.
- **Context-Aware Response:** Generate personalized responses based on ticket context.
- **Web Interface:** Manage tickets via an intuitive web UI.
- **Error Handling:** Robust error handling and validation mechanisms.

---

## Setup Instructions

### Prerequisites

- **Python:** Version 3.9 or higher
- **Package Manager:** pip

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/aamirsahil/Customer-Support-Ticket-Processing-System.git
   cd Customer-Support-Ticket-Processing-System
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   ```
   - **Activate the Virtual Environment:**
     - Linux/MacOS:
       ```bash
       source venv/bin/activate
       ```
     - Windows:
       ```bash
       venv\Scripts\activate
       ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   python -m textblob.download_corpora
   ```

4. **Set Environment Variables:**
   ```bash
   cp .env.example .env
   ```
   - Edit the `.env` file with your configuration settings.

5. **Run the Application:**
   ```bash
   flask run --port 5000
   ```

---

## Design Decisions

### Architecture Overview

The system is designed using a three-tier architecture, ensuring a clear separation of concerns.

#### Key Components

- **Ticket Analysis Agent:**
  - Hybrid ML and Rule classification.
  - Uses DistilBERT for category classification.
  - Leverages yake for key point extraction.
  - Implements a custom priority scoring algorithm.

- **Response Generation Agent:**
  - Utilizes the Jinja2 templating system.
  - Includes a confidence-based approval system.
  - Features a multi-level fallback mechanism.

- **Orchestration Layer:**
  - Manages an asynchronous processing pipeline.
  - Preserves context across tickets.

---

### Technology Choices

| **Component**       | **Technology**           | **Rationale**                         |
|---------------------|--------------------------|---------------------------------------|
| NLP Processing      | yake + Transformers      | Balances speed and accuracy           |
| ML Framework        | HuggingFace              | Availability of pretrained models     |
| Web Framework       | Flask                    | Lightweight and flexible              |
| Caching             | sql                      | High performance in production        |
| Testing             | pytest                   | Ecosystem compatibility               |

---

## Testing Approach

### Test Types

- **Unit Testing:**
  - Isolates agent components.
  - Validates templates.
  - Tests priority scoring logic.

- **Integration Testing:**
  - Verifies the full processing pipeline.
  - Checks context preservation.
  - Assesses error recovery scenarios.

- **End-to-End Testing:**
  - Simulates web UI workflows.
  - Validates ticket submission flow.
  - Ensures response accuracy.

### Running Tests

```bash
# Run unit tests
pytest tests/unit -v

# Run integration tests
pytest tests/integration -v

```

### Test Data Strategy

- **Sample Tickets:** tests/data/test_template.
- **Edge Cases:**
  - Ambiguous ticket content.
  - Missing customer information.
  - Mixed-category tickets.
---

## Future Improvements

- **User Authentication:** Enhance security with user-specific access.
- **Approval Workflow:** Implement a multi-step approval process for responses.
- **Multi-language Support:** Cater to a global audience.
- **LLM:** Personalized response generation with LLM.
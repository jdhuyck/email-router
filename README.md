# AI-Powered Email Routing System

Businesses receive high volumes of emails that need automated categorization and routings. This project aims to provide (or provide a framework for) an NLP-based email classifier that uses transformer models to route emails to appropriate teams or trigger automated responses.

## Proposed Technologies

- **NLP**: Hugging Face's zero-shot-classification pipeline (requires no training data)
    - facebook/bart-large-mnli
    ```python
    from transformers import pipeline
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    labels = ["sales", "support", "billing"]
    result = classifier(email_body, candidate_labels=labels)
    ```
- **Backend**: FastAPI (lightweight, async)
    - Deploy FastAPI to Google Cloud Run
    - GitHub actions for CI/CD
    ```mermaid
    graph LR
        A[Build Docker image] --> B[Push to registry]
        B[Push to registry] --> C[Deploy to serverless]
    ```

- **Infrastructure**: Docker for containerization, Serverless Google Cloud
- **API**: Gmail API (OAuth2), Slack API (Webhooks for basic notifications)
- **Monitoring**: Prometheus Flask Exporter & GitHub pages
    - Prometheus for metrics
    - Export metrics to gh pages via static JSON periodically



## Development Phases

- **Phase 1** - FastAPI + Hugging Face model (test local)
- **Phase 2** - Integrate Gmail API and Slack
- **Phase 3** - Dockerize + deploy to cloud run
- **Phase 4** - Add basic metrics exporter


## Cost Analysis (ensure free)

- **Gmail API** - Free
- **Cloud Run** - Always-free tier
- **Slack Webhooks** - Free
- **Monitoring (GH pages)** - Free

**Total Cost - Free**


## Risks and mitigations

- **Gmail API Quota** - Limit polling to avoid rate limits (200 emails/day free)
- **Model Accuracy** - Zero-shot works fo broad categories but may struggle with similar categories
- **Serverless Cold Starts** - Use minimum instances (using Cloud Run)
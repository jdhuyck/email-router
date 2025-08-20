from fastapi import APIRouter, HTTPException

from app.core.models import ClassificationRequest, ClassificationResponse
from app.services.classifier import classification_service

router = APIRouter()


@router.post("/classify", response_model=ClassificationResponse)
async def classify_email(request: ClassificationRequest):
    """
    Classify an email text into a predefined category.

    - email_text: The body of the email to be classified
    """
    try:
        classification_result = await classification_service.classify_email(request.email_text)  # noqa:E501
        return classification_result
    except ValueError as e:
        # Handle empty text errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        # Handle any other unexpected errors
        raise HTTPException(status_code=500, detail="An internal error occurred during classification")  # noqa:E501

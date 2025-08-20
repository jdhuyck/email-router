from typing import List

from pydantic import BaseModel


class ClassificationRequest(BaseModel):
    """Request model for the classify endpoint."""

    email_text: str


class ClassificationResponse(BaseModel):
    """Response model for the classify endpoint."""

    sequence: str
    labels: List[str]
    scores: List[float]

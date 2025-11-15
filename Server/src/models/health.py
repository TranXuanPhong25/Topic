from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    version: str
    model: str
    clinic: str

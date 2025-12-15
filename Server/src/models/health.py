from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str
    model: str
    clinic: str

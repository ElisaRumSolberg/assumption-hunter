from pydantic import BaseModel


class Assumption(BaseModel):
    assumption: str
    category: str
    evidence: str
    risk: str
    severity: str = "medium"


class AssumptionReport(BaseModel):
    assumptions: list[Assumption]

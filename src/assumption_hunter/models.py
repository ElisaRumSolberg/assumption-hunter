from pydantic import BaseModel


class Assumption(BaseModel):
    assumption: str
    category: str
    evidence: str
    risk: str


class AssumptionReport(BaseModel):
    assumptions: list[Assumption]

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CompanyOut(BaseModel):
    ticker: str
    name: str
    sector: str | None = None
    industry: str | None = None
    exchange: str | None = None
    cik: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RelationshipOut(BaseModel):
    type: str
    target: str
    target_ticker: str | None = None
    confidence: float = Field(ge=0, le=1)
    source: str


class FactorOut(BaseModel):
    factor_date: date
    factor_name: str
    factor_value: float

    model_config = ConfigDict(from_attributes=True)


class EventOut(BaseModel):
    event_date: date
    event_type: str
    title: str
    summary: str
    source_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SignalOut(BaseModel):
    signal_date: date
    category: str
    score: float = Field(ge=-1, le=1)
    confidence: float = Field(ge=0, le=1)
    explanation: str

    model_config = ConfigDict(from_attributes=True)


class ExplanationOut(BaseModel):
    ticker: str
    summary: list[str]
    citations: list[str]
    affected_sectors: list[str]


class ThesisOut(BaseModel):
    ticker: str
    bull_case: list[str]
    bear_case: list[str]
    risks: list[str]
    catalysts: list[str]
    valuation: list[str]


class SimilarCompanyOut(BaseModel):
    ticker: str
    name: str
    similarity_score: float = Field(ge=0, le=1)
    reasons: list[str]


class NetworkNode(BaseModel):
    id: str
    label: str
    kind: str


class NetworkEdge(BaseModel):
    source: str
    target: str
    type: str
    confidence: float


class NetworkOut(BaseModel):
    ticker: str
    nodes: list[NetworkNode]
    edges: list[NetworkEdge]


class HealthOut(BaseModel):
    status: str
    app: str

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.models import Company, Event, FinancialFactor
from app.db.session import get_db
from app.schemas import (
    CompanyOut,
    EventOut,
    ExplanationOut,
    FactorOut,
    HealthOut,
    NetworkOut,
    RelationshipOut,
    SignalOut,
    SimilarCompanyOut,
    ThesisOut,
)
from app.services.intelligence import (
    build_explanation,
    build_network,
    build_thesis,
    find_similar_companies,
    get_company_or_none,
    latest_signals,
    list_relationships,
    normalize_ticker,
)

router = APIRouter()


def require_company(db: Session, ticker: str) -> Company:
    company = get_company_or_none(db, ticker)
    if company is None:
        raise HTTPException(status_code=404, detail=f"No company found for ticker {normalize_ticker(ticker)}")
    return company


@router.get("/health", response_model=HealthOut, tags=["system"])
def health(settings: Settings = Depends(get_settings)) -> HealthOut:
    return HealthOut(status="ok", app=settings.app_name)


@router.get("/companies", response_model=list[CompanyOut], tags=["companies"])
def list_companies(db: Session = Depends(get_db)) -> list[Company]:
    return list(db.scalars(select(Company).order_by(Company.ticker)).all())


@router.get("/companies/{ticker}", response_model=CompanyOut, tags=["companies"])
def get_company(ticker: str, db: Session = Depends(get_db)) -> Company:
    return require_company(db, ticker)


@router.get("/companies/{ticker}/relationships", response_model=list[RelationshipOut], tags=["intelligence"])
def get_relationships(ticker: str, db: Session = Depends(get_db)) -> list[RelationshipOut]:
    return list_relationships(db, require_company(db, ticker))


@router.get("/companies/{ticker}/factors", response_model=list[FactorOut], tags=["intelligence"])
def get_factors(ticker: str, db: Session = Depends(get_db)) -> list[FinancialFactor]:
    normalized = normalize_ticker(ticker)
    require_company(db, normalized)
    return list(
        db.scalars(
            select(FinancialFactor)
            .where(FinancialFactor.ticker == normalized)
            .order_by(FinancialFactor.factor_date.desc(), FinancialFactor.factor_name)
        ).all()
    )


@router.get("/companies/{ticker}/events", response_model=list[EventOut], tags=["intelligence"])
def get_events(ticker: str, db: Session = Depends(get_db)) -> list[Event]:
    normalized = normalize_ticker(ticker)
    require_company(db, normalized)
    return list(db.scalars(select(Event).where(Event.ticker == normalized).order_by(Event.event_date.desc())).all())


@router.get("/companies/{ticker}/signals", response_model=list[SignalOut], tags=["intelligence"])
def get_signals(ticker: str, db: Session = Depends(get_db)) -> list:
    normalized = normalize_ticker(ticker)
    require_company(db, normalized)
    return latest_signals(db, normalized)


@router.get("/companies/{ticker}/explain", response_model=ExplanationOut, tags=["ai-services"])
def explain_company(ticker: str, db: Session = Depends(get_db)) -> ExplanationOut:
    return build_explanation(db, require_company(db, ticker))


@router.get("/companies/{ticker}/thesis", response_model=ThesisOut, tags=["ai-services"])
def get_thesis(ticker: str, db: Session = Depends(get_db)) -> ThesisOut:
    return build_thesis(db, require_company(db, ticker))


@router.get("/companies/{ticker}/similar", response_model=list[SimilarCompanyOut], tags=["ai-services"])
def get_similar(ticker: str, db: Session = Depends(get_db)) -> list[SimilarCompanyOut]:
    return find_similar_companies(db, require_company(db, ticker))


@router.get("/network/{ticker}", response_model=NetworkOut, tags=["network"])
def get_network(ticker: str, db: Session = Depends(get_db)) -> NetworkOut:
    return build_network(db, require_company(db, ticker))

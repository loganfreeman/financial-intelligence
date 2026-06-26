from datetime import date, timedelta
from math import sin

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Company, Event, FinancialFactor, MarketPrice, Relationship, Signal


COMPANIES = [
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics", "exchange": "NASDAQ", "cik": "0000320193"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "industry": "Software", "exchange": "NASDAQ", "cik": "0000789019"},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors", "exchange": "NASDAQ", "cik": "0001045810"},
    {"ticker": "AMD", "name": "Advanced Micro Devices, Inc.", "sector": "Technology", "industry": "Semiconductors", "exchange": "NASDAQ", "cik": "0000002488"},
    {"ticker": "TSM", "name": "Taiwan Semiconductor Manufacturing Company", "sector": "Technology", "industry": "Semiconductors", "exchange": "NYSE", "cik": None},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Communication Services", "industry": "Internet Content", "exchange": "NASDAQ", "cik": "0001652044"},
    {"ticker": "AMZN", "name": "Amazon.com, Inc.", "sector": "Consumer Discretionary", "industry": "Internet Retail", "exchange": "NASDAQ", "cik": "0001018724"},
]

RELATIONSHIPS = [
    ("NVDA", "COMPETES_WITH", "AMD", 0.92),
    ("NVDA", "SUPPLIER_DEPENDENCY", "TSM", 0.95),
    ("NVDA", "MACRO_EXPOSURE", "AI infrastructure spending", 0.91),
    ("NVDA", "MACRO_EXPOSURE", "Semiconductor cycle", 0.87),
    ("AMD", "COMPETES_WITH", "NVDA", 0.92),
    ("AMD", "SUPPLIER_DEPENDENCY", "TSM", 0.9),
    ("AAPL", "COMPETES_WITH", "MSFT", 0.68),
    ("AAPL", "SUPPLIER_DEPENDENCY", "TSM", 0.82),
    ("AAPL", "MACRO_EXPOSURE", "Consumer spending", 0.84),
    ("MSFT", "COMPETES_WITH", "GOOGL", 0.79),
    ("MSFT", "MACRO_EXPOSURE", "Enterprise software budgets", 0.86),
    ("GOOGL", "COMPETES_WITH", "MSFT", 0.76),
    ("GOOGL", "MACRO_EXPOSURE", "Digital advertising demand", 0.9),
    ("AMZN", "MACRO_EXPOSURE", "Consumer spending", 0.88),
    ("AMZN", "MACRO_EXPOSURE", "Cloud infrastructure spending", 0.84),
]

EVENTS = [
    ("NVDA", "EARNINGS", "Data center growth remains the key driver", "Recent intelligence highlights data center demand as the dominant catalyst for NVIDIA."),
    ("AAPL", "PRODUCT", "Hardware refresh cycle in focus", "Investor attention is centered on device replacement demand and services attachment."),
    ("MSFT", "CLOUD", "Cloud and AI platform spend support growth", "Enterprise cloud demand remains a central part of the Microsoft thesis."),
    ("AMZN", "MARGIN", "Retail margins and cloud growth shape outlook", "Operating leverage and AWS demand remain the primary factors to monitor."),
]


def seed_database(db: Session) -> None:
    if db.scalar(select(Company).limit(1)):
        return

    companies_by_ticker: dict[str, Company] = {}
    for item in COMPANIES:
        company = Company(**item)
        db.add(company)
        companies_by_ticker[item["ticker"]] = company
    db.flush()

    for source_ticker, rel_type, target, confidence in RELATIONSHIPS:
        target_company = companies_by_ticker.get(target)
        db.add(
            Relationship(
                source_company_id=companies_by_ticker[source_ticker].id,
                target_company_id=target_company.id if target_company else None,
                relationship_type=rel_type,
                target_label=target_company.name if target_company else target,
                confidence=confidence,
                source="seed",
            )
        )

    today = date.today()
    for ticker, event_type, title, summary in EVENTS:
        db.add(
            Event(
                ticker=ticker,
                event_date=today - timedelta(days=7),
                event_type=event_type,
                title=title,
                summary=summary,
                source_url=None,
            )
        )

    for company in COMPANIES:
        _seed_prices(db, company["ticker"], today)
        _seed_factors_and_signals(db, company["ticker"], today)

    db.commit()


def _seed_prices(db: Session, ticker: str, today: date) -> None:
    base = 80 + (sum(ord(char) for char in ticker) % 180)
    drift = 0.002 + (len(ticker) * 0.0004)
    for offset in range(90):
        price_date = today - timedelta(days=90 - offset)
        seasonal = sin(offset / 7) * 2.5
        close = round(base * (1 + drift * offset) + seasonal, 2)
        db.add(
            MarketPrice(
                ticker=ticker,
                price_date=price_date,
                open=round(close * 0.995, 2),
                high=round(close * 1.015, 2),
                low=round(close * 0.985, 2),
                close=close,
                volume=1_000_000 + offset * 12_500,
            )
        )


def _seed_factors_and_signals(db: Session, ticker: str, today: date) -> None:
    quality = 60 + (sum(ord(char) for char in ticker) % 35)
    momentum = 55 + (len(ticker) * 7)
    volatility = 100 - min(95, quality)
    factors = {
        "quality": quality,
        "momentum": min(momentum, 95),
        "volatility": volatility,
        "growth": min(quality + 6, 98),
        "value": max(20, 100 - quality),
    }
    for name, value in factors.items():
        db.add(FinancialFactor(ticker=ticker, factor_date=today, factor_name=name, factor_value=float(value)))

    trend_score = min(1.0, (factors["momentum"] - 50) / 50)
    db.add(
        Signal(
            ticker=ticker,
            signal_date=today,
            category="trend",
            score=round(trend_score, 2),
            confidence=0.72,
            explanation=f"{ticker} has positive seeded momentum and a constructive short-term trend profile.",
        )
    )

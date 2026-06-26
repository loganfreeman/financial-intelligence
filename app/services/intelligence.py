from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Company, Event, FinancialFactor, Relationship, Signal
from app.schemas import ExplanationOut, NetworkEdge, NetworkNode, NetworkOut, RelationshipOut, SimilarCompanyOut, ThesisOut


def normalize_ticker(ticker: str) -> str:
    return ticker.strip().upper()


def get_company_or_none(db: Session, ticker: str) -> Company | None:
    return db.scalar(select(Company).where(Company.ticker == normalize_ticker(ticker)))


def list_relationships(db: Session, company: Company) -> list[RelationshipOut]:
    rows = db.scalars(select(Relationship).where(Relationship.source_company_id == company.id)).all()
    return [
        RelationshipOut(
            type=row.relationship_type,
            target=row.target_label,
            target_ticker=row.target_company.ticker if row.target_company else None,
            confidence=row.confidence,
            source=row.source,
        )
        for row in rows
    ]


def build_explanation(db: Session, company: Company) -> ExplanationOut:
    factors = db.scalars(select(FinancialFactor).where(FinancialFactor.ticker == company.ticker)).all()
    events = db.scalars(select(Event).where(Event.ticker == company.ticker).order_by(Event.event_date.desc()).limit(3)).all()
    relationships = list_relationships(db, company)

    strongest = sorted(factors, key=lambda item: item.factor_value, reverse=True)[:2]
    summary = [f"{factor.factor_name.title()} score is {factor.factor_value:.0f}" for factor in strongest]
    summary.extend(event.title for event in events[:2])
    if not summary:
        summary.append(f"{company.ticker} has limited intelligence coverage in the current dataset")

    affected_sectors = sorted({company.sector or "Unknown"} | {rel.target for rel in relationships if "EXPOSURE" in rel.type})
    return ExplanationOut(
        ticker=company.ticker,
        summary=summary,
        citations=[event.source_url for event in events if event.source_url],
        affected_sectors=affected_sectors,
    )


def build_thesis(db: Session, company: Company) -> ThesisOut:
    factors = {row.factor_name: row.factor_value for row in db.scalars(select(FinancialFactor).where(FinancialFactor.ticker == company.ticker)).all()}
    relationships = list_relationships(db, company)
    exposures = [rel.target for rel in relationships if "EXPOSURE" in rel.type]

    return ThesisOut(
        ticker=company.ticker,
        bull_case=[
            f"Momentum score of {factors.get('momentum', 0):.0f} supports a constructive setup.",
            f"Growth score of {factors.get('growth', 0):.0f} suggests durable expansion potential.",
        ],
        bear_case=[
            f"Value score of {factors.get('value', 0):.0f} may indicate valuation sensitivity.",
            "Competitive pressure remains a key monitoring item.",
        ],
        risks=exposures[:3] or ["Insufficient exposure data in current dataset."],
        catalysts=["Earnings revisions", "Product demand", "Macro regime changes"],
        valuation=["Seeded valuation view only; connect fundamentals ingestion for production valuation."],
    )


def find_similar_companies(db: Session, company: Company) -> list[SimilarCompanyOut]:
    candidates = db.scalars(select(Company).where(Company.ticker != company.ticker)).all()
    results: list[SimilarCompanyOut] = []
    for candidate in candidates:
        score = 0.35
        reasons: list[str] = []
        if candidate.sector == company.sector:
            score += 0.3
            reasons.append("same sector")
        if candidate.industry == company.industry:
            score += 0.25
            reasons.append("same industry")
        if not reasons:
            reasons.append("cross-sector intelligence universe")
        results.append(
            SimilarCompanyOut(
                ticker=candidate.ticker,
                name=candidate.name,
                similarity_score=round(min(score, 0.98), 2),
                reasons=reasons,
            )
        )
    return sorted(results, key=lambda item: item.similarity_score, reverse=True)[:5]


def build_network(db: Session, company: Company) -> NetworkOut:
    relationships = list_relationships(db, company)
    nodes = {company.ticker: NetworkNode(id=company.ticker, label=company.name, kind="company")}
    edges: list[NetworkEdge] = []
    for rel in relationships:
        node_id = rel.target_ticker or rel.target
        nodes[node_id] = NetworkNode(id=node_id, label=rel.target, kind="company" if rel.target_ticker else "concept")
        edges.append(NetworkEdge(source=company.ticker, target=node_id, type=rel.type, confidence=rel.confidence))
    return NetworkOut(ticker=company.ticker, nodes=list(nodes.values()), edges=edges)


def latest_signals(db: Session, ticker: str) -> list[Signal]:
    return db.scalars(select(Signal).where(Signal.ticker == normalize_ticker(ticker)).order_by(Signal.signal_date.desc())).all()

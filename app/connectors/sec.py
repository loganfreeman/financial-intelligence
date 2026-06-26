from dataclasses import dataclass


@dataclass(frozen=True)
class SecConnector:
    user_agent: str
    name: str = "sec"

    def headers(self) -> dict[str, str]:
        return {"User-Agent": self.user_agent, "Accept-Encoding": "gzip, deflate"}

    def company_facts_url(self, cik: str) -> str:
        normalized = cik.lstrip("0").zfill(10)
        return f"https://data.sec.gov/api/xbrl/companyfacts/CIK{normalized}.json"

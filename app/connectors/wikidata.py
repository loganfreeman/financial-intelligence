from dataclasses import dataclass


@dataclass(frozen=True)
class WikidataConnector:
    name: str = "wikidata"

    def company_search_query(self, ticker: str) -> str:
        return f"""
        SELECT ?company ?companyLabel WHERE {{
          ?company wdt:P414 ?exchange;
                   wdt:P249 "{ticker.upper()}".
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 10
        """.strip()

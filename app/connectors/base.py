from typing import Protocol


class Connector(Protocol):
    name: str

    def fetch(self, ticker: str) -> dict:
        """Fetch source data for a ticker."""

from src.domain.price_report import PriceReport
from src.ports.repository import ReportRepository


class QueryPriceReportUseCase:
    def __init__(self, repository: ReportRepository[PriceReport]) -> None:
        self._repository = repository

    def execute(self, ticker: str, date_str: str) -> list[PriceReport]:
        return self._repository.find_by_ticker(ticker, date_str)

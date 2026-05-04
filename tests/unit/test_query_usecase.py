from src.domain.price_report import PriceReport
from src.usecases.query_price_report import QueryPriceReportUseCase


class _Repository:
    def __init__(self, records: list[PriceReport]):
        self._records = records
        self.calls: list[tuple] = []

    def save(self, reports: list[PriceReport]) -> int:
        return 0

    def find_by_ticker(self, ticker: str, date_str: str) -> list[PriceReport]:
        self.calls.append((ticker, date_str))
        return [r for r in self._records if r.ticker == ticker]


def _make_report(ticker: str) -> PriceReport:
    return PriceReport(ticker, "2026-04-16", "f.xml", 1, "", None, None)


def test_execute_delega_ao_repositorio():
    repo = _Repository([_make_report("PETR4")])
    uc = QueryPriceReportUseCase(repository=repo)
    uc.execute("PETR4", "2026-04-16")
    assert repo.calls == [("PETR4", "2026-04-16")]


def test_execute_retorna_registros_do_ticker():
    repo = _Repository([_make_report("PETR4"), _make_report("VALE3")])
    uc = QueryPriceReportUseCase(repository=repo)
    result = uc.execute("PETR4", "2026-04-16")
    assert len(result) == 1
    assert result[0].ticker == "PETR4"


def test_execute_retorna_lista_vazia_quando_ticker_nao_existe():
    repo = _Repository([])
    uc = QueryPriceReportUseCase(repository=repo)
    assert uc.execute("XXXX99", "2026-04-16") == []

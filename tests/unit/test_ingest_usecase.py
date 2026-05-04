from src.domain.price_report import PriceReport
from src.usecases.ingest_price_report import IngestPriceReportUseCase


# ── Mocks que satisfazem os Protocols por estrutura (sem herança) ──────────

class _Downloader:
    def __init__(self, path: str | None):
        self._path = path
        self.calls: list[str] = []

    def download(self, date_str: str) -> str | None:
        self.calls.append(date_str)
        return self._path


class _Extractor:
    def __init__(self, directory: str = "/tmp/extracted"):
        self._directory = directory
        self.calls: list[tuple] = []

    def extract(self, zip_path: str, date_str: str) -> str:
        self.calls.append((zip_path, date_str))
        return self._directory


class _Parser:
    def __init__(self, reports: list[PriceReport]):
        self._reports = reports
        self.calls: list[str] = []

    def parse(self, directory: str) -> list[PriceReport]:
        self.calls.append(directory)
        return self._reports


class _Repository:
    def __init__(self):
        self.saved: list[PriceReport] = []

    def save(self, reports: list[PriceReport]) -> int:
        self.saved.extend(reports)
        return len(reports)

    def find_by_ticker(self, ticker: str, date_str: str) -> list[PriceReport]:
        return []


def _make_report(ticker: str = "PETR4") -> PriceReport:
    return PriceReport(ticker, "2026-04-16", "f.xml", 1, "", None, None)


# ── Testes ─────────────────────────────────────────────────────────────────

def test_execute_retorna_zero_quando_download_falha():
    uc = IngestPriceReportUseCase(
        downloader=_Downloader(path=None),
        extractor=_Extractor(),
        parser=_Parser([]),
        repository=_Repository(),
    )
    assert uc.execute("2026-04-16") == 0


def test_execute_nao_chama_extractor_quando_download_falha():
    extractor = _Extractor()
    uc = IngestPriceReportUseCase(
        downloader=_Downloader(path=None),
        extractor=extractor,
        parser=_Parser([]),
        repository=_Repository(),
    )
    uc.execute("2026-04-16")
    assert extractor.calls == []


def test_execute_passa_zip_path_para_extractor():
    extractor = _Extractor()
    uc = IngestPriceReportUseCase(
        downloader=_Downloader(path="/downloads/PR260416.zip"),
        extractor=extractor,
        parser=_Parser([]),
        repository=_Repository(),
    )
    uc.execute("2026-04-16")
    assert extractor.calls == [("/downloads/PR260416.zip", "2026-04-16")]


def test_execute_passa_diretorio_para_parser():
    parser = _Parser([])
    uc = IngestPriceReportUseCase(
        downloader=_Downloader(path="/downloads/f.zip"),
        extractor=_Extractor(directory="/extracted/2026-04-16"),
        parser=parser,
        repository=_Repository(),
    )
    uc.execute("2026-04-16")
    assert parser.calls == ["/extracted/2026-04-16"]


def test_execute_persiste_registros_e_retorna_contagem():
    reports = [_make_report("PETR4"), _make_report("VALE3")]
    repo = _Repository()
    uc = IngestPriceReportUseCase(
        downloader=_Downloader(path="/f.zip"),
        extractor=_Extractor(),
        parser=_Parser(reports),
        repository=repo,
    )
    assert uc.execute("2026-04-16") == 2
    assert len(repo.saved) == 2


def test_execute_retorna_zero_quando_parser_retorna_vazio():
    repo = _Repository()
    uc = IngestPriceReportUseCase(
        downloader=_Downloader(path="/f.zip"),
        extractor=_Extractor(),
        parser=_Parser([]),
        repository=repo,
    )
    assert uc.execute("2026-04-16") == 0
    assert repo.saved == []

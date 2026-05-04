from src.domain.price_report import PriceReport
from src.logger import get_logger
from src.ports.downloader import FileDownloader
from src.ports.extractor import FileExtractor
from src.ports.parser import ReportParser
from src.ports.repository import ReportRepository

_log = get_logger(__name__)


class IngestPriceReportUseCase:
    def __init__(
        self,
        downloader: FileDownloader,
        extractor: FileExtractor,
        parser: ReportParser[PriceReport],
        repository: ReportRepository[PriceReport],
    ) -> None:
        self._downloader = downloader
        self._extractor = extractor
        self._parser = parser
        self._repository = repository

    def execute(self, date_str: str) -> int:
        _log.info("pipeline_started", date=date_str)

        zip_path = self._downloader.download(date_str)
        if not zip_path:
            _log.error("pipeline_aborted", reason="download_failed", date=date_str)
            return 0

        directory = self._extractor.extract(zip_path, date_str)
        reports = self._parser.parse(directory)
        saved = self._repository.save(reports)

        _log.info("pipeline_complete", date=date_str, records=saved)
        return saved

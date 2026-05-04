import argparse
from datetime import datetime

import uvicorn

from src.logger import configure_logging
configure_logging()

from src.config import SRC_DOWNLOADS, SRC_EXTRAIDOS
from src.infra.bvbg086_parser import BVBG086Parser
from src.infra.exchange_downloader import ExchangeFileDownloader
from src.infra.parquet_repository import ParquetRepository
from src.infra.zip_extractor import ZipExtractor
from src.usecases.ingest_price_report import IngestPriceReportUseCase


def _build_ingest_use_case() -> IngestPriceReportUseCase:
    return IngestPriceReportUseCase(
        downloader=ExchangeFileDownloader(SRC_DOWNLOADS),
        extractor=ZipExtractor(SRC_EXTRAIDOS),
        parser=BVBG086Parser(),
        repository=ParquetRepository(SRC_EXTRAIDOS),
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline Post-Trade Market Data — BVBG.086")
    parser.add_argument(
        "--data",
        type=str,
        default=datetime.today().strftime("%Y-%m-%d"),
        help="Data do pregão no formato YYYY-MM-DD (default: hoje)",
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Inicia a API FastAPI após o pipeline",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    print(f"📅 Data do pregão: {args.data}")

    _build_ingest_use_case().execute(args.data)

    if args.api:
        uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=False)

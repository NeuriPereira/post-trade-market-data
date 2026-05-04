from fastapi import Depends, FastAPI, HTTPException, Query

from src.config import SRC_DOWNLOADS, SRC_EXTRAIDOS
from src.logger import configure_logging, get_logger

configure_logging()
_log = get_logger(__name__)
from src.infra.bvbg086_parser import BVBG086Parser
from src.infra.exchange_downloader import ExchangeFileDownloader
from src.infra.parquet_repository import ParquetRepository
from src.infra.zip_extractor import ZipExtractor
from src.usecases.ingest_price_report import IngestPriceReportUseCase
from src.usecases.query_price_report import QueryPriceReportUseCase

app = FastAPI(title="Post-Trade Market Data API")


def _ingest_use_case() -> IngestPriceReportUseCase:
    return IngestPriceReportUseCase(
        downloader=ExchangeFileDownloader(SRC_DOWNLOADS),
        extractor=ZipExtractor(SRC_EXTRAIDOS),
        parser=BVBG086Parser(),
        repository=ParquetRepository(SRC_EXTRAIDOS),
    )


def _query_use_case() -> QueryPriceReportUseCase:
    return QueryPriceReportUseCase(
        repository=ParquetRepository(SRC_EXTRAIDOS),
    )


@app.post("/pipeline/run")
def run_pipeline(
    data: str = Query(..., description="Data no formato YYYY-MM-DD"),
    use_case: IngestPriceReportUseCase = Depends(_ingest_use_case),
):
    saved = use_case.execute(data)
    if not saved:
        raise HTTPException(status_code=422, detail=f"Nenhum registro extraído para {data}.")
    return {"status": "ok", "data": data, "registros": saved}


@app.get("/ativos/{ticker}")
def get_ativo(
    ticker: str,
    data: str = Query(..., description="Data no formato YYYY-MM-DD"),
    use_case: QueryPriceReportUseCase = Depends(_query_use_case),
):
    reports = use_case.execute(ticker, data)
    if not reports:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    return [
        {
            "ticker": r.ticker,
            "trade_date": r.trade_date,
            "source_file": r.source_file,
            "file_seq": r.file_seq,
            "processed_at": r.processed_at,
            "codigo": r.codigo,
            "trad_qty": r.trad_qty,
            **r.attributes,
        }
        for r in reports
    ]

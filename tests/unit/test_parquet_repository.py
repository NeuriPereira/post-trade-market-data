import pytest
from src.domain.price_report import PriceReport
from src.infra.parquet_repository import ParquetRepository


def _make_report(ticker: str, trade_date: str = "2026-04-16", file_seq: int = 1) -> PriceReport:
    return PriceReport(
        ticker=ticker,
        trade_date=trade_date,
        source_file="BVBG.086.01_BV000328202604160328000001839436960.xml",
        file_seq=file_seq,
        processed_at="2026-04-16T20:30:00.000000",
        codigo="123456789",
        trad_qty="1000",
        attributes={"opn_intrst": "500.0", "best_bid_pric": "10.50"},
    )


@pytest.fixture
def repo(tmp_path):
    return ParquetRepository(base_dir=str(tmp_path))


# ── save ───────────────────────────────────────────────────────────────────

def test_save_retorna_contagem_de_registros(repo):
    reports = [_make_report("PETR4"), _make_report("VALE3")]
    assert repo.save(reports) == 2


def test_save_lista_vazia_retorna_zero(repo):
    assert repo.save([]) == 0


def test_save_cria_arquivo_parquet(repo, tmp_path):
    repo.save([_make_report("PETR4")])
    parquet = tmp_path / "2026-04-16" / "price_report.parquet"
    assert parquet.exists()


# ── find_by_ticker ─────────────────────────────────────────────────────────

def test_find_by_ticker_retorna_registro_correto(repo):
    repo.save([_make_report("PETR4"), _make_report("VALE3")])
    result = repo.find_by_ticker("PETR4", "2026-04-16")
    assert len(result) == 1
    assert result[0].ticker == "PETR4"


def test_find_by_ticker_retorna_vazio_quando_ticker_nao_existe(repo):
    repo.save([_make_report("PETR4")])
    assert repo.find_by_ticker("XXXX99", "2026-04-16") == []


def test_find_by_ticker_retorna_vazio_quando_parquet_nao_existe(repo):
    assert repo.find_by_ticker("PETR4", "2099-01-01") == []


def test_find_by_ticker_restaura_atributos_dinamicos(repo):
    repo.save([_make_report("PETR4")])
    result = repo.find_by_ticker("PETR4", "2026-04-16")
    assert result[0].attributes.get("opn_intrst") is not None


def test_find_by_ticker_sem_nan_nos_campos(repo):
    import math
    repo.save([_make_report("PETR4")])
    result = repo.find_by_ticker("PETR4", "2026-04-16")
    r = result[0]
    for v in r.attributes.values():
        assert not (isinstance(v, float) and math.isnan(v))


def test_save_multiplas_datas_cria_arquivos_separados(repo, tmp_path):
    repo.save([
        _make_report("PETR4", trade_date="2026-04-16"),
        _make_report("VALE3", trade_date="2026-04-17"),
    ])
    assert (tmp_path / "2026-04-16" / "price_report.parquet").exists()
    assert (tmp_path / "2026-04-17" / "price_report.parquet").exists()

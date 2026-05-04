import os
import pytest
from src.infra.bvbg086_parser import BVBG086Parser, _parse_filename_meta, _to_snake

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")
FIXTURE_XML = os.path.join(
    FIXTURES_DIR,
    "BVBG.086.01_BV000328202604160328000001839436960.xml",
)


# ── _to_snake ──────────────────────────────────────────────────────────────

def test_to_snake_camel_simples():
    assert _to_snake("OpnIntrst") == "opn_intrst"


def test_to_snake_ja_e_minusculo():
    assert _to_snake("ticker") == "ticker"


def test_to_snake_primeira_letra_maiuscula():
    assert _to_snake("BestBidPric") == "best_bid_pric"


# ── _parse_filename_meta ───────────────────────────────────────────────────

def test_parse_filename_extrai_file_seq():
    nome, date, seq, _ = _parse_filename_meta(
        "BVBG.086.01_BV000328202604160328000001839436960.xml"
    )
    assert seq == 1839436960


def test_parse_filename_extrai_data():
    _, date, _, _ = _parse_filename_meta(
        "BVBG.086.01_BV000328202604160328000001839436960.xml"
    )
    assert date == "2026-04-16"


def test_parse_filename_nome_invalido_retorna_none():
    _, date, seq, _ = _parse_filename_meta("arquivo_sem_padrao.xml")
    assert date is None
    assert seq is None


# ── BVBG086Parser.parse ────────────────────────────────────────────────────

@pytest.fixture
def reports():
    return BVBG086Parser().parse(FIXTURES_DIR)


def test_parse_retorna_dois_registros(reports):
    assert len(reports) == 2


def test_parse_extrai_ticker_corretamente(reports):
    tickers = {r.ticker for r in reports}
    assert tickers == {"PETR4", "VALE3"}


def test_parse_extrai_file_seq_do_nome(reports):
    for r in reports:
        assert r.file_seq == 1839436960


def test_parse_extrai_trade_date_do_nome_do_arquivo(reports):
    for r in reports:
        assert r.trade_date == "2026-04-16"


def test_parse_extrai_codigo(reports):
    petr4 = next(r for r in reports if r.ticker == "PETR4")
    assert petr4.codigo == "123456789"


def test_parse_extrai_atributos_dinamicos(reports):
    petr4 = next(r for r in reports if r.ticker == "PETR4")
    assert "opn_intrst" in petr4.attributes
    assert petr4.attributes["opn_intrst"] == "500.0"


def test_parse_extrai_atributo_com_atributo_xml(reports):
    petr4 = next(r for r in reports if r.ticker == "PETR4")
    # BestBidPric tem atributo Ccy="BRL" → best_bid_pric_ccy
    assert petr4.attributes.get("best_bid_pric_ccy") == "BRL"


def test_parse_pasta_vazia_retorna_lista_vazia(tmp_path):
    assert BVBG086Parser().parse(str(tmp_path)) == []

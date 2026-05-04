from src.domain.price_report import PriceReport


def test_price_report_instancia_com_campos_obrigatorios():
    r = PriceReport(
        ticker="PETR4",
        trade_date="2026-04-16",
        source_file="BVBG.086.01_BV000328202604160328000001839436960.xml",
        file_seq=1839436960,
        processed_at="2026-04-16T20:30:00.000000",
        codigo="123456789",
        trad_qty="1000",
    )
    assert r.ticker == "PETR4"
    assert r.file_seq == 1839436960
    assert r.attributes == {}


def test_price_report_attributes_default_e_independente():
    r1 = PriceReport("A", None, "f.xml", None, "", None, None)
    r2 = PriceReport("B", None, "f.xml", None, "", None, None)
    r1.attributes["x"] = 1
    assert "x" not in r2.attributes  # default_factory garante dicts separados


def test_price_report_campos_opcionais_aceitam_none():
    r = PriceReport(
        ticker=None,
        trade_date=None,
        source_file="f.xml",
        file_seq=None,
        processed_at="",
        codigo=None,
        trad_qty=None,
    )
    assert r.ticker is None
    assert r.file_seq is None


def test_price_report_igualdade_por_valor():
    kwargs = dict(ticker="PETR4", trade_date="2026-04-16", source_file="f.xml",
                  file_seq=1, processed_at="", codigo=None, trad_qty=None)
    assert PriceReport(**kwargs) == PriceReport(**kwargs)

from dataclasses import dataclass, field


@dataclass
class PriceReport:
    ticker: str | None
    trade_date: str | None
    source_file: str
    file_seq: int | None
    processed_at: str
    codigo: str | None
    trad_qty: str | None
    attributes: dict = field(default_factory=dict)

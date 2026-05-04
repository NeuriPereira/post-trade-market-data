import math
import os
from dataclasses import asdict

import pandas as pd

from src.domain.price_report import PriceReport


class ParquetRepository:
    def __init__(self, base_dir: str) -> None:
        self._base_dir = base_dir

    def _path(self, date_str: str) -> str:
        return os.path.join(self._base_dir, date_str, "price_report.parquet")

    def save(self, reports: list[PriceReport]) -> int:
        if not reports:
            return 0

        dates = {r.trade_date or "unknown" for r in reports}
        for date_str in dates:
            subset = [r for r in reports if (r.trade_date or "unknown") == date_str]
            rows = []
            for r in subset:
                row = asdict(r)
                attrs = row.pop("attributes", {})
                row.update(attrs)
                rows.append(row)

            df = pd.DataFrame(rows)
            for col in df.columns:
                converted = pd.to_numeric(df[col], errors="coerce")
                non_null = df[col].dropna()
                if len(non_null) > 0 and converted.dropna().shape[0] == non_null.shape[0]:
                    df[col] = converted

            path = self._path(date_str)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            df.to_parquet(path, index=False)
            print(f"✅ Parquet salvo: {path} ({len(subset)} registros)")

        return len(reports)

    def find_by_ticker(self, ticker: str, date_str: str) -> list[PriceReport]:
        path = self._path(date_str)
        if not os.path.exists(path):
            return []

        df = pd.read_parquet(path)
        matches = df[df["ticker"] == ticker]

        known = {"ticker", "trade_date", "source_file", "file_seq", "processed_at", "codigo", "trad_qty"}
        results: list[PriceReport] = []
        for _, row in matches.iterrows():
            d = {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in row.to_dict().items()}
            attributes = {k: v for k, v in d.items() if k not in known}
            results.append(PriceReport(
                ticker=d.get("ticker"),
                trade_date=d.get("trade_date"),
                source_file=d.get("source_file", ""),
                file_seq=d.get("file_seq"),
                processed_at=d.get("processed_at", ""),
                codigo=d.get("codigo"),
                trad_qty=d.get("trad_qty"),
                attributes=attributes,
            ))
        return results

import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime

from src.domain.price_report import PriceReport
from src.logger import get_logger

_log = get_logger(__name__)
_NS = {"bvmf": "urn:bvmf.217.01.xsd"}
_FILENAME_PATTERN = re.compile(r"BV(\d{6})(\d{8})(\d{4})(\d+)\.xml")


def _get_text(elem, xpath: str) -> str | None:
    el = elem.find(xpath, _NS)
    return el.text if el is not None else None


def _to_snake(text: str) -> str:
    return "".join(["_" + c.lower() if c.isupper() else c for c in text]).lstrip("_")


def _parse_filename_meta(path: str) -> tuple[str, str | None, int | None, str]:
    nome = os.path.basename(path)
    file_date: str | None = None
    file_seq: int | None = None
    processed_at = datetime.now().isoformat(timespec="microseconds")
    m = _FILENAME_PATTERN.search(nome)
    if m:
        _, date_raw, _, seq_raw = m.groups()
        try:
            file_date = datetime.strptime(date_raw, "%Y%m%d").strftime("%Y-%m-%d")
        except ValueError:
            pass
        try:
            file_seq = int(seq_raw)
        except ValueError:
            pass
    return nome, file_date, file_seq, processed_at


class BVBG086Parser:
    def parse(self, directory: str) -> list[PriceReport]:
        reports: list[PriceReport] = []
        for root, _, files in os.walk(directory):
            for nome in sorted(files):
                if nome.endswith(".xml"):
                    path = os.path.join(root, nome)
                    file_reports = self._parse_file(path)
                    _log.info("file_parsed", path=path, records=len(file_reports))
                    reports.extend(file_reports)
        return reports

    def _parse_file(self, path: str) -> list[PriceReport]:
        source_file, file_date, file_seq, processed_at = _parse_filename_meta(path)
        reports: list[PriceReport] = []
        errors = 0

        for _, elem in ET.iterparse(path, events=("end",)):
            if not elem.tag.endswith("PricRpt"):
                continue
            try:
                attributes: dict = {}
                fin_attr = elem.find("bvmf:FinInstrmAttrbts", _NS)
                if fin_attr is not None:
                    for child in fin_attr:
                        tag = _to_snake(child.tag.split("}")[-1])
                        attributes[tag] = child.text
                        for k, v in child.attrib.items():
                            attributes[f"{tag}_{k.lower()}"] = v

                reports.append(PriceReport(
                    ticker=_get_text(elem, "bvmf:SctyId/bvmf:TckrSymb"),
                    trade_date=file_date,
                    source_file=source_file,
                    file_seq=file_seq,
                    processed_at=processed_at,
                    codigo=_get_text(elem, "bvmf:FinInstrmId/bvmf:OthrId/bvmf:Id"),
                    trad_qty=_get_text(elem, "bvmf:TradDtls/bvmf:TradQty"),
                    attributes=attributes,
                ))
            except Exception as e:
                errors += 1
                _log.warning("record_parse_error", error=str(e), file=source_file)
            finally:
                elem.clear()

        if errors:
            _log.warning("file_parse_errors", file=source_file, errors=errors)
        return reports

from typing import Protocol


class FileExtractor(Protocol):
    def extract(self, zip_path: str, date_str: str) -> str:
        ...

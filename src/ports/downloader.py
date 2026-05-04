from typing import Protocol


class FileDownloader(Protocol):
    def download(self, date_str: str) -> str | None:
        ...

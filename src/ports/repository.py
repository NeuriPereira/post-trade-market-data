from typing import Protocol, TypeVar

T = TypeVar("T")


class ReportRepository(Protocol[T]):
    def save(self, reports: list[T]) -> int:
        ...

    def find_by_ticker(self, ticker: str, date_str: str) -> list[T]:
        ...

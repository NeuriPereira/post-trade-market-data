from typing import Protocol, TypeVar

T = TypeVar("T")


class ReportParser(Protocol[T]):
    def parse(self, directory: str) -> list[T]:
        ...

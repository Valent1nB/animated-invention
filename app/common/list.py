from typing import Sequence

from pydantic import BaseModel


class ListResult[T](BaseModel):
    items: Sequence[T]
    total: int

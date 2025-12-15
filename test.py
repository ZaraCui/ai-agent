from pydantic import BaseModel
from typing import List

class MyModel(BaseModel):
    name: str
    items: List[str]

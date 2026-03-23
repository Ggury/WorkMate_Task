from dataclasses import dataclass
from datetime import datetime


@dataclass
class Cell:
    name: str
    date: datetime
    coffee_spent: int
    sleep_hours: float
    study_hours: float
    mood: str
    exam: str

from pydantic import BaseModel
from datetime import datetime

class User_data(BaseModel):
    hotelName: str | None = ""
    hotelPhone: str | None = ""
    name: str | None = ""
    cpf: str | None = ""
    bookCode: str | None = ""
    checkIn: datetime | None = ""
    checkOut: datetime | None = ""
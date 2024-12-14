from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ContactBase(BaseModel):
  first_name: str = Field(max_length=50)
  last_name: str = Field(max_length=50)
  email: str = Field(max_length=50)
  phone: str = Field(max_length=50)
  birthday: datetime | None

class ContactResponse(ContactBase):
  id: int

  model_config = ConfigDict(from_attributes=True)

# schemas.py
from pydantic import BaseModel  # pylint: disable=E0611
from datetime import datetime
# UserOut is a Pydantic model used to define the output schema for the User
class UserOut(BaseModel):
    user_id: int
    email: str
    password: str
    activation: datetime
    subscription: bool

class UserCreate(BaseModel):
    email: str
    password: str


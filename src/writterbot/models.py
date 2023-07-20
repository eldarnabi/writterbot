from sqlalchemy import Boolean, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "User"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    activation = Column(DateTime, default=func.now())  
    subscription = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "password": self.password,
            "activation": self.activation,
            "subscription": self.subscription
        }


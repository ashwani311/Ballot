import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable = False)
    url = Column(String(250),nullable = False)
    email = Column(String(250), nullable=False)
    mobile = Column(Integer, nullable = False)
    password = Column(String(250), nullable = False)




engine = create_engine('sqlite:///OBallot.db')
Base.metadata.create_all(engine)

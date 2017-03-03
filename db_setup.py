import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.types import Date 
import datetime

Base = declarative_base()

class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable = False)
    url = Column(String(250),nullable = False)
    email = Column(String(250), nullable=False)
    mobile = Column(Integer, nullable = False)
    password = Column(String(250), nullable = False)


class Ballot(Base):
    __tablename__ = 'ballot'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable = False)
    date = Column(Date, nullable = False)
    uid = Column(Integer, ForeignKey('admin.id'))
    admin = relationship(Admin)

    
class Options(Base):
    __tablename__ = 'option'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable = False)
    bid = Column(Integer, ForeignKey('ballot.id'))
    ballot = relationship(Ballot)

class Voters(Base):
    __tablename__ = 'voter'
    
    id = Column(Integer, primary_key=True)
    uname = Column(String(250), nullable = False)
    mobile = Column(Integer, nullable = False)
    password = Column(String(250), nullable = False)
    
engine = create_engine('sqlite:///OBallot.db')
Base.metadata.create_all(engine)

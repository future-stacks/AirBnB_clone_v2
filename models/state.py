#!/usr/bin/python3
""" State Module for HBNB project """
import os
from models.city import Base, City
from models.base_model import BaseModel
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class State(BaseModel, Base):
    """ State class """
    __table__ = 'states'

    name = Column(String(128), nullable=False)
    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        cities = relationship('City', backref='state', cascade='all, delete')
    elif os.getenv('HBNB_TYPE_STORAGE') == 'file':
        @property
        def cities(self):
            """
            Returns (list): List of City instances
            with state_id equals to the current State.id
            """
            from models.city import City
            from models import storage
            city_list = list(storage.all(City).values())
            return [city for city in city_list if city.state_id == self.id]

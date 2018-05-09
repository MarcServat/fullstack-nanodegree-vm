from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def get_restaurants():
    restaurants = session.query(Restaurant).all()
    return restaurants


def add_restaurant(name):
    try:
        session.add(Restaurant(name=name))
        session.commit()
    except Exception as e:
        print e.message


def update_restaurant(name, id):
    try:
        restaurant = session.query(Restaurant).filter(Restaurant.id == id).one()
        restaurant.name = name
        session.commit()
    except Exception as e:
        print e.message

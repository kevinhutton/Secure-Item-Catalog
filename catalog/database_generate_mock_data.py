# This script is used to populate the DB with categories for testing purposes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CategoryItem, Users

engine = create_engine('postgresql://catalog:catalog@/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create mock categories
category1 = Category(name="Clothing")
session.add(category1)
session.commit()

category1 = Category(name="Cars")
session.add(category1)
session.commit()

category1 = Category(name="Sports Equipment")
session.add(category1)
session.commit()

category1 = Category(name="Electronics")
session.add(category1)
session.commit()

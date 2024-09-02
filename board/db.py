from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models to register them with SQLAlchemy
from .SubscriberMaster import SubscriberMaster
from .videoCategory import videoCategory
from .videoMaster import videoMaster
from .SubCategory import SubCategory




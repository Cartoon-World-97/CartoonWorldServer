from datetime import date, datetime
from . import db  # Import the db instance from __init__.py

class SubscriberMaster(db.Model):
    __tablename__ = 'subscriber_master'

    SL = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Sub_ID = db.Column(db.String(150), nullable=False, unique=True)
    Name = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(50), nullable=False, unique=True)
    Password = db.Column(db.String(255), nullable=False)
    Date = db.Column(db.Date, default=date.today)	
    Time = db.Column(db.Time, default=lambda: datetime.now().time())
    Ver_Url = db.Column(db.String(50), nullable=False)
    User_Verification = db.Column(db.Boolean, default=False, nullable=False)
    Status = db.Column(db.SmallInteger, default=1, nullable=False)

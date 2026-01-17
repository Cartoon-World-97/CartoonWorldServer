from datetime import date, datetime
from . import db  # Import the db instance from __init__.py

class SubCategory(db.Model):
    __tablename__ = 'sub_category'

    SL = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Sub_Cat_Id = db.Column(db.String(150), nullable=False, unique=True)
    Category_Title = db.Column(db.String(50), nullable=False)
    Date = db.Column(db.Date, default=date.today)
    Time = db.Column(db.Time, default=lambda: datetime.now().time())
    Status = db.Column(db.SmallInteger, default=1, nullable=False)

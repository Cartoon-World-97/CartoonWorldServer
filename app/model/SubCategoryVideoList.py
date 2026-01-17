from datetime import date, datetime
from . import db  # Import the db instance from __init__.py

class SubCategoryVideoList(db.Model):
    __tablename__ = 'sub_category_video_list'

    SL = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Sub_Cat_Id = db.Column(db.String(150), nullable=False, unique=True)
    Video_ID = db.Column(db.String(150), nullable=False, unique=True)
    Date = db.Column(db.Date, default=date.today)
    Time = db.Column(db.Time, default=lambda: datetime.now().time())
    Status = db.Column(db.SmallInteger, default=1, nullable=False)

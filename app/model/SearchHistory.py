from datetime import datetime
from . import db

class SearchHistory(db.Model):
    __tablename__ = 'search_history'

    SL = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Sub_ID = db.Column(db.String(150), nullable=False, unique=True)
    Search_Json = db.Column(db.String, nullable=False)
    Update_Date_Time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
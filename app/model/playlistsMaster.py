from datetime import date, datetime
from . import db 

class playlistsMaster(db.Model):
    __tablename__ = 'playlists_master'

    SL = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Sub_ID = db.Column(db.String(150), nullable=False)
    Video_ID = db.Column(db.String(150), nullable=False)
    Date = db.Column(db.Date, default=date.today)	
    Time = db.Column(db.Time, default=lambda: datetime.now().time())
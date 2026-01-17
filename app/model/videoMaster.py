from datetime import date, datetime
from . import db

class videoMaster(db.Model):
    __tablename__ = 'video_master'
    SL = db.Column(db.Integer,primary_key=True,autoincrement=True)
    Video_ID = db.Column(db.String,nullable=False,unique=True)
    Category_ID = db.Column(db.String,db.ForeignKey("video_category.Category_ID"),nullable=False)
    Title = db.Column(db.String,nullable=False)
    Description = db.Column(db.String,nullable=False)
    Thumbnail_URL = db.Column(db.String,nullable=False)
    Video_Url = db.Column(db.String,nullable=False)
    Content_Type = db.Column(db.String,nullable=False)
    View =  db.Column(db.Integer)
    Free =  db.Column(db.SmallInteger, default=1, nullable=False)
    AD =  db.Column(db.SmallInteger, default=1, nullable=False)
    Ad_Video_URL = db.Column(db.String,nullable=False)
    Into_Json = db.Column(db.String,nullable=False)
    Status = db.Column(db.SmallInteger, default=1, nullable=False)
    Date = db.Column(db.Date, default=date.today)
    Time = db.Column(db.Time, default=lambda: datetime.now().time())
    category = db.relationship("videoCategory", back_populates="videos")





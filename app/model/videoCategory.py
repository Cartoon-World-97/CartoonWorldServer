from datetime import date , time
from . import db

class videoCategory(db.Model):
    __tablename__ = 'video_category'
    SL = db.Column(db.Integer,primary_key=True,autoincrement=True)
    Category_ID = db.Column(db.String(150),nullable=False,unique=True)
    Category_Name = db.Column(db.String(150),nullable=False,unique=True)
    icon = db.Column(db.String(150),nullable=False)
    Description = db.Column(db.String(150),nullable=False)

    videos = db.relationship("videoMaster", back_populates="category")

from datetime import datetime
from . import db

class ProgramMaster(db.Model):
    __tablename__ = 'program_master'

    SL = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Program_ID = db.Column(db.String(150), nullable=False, unique=True)
    Program_Name = db.Column(db.String(150), nullable=False)
    Program_Details = db.Column(db.String(300), nullable=False)
    Program_Img_Path = db.Column(db.String(300), nullable=False)
    prev_price = db.Column(db.Integer, nullable=False)
    Price = db.Column(db.Integer, nullable=False)
    Duration = db.Column(db.Integer, nullable=False)
    Active_Sts = db.Column(db.SmallInteger, default=1, nullable=False)
from datetime import datetime,date
from . import db

class ActivePlans(db.Model):
    __tablename__ = 'active_plans'

    SL = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Sub_ID = db.Column(db.String(150),db.ForeignKey("subscriber_master.Sub_ID"), nullable=False)
    Program_ID = db.Column(db.String(150),db.ForeignKey("program_master.Program_ID"), nullable=False)
    Duration = db.Column(db.Integer, nullable=False)
    Date = db.Column(db.Date, default=date.today)	
    Time = db.Column(db.Time, default=lambda: datetime.now().time())
    Status = db.Column(db.SmallInteger, default=1, nullable=False)
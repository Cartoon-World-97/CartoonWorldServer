from datetime import datetime,date
from . import db

class TransactionDetails(db.Model):
    __tablename__ = 'transaction_details'

    SL = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Date = db.Column(db.Date, default=date.today)
    Time = db.Column(db.Time, default=lambda: datetime.now().time())
    Sub_ID = db.Column(db.String(150), nullable=False)
    Txn_ID = db.Column(db.String(150), nullable=False, unique=True)
    Program_ID = db.Column(db.String(150), nullable=False, unique=True)
    Card_Category = db.Column(db.String(150), nullable=False)
    Txn_Category = db.Column(db.String(150), nullable=False)
    Amount = db.Column(db.Integer, nullable=False)
    Status = db.Column(db.String(150), default=1, nullable=False)
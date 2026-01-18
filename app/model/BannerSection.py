from datetime import datetime, date
from . import db

class BannerSection(db.Model):
    __tablename__ = 'banner_section'

    SL = db.Column(db.Integer, primary_key=True, autoincrement=True)

    Video_ID = db.Column(
        db.String(50),
        db.ForeignKey("video_master.Video_ID"),
        nullable=False,
        index=True
    )

    Default = db.Column(db.SmallInteger, default=0, nullable=False)
    Active_sts = db.Column(db.SmallInteger, default=1, nullable=False)

    Date = db.Column(db.Date, default=date.today)
    Time = db.Column(db.Time, default=lambda: datetime.now().time())

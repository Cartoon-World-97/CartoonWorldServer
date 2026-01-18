from datetime import datetime
from . import db

class VideosCatList(db.Model):
    __tablename__ = 'videos_cat_list'

    SL = db.Column(db.Integer, primary_key=True, autoincrement=True)

    Name = db.Column(db.String(150), nullable=False)

    Category_ID = db.Column(
        db.String(50),
        db.ForeignKey("video_category.Category_ID"),
        nullable=False,
        index=True
    )

    Is_title_Card = db.Column(db.SmallInteger, default=0, nullable=False)
    Status = db.Column(db.SmallInteger, default=1, nullable=False)

    Created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

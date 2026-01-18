from . import db

class videoCategory(db.Model):
    __tablename__ = 'video_category'

    SL = db.Column(db.Integer, primary_key=True, autoincrement=True)

    Category_ID = db.Column(db.String(50), nullable=False, unique=True)
    Category_Name = db.Column(db.String(100), nullable=False, unique=True)

    icon = db.Column(db.String(300), nullable=False)

    # Description can be long → use Text
    Description = db.Column(db.Text, nullable=False)

    videos = db.relationship(
        "videoMaster",
        back_populates="category",
        cascade="all, delete-orphan"
    )

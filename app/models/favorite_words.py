from sqlalchemy import Table, Column, ForeignKey

from app.models import Base

favorite_words = Table(
    "favorite_words",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("word_id", ForeignKey("words.id", ondelete="CASCADE"), primary_key=True),
)
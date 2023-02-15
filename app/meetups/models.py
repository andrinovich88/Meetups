from config.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text


class Places(Base):
    __tablename__ = "places"

    place_name = Column(String(128))
    id = Column(Integer, primary_key=True)
    location = Column(String(128))


class Themes(Base):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True)
    tags = Column(String(128))
    theme = Column(String(128))


class Meetups(Base):
    __tablename__ = "meetups"

    meetup_name = Column(String(128))
    theme_id = Column(ForeignKey("themes.id"))
    place_id = Column(ForeignKey("places.id"))
    id = Column(Integer, primary_key=True)
    description = Column(Text())
    date = Column(DateTime())


class MeetupsUsers(Base):
    __tablename__ = "meetups_users"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete='CASCADE'))
    meetup_id = Column(ForeignKey("meetups.id", ondelete='CASCADE'))

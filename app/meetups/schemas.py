from datetime import datetime

from pydantic import BaseModel, StrictInt, StrictStr


class MeetupsBase(BaseModel):
    date: datetime
    tags: StrictStr
    theme: StrictStr
    location: StrictStr
    place_name: StrictStr
    meetup_name: StrictStr
    description: StrictStr


class Meetups(MeetupsBase):
    id: StrictInt


class MeetupsUpdate(BaseModel):
    tags: StrictStr = None
    theme: StrictStr = None
    date: datetime = None
    location: StrictStr = None
    place_name: StrictStr = None
    meetup_name: StrictStr = None
    description: StrictStr = None


class MeetupsReportCSV(BaseModel):
    path: StrictStr

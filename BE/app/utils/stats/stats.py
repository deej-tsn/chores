

import datetime
from sqlmodel import Session, func, select

from ..database.db import Timetable, UserDB


START_DATE = datetime.date(2025, 12, 8)

def get_count_per_person_since_start(session : Session):
    stmt = (
        select(
            func.coalesce(
                     (UserDB.first_name + " " + UserDB.second_name),
                    "Unassigned"
                ).label("name"),
            func.count().label('count'),
        ).join(Timetable, UserDB.id == Timetable.assigned, isouter=True)
        .where(Timetable.day >= START_DATE)
        .group_by(UserDB.id)
    )

    rows = session.exec(stmt).all()
    return {name : count for name,count in rows}


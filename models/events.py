'''
MIT License

Copyright (c) 2019 Enrique Sandoval

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from models.database import Database
from datetime import datetime
from collections import namedtuple


class Event(namedtuple("Event", "name, type, start, end, days, hours")):
    @staticmethod
    def get_current_events():
        now = datetime.now()
        with Database("master.db") as db:
            resultset = db.query(get_current_events_text)
        result = []
        for r in resultset:
            diff = datetime.strptime(r[3], "%Y-%m-%d %H:%M:%S.%f") - now
            daysleft = diff.days
            hoursleft = int(diff.total_seconds() // 3600 - daysleft * 24)
            event = Event(r[0], r[1], r[2], r[3], daysleft, hoursleft)
            result.append(event)
        return result


get_current_events_text = '''
    SELECT Name
        , EventType
        , StartDate
        , EndDate
    FROM Events
    WHERE datetime('now') BETWEEN datetime(StartDate)
        AND datetime(EndDate)
    ORDER BY CASE EventType
        WHEN 'Summon Showcase' THEN 1
        WHEN 'Defense Battle' THEN 2
        WHEN 'Raid Battle' THEN 2
        WHEN 'Facility Event' THEN 2
        WHEN 'Login Bonus' THEN 3
        ELSE 5 END
'''

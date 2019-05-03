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


create_adventurer_alias_text = '''
    INSERT INTO Aliases (AdventurerID, AliasText) VALUES (?, ?)
'''

create_wyrmprint_alias_text = '''
    INSERT INTO Aliases (WyrmprintID, AliasText) VALUES (?, ?)
'''

create_dragon_alias_text = '''
    INSERT INTO Aliases (DragonID, AliasText) VALUES (?, ?)
'''


def create_alias(alias_id, text, alias_type):
    with Database("master.db") as db:
        if alias_type == 0:
            db.execute(create_adventurer_alias_text, (alias_id, text,))
        elif alias_type == 1:
            db.execute(create_wyrmprint_alias_text, (alias_id, text,))
        elif alias_type == 2:
            db.execute(create_dragon_alias_text, (alias_id, text,))

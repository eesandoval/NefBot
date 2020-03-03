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
import os


create_adventurer_alias_text = '''
    INSERT INTO Aliases (AdventurerID, AliasText) VALUES (?, ?)
'''

create_wyrmprint_alias_text = '''
    INSERT INTO Aliases (WyrmprintID, AliasText) VALUES (?, ?)
'''

create_dragon_alias_text = '''
    INSERT INTO Aliases (DragonID, AliasText) VALUES (?, ?)
'''

create_weapon_alias_text = '''
    INSERT INTO Aliases (WeaponID, AliasText) VALUES (?, ?)
'''

update_adventurer_alias_text = '''
    UPDATE Aliases
    SET AdventurerID = ?
    WHERE AliasText = ? COLLATE NOCASE
'''

update_wyrmprint_alias_text = '''
    UPDATE Aliases
    SET WyrmprintID = ?
    WHERE AliasText = ? COLLATE NOCASE
'''

update_dragon_alias_text = '''
    UPDATE Aliases
    SET DragonID = ?
    WHERE AliasText = ? COLLATE NOCASE
'''

update_weapon_alias_text = '''
    UPDATE Aliases
    SET WeaponID = ?
    WHERE AliasText = ? COLLATE NOCASE
'''

find_alias_text = '''
    SELECT 1 FROM Aliases WHERE AliasText = ? COLLATE NOCASE
'''

delete_alias_text = '''
    DELETE FROM Aliases WHERE AliasText = ? COLLATE NOCASE
'''

dump_aliases_text = '''
    SELECT AliasText
        , AdventurerID
        , WyrmprintID
        , DragonID
        , WeaponID
    FROM Aliases
    WHERE CustomAlias = 1 
'''


def delete_alias(text):
    with Database("master.db") as db:
        db.execute(delete_alias_text, (text,))
    return "Deleted alias: {0}".format(text)


def create_update_alias(alias_id, text, alias_type, aliased_name):
    with Database("master.db") as db:
        resultset = db.query(find_alias_text, (text,))
    if resultset is not None and len(resultset) > 0:
        return update_alias(alias_id, text, alias_type, aliased_name)
    else:
        return create_alias(alias_id, text, alias_type, aliased_name)


def create_alias(alias_id, text, alias_type, aliased_name):
    result = "Created alias: {0} -> {1} ({2})"
    with Database("master.db") as db:
        if alias_type == 0:
            result = result.format(text, aliased_name, "Adventurer")
            db.execute(create_adventurer_alias_text, (alias_id, text,))
        elif alias_type == 1:
            result = result.format(text, aliased_name, "Wyrmprint")
            db.execute(create_wyrmprint_alias_text, (alias_id, text,))
        elif alias_type == 2:
            result = result.format(text, aliased_name, "Dragon")
            db.execute(create_dragon_alias_text, (alias_id, text,))
        elif alias_type == 3:
            result = result.format(text, aliased_name, "Weapon")
            db.execute(create_weapon_alias_text, (alias_id, text,))
    return result


def update_alias(alias_id, text, alias_type, aliased_name):
    result = "Updated alias: {0} -> {1} ({2})"
    with Database("master.db") as db:
        if alias_type == 0:
            result = result.format(text, aliased_name, "Adventurer")
            db.execute(update_adventurer_alias_text, (alias_id, text,))
        elif alias_type == 1:
            result = result.format(text, aliased_name, "Wyrmprint")
            db.execute(update_wyrmprint_alias_text, (alias_id, text,))
        elif alias_type == 2:
            result = result.format(text, aliased_name, "Dragon")
            db.execute(update_dragon_alias_text, (alias_id, text,))
        elif alias_type == 3:
            result = result.format(text, aliased_name, "Weapon")
            db.execute(update_weapon_alias_text, (alias_id, text,))
    return result


def restore_custom_aliases():
    with open("_custom_aliases.txt", 'r') as f:
        for line in f.readlines():
            row = eval(line)
            text = row[0]
            if row[1] != None:
                alias_type = 0
                alias_id = row[1]
            elif row[2] != None:
                alias_type = 1
                alias_id = row[2]
            elif row[3] != None:
                alias_type = 2
                alias_id = row[3]
            elif row[4] != None:
                alias_type = 3
                alias_id = row[4]
            else:
                print("Error Restoring Alias: " + line)
                continue # Line is in error; notify and move on
            create_update_alias(alias_id, text, alias_type, "")
    if os.path.isfile("_custom_aliases.txt"):
        os.remove("_custom_aliases.txt")
        

def dump_custom_aliases():
    result = None
    try:
        with Database("master.db") as db:
            result = db.query(dump_aliases_text)
    except:
        # DB does not have CustomAlias column yet (update will retrieve)
        return 
    if result is None or len(result) == 0:
        return
    with open("_custom_aliases.txt", 'w') as f:
        for row in result:
            f.write("{0}\n".format(row))

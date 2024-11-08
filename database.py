import os

from pony.orm import Database, Optional, PrimaryKey

# Database singleton
db = Database()

class UserSetting(db.Entity):
    id = PrimaryKey(int, auto=False, size=64)  # Telegram User ID
    lang = Optional(str, default='')  # The language setting for this user
    stats = Optional(bool, default=False)  # Opt-in to keep game statistics
    first_places = Optional(int, default=0)  # Nr. of games won in first place
    games_played = Optional(int, default=0)  # Nr. of games completed
    cards_played = Optional(int, default=0)  # Nr. of cards played total
    use_keyboards = Optional(bool, default=False)  # Use keyboards (unused)


# Init database connection
db.bind('sqlite', os.getenv('UNO_DB', 'uno.sqlite3'), create_db=True)
db.generate_mapping(create_tables=True)

r"""
               _          __                                                                      
  ___   _ __  | | _   _  / _|  __ _  _ __   ___         ___   ___  _ __   __ _  _ __    ___  _ __ 
 / _ \ | '_ \ | || | | || |_  / _` || '_ \ / __| _____ / __| / __|| '__| / _` || '_ \  / _ \| '__|
| (_) || | | || || |_| ||  _|| (_| || | | |\__ \|_____|\__ \| (__ | |   | (_| || |_) ||  __/| |   
 \___/ |_| |_||_| \__, ||_|   \__,_||_| |_||___/       |___/ \___||_|    \__,_|| .__/  \___||_|   
                  |___/                                                        |_|                
"""

import contextlib
import glob
import pathlib
import sqlite3
from itertools import chain

from ..constants import configPath, databaseFile
from ..utils import separate, profiles


def create_database(model_id, path=None):
    profile = profiles.get_current_profile()

    path = path or pathlib.Path.home() / configPath / profile / databaseFile

    with contextlib.closing(sqlite3.connect(path)) as conn:
        with contextlib.closing(conn.cursor()) as cur:
            try:
                model_sql = f"""
                CREATE TABLE '{model_id}'(
                    id INTEGER PRIMARY KEY,
                    media_id INTEGER NOT NULL,
                    filename VARCHAR NOT NULL
                );"""
                cur.execute(model_sql)
            except sqlite3.OperationalError:
                pass


def write_from_data(data: tuple, model_id):
    profile = profiles.get_current_profile()

    database_path = pathlib.Path.home() / configPath / profile / databaseFile

    with contextlib.closing(sqlite3.connect(database_path)) as conn:
        with contextlib.closing(conn.cursor()) as cur:
            model_insert_sql = f"""
            INSERT INTO '{model_id}'(
                media_id, filename
            )
            VALUES (?, ?);"""
            cur.execute(model_insert_sql, data)
            conn.commit()


def read_foreign_database(path) -> list:
    database_files = glob.glob(path.strip('\'\"') + '/*.db')

    database_results = []
    for file in database_files:
        with contextlib.closing(sqlite3.connect(file)) as conn:
            with contextlib.closing(conn.cursor()) as cur:
                read_sql = """SELECT media_id, filename FROM medias"""
                cur.execute(read_sql)
                for result in cur.fetchall():
                    database_results.append(result)

    return database_results


def write_from_foreign_database(results: list, model_id):
    profile = profiles.get_current_profile()

    database_path = pathlib.Path.home() / configPath / profile / databaseFile

    # Create the database table in case it doesn't exist:
    create_database(model_id, database_path)

    # Filter results to avoid adding duplicates to database:
    media_ids = get_media_ids(model_id)
    filtered_results = separate.separate_database_results_by_id(
        results, media_ids)

    # Insert results into our database:
    with contextlib.closing(sqlite3.connect(database_path)) as conn:
        with contextlib.closing(conn.cursor()) as cur:
            model_insert_sql = f"""
            INSERT INTO '{model_id}'(
                media_id, filename
            )
            VALUES (?, ?);"""
            cur.executemany(model_insert_sql, filtered_results)
            conn.commit()

    print(f'Migration complete. Migrated {len(filtered_results)} items.')


def get_media_ids(model_id) -> list:
    profile = profiles.get_current_profile()

    database_path = pathlib.Path.home() / configPath / profile / databaseFile

    with contextlib.closing(sqlite3.connect(database_path)) as conn:
        with contextlib.closing(conn.cursor()) as cur:
            media_ids_sql = f"""SELECT media_id FROM '{model_id}'"""
            cur.execute(media_ids_sql)
            media_ids = cur.fetchall()

    # A list of single elements and not iterables:
    return list(chain.from_iterable(media_ids))

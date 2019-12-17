#!/usr/bin/python

import os, argparse, time, requests, sqlite3, sys, logging
from datetime import datetime

try:
    import simplejson as json
except ImportError:
    import json

LOGGER = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(out_hdlr)
LOGGER.setLevel(logging.INFO)

class GistQuery:
    def __init__(self, connection, dbexists):
        self.connection = connection
        self.dbexists = dbexists
        self.init_db(self.connection, self.dbexists)

    def init_db(self, conn, dbexists):
        if dbexists:
            LOGGER.info("No schema exists, initializing local database.")
            conn.executescript("""
            CREATE TABLE gists (
             gists_id     text,
             updated_at   date
            );
             """)

    def get_gist(self, gitUser):
        GIST_URL = 'https://api.github.com/users/' + gitUser + '/gists'
        r = requests.get(GIST_URL)
        if r.status_code != 200:
            if r.status_code == 404:
                LOGGER.error("Error: Github user " + gitUser + " not found.")
                exit(1)
            else:
                r.raise_for_status()
                LOGGER.error("Error: Github user / unexpected status code!")
                exit(255)
        gist = json.loads(r.content)
        if not gist:
            LOGGER.error("Github user " + gitUser + " has not published any gists.")
            exit(1)
        else:
            return gist

    def insert_data(self, conn, gists_id, updated_at):
        conn.execute("insert into gists (gists_id, updated_at) values ('%s', '%s')" % (gists_id, updated_at))
        conn.commit()

    def update_data(self, conn, gists_id, updated_at):
        cursor = conn.cursor()
        cursor.execute("UPDATE gists set updated_at = '%s' WHERE gists_id = '%s'" % (updated_at, gists_id))
        conn.commit()
        cursor.close()

    def delete_data(self, conn, gists_id):
        cursor = conn.cursor()
        cursor.execute("DELETE from gists WHERE gists_id = '%s'" % (gists_id))
        conn.commit()
        cursor.close()

    def select_data(self, conn, gists_id):
        cursor = conn.cursor()
        cursor.execute("SELECT updated_at FROM gists WHERE gists_id = '%s'" % (gists_id))
        data = cursor.fetchone()
        cursor.close()
        return data

    def select_all(self, conn):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gists")
        data = cursor.fetchall()
        cursor.close()
        return data

    def convert_date_to_unix(self, date_parameter):
        return time.mktime(datetime.strptime(date_parameter, "%Y-%m-%dT%H:%M:%SZ").timetuple())

    def garbage_collection(self, conn, gists):
        for item in self.select_all(conn):
            gist_exist = False
            for gist in gists:
                if gist['id'] == item[0]:
                    gist_exist = True
            if not gist_exist:
                self.delete_data(conn, item[0])
                LOGGER.info("Gist id:{} deleted from local database".format(item[0]))


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("gitUser", help="Github username for gists query")
    args = parser.parse_args()

    db_filename = '/tmp/gists.db'
    db_exists = not os.path.exists(db_filename)
    connection = sqlite3.connect(db_filename)
    gist_query = GistQuery(connection, db_exists)
    gists = gist_query.get_gist(args.gitUser)

    for gist in gists:
        stored_updated_at = gist_query.select_data(connection, gist['id'])

        if stored_updated_at is not None:
            if gist_query.convert_date_to_unix(stored_updated_at[0]) < gist_query.convert_date_to_unix(gist['updated_at']):
                gist_query.update_data(connection, gist['id'], gist['updated_at'])
                LOGGER.info("There is a new gits available: {}".format(gist['git_pull_url']))
        else:
            gist_query.insert_data(connection, gist['id'], gist['updated_at'])
            LOGGER.info("New gits has been added: {}".format(gist['git_pull_url']))

    gist_query.garbage_collection(connection, gists)
    connection.close()


if __name__== "__main__":
    main()


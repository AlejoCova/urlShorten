import sqlite3
from sqlite3 import Error

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
	return conn

def main():
    database = "./pythonsqlite.db"
 
    sql_create_urls_table = """ CREATE TABLE IF NOT EXISTS urls (
                                        id integer PRIMARY KEY,
                                        url_long_name text NOT NULL UNIQUE,
                                        url_short_name text NOT NULL UNIQUE,
                                        clicks integer NOT NULL,
                                        date_last_click text NOT NULL
                                    ); """
    sql_create_urls_clicks_table = """ CREATE TABLE IF NOT EXISTS urls_clicks (
                                        id integer PRIMARY KEY,
                                        url_long_name text NOT NULL,
                                        date_click text NOT NULL
                                    ); """   
    sql_create_user_password_table = """ CREATE TABLE IF NOT EXISTS user_password (
                                        id integer PRIMARY KEY,
                                        user text NOT NULL,
                                        user_password_hash text NOT NULL
                                    ); """                                                                       
 
    conn = create_connection(database)
    if conn is not None:
        create_table(conn, sql_create_urls_table)
        create_table(conn, sql_create_urls_clicks_table)
        conn.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_db():
    con = psycopg2.connect("user=postgres password='lkjh9874'");
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
    cursor = con.cursor();
    name_Database   = 'database_db';
    sqlCreateDatabase = "CREATE DATABASE database_db;"
    cursor.execute(sqlCreateDatabase);
    con.close()



def create_table_seen_users(connection):
    # создаем таблицу "Просмотренные пользователи"
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS seen_users(
            id serial,
            vk_id varchar(50) PRIMARY KEY);"""
        )
        connection.commit()
    print("[INFO] Table SEEN_USERS was created.")


def insert_data_seen_users(connection, vk_id):
   # вставляем данные в таблицу
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO seen_users (vk_id)
            VALUES ('{vk_id}')
            OFFSET '{offset}';"""
        )

def check_user(connection, vk_id):
    with connection.cursor() as cursor:
        cursor.execute(
                f"""SELECT EXISTS(
                SELECT * FROM seen_users WHERE id = '{vk_id}');"""
            )
        connection.commit()
        cur.fetchone() is None
        True


if __name__ == '__main__':
    create_db()
    connections = psycopg2.connect(database='database_db', user='postgres', password='lkjh9874')
    create_table_seen_users(connections)
    check_user(connection)
    connections.close()

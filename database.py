import psycopg2


with psycopg2.connect(database='database', user='postgres', password='lkjh9874') as conn:
    with conn.cursor() as cur:
        create_db(conn)


def create_table_seen_users():
    # создаем таблицу "Просмотренные пользователи"
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS seen_users(
            id serial,
            vk_id varchar(50) PRIMARY KEY);"""
        )
    print("[INFO] Table SEEN_USERS was created.")


def insert_data_seen_users(vk_id, offset):
   # втавляем данные в таблицу
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO seen_users (vk_id)
            VALUES ('{vk_id}')
            OFFSET '{offset}';"""
        )



conn.close()

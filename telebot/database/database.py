import os
import psycopg
from dotenv import load_dotenv


load_dotenv()
db_name = os.getenv("DB_NAME")
db_password = os.getenv("DB_PASSWORD")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")


class Database:
    def __init__(self):
        self.conn = None

    async def connect(self):
        self.conn = await psycopg.AsyncConnection.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        await self.create_tables()

    async def create_tables(self):
        cursor = self.conn.cursor()

        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                tg_id BIGINT UNIQUE,
                name TEXT,
                age INTEGER,
                gender TEXT,
                looking_for TEXT,
                city TEXT,
                about TEXT,
                photo TEXT
            )
        """)

        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                from_user BIGINT,
                to_user BIGINT,
                PRIMARY KEY (from_user, to_user)
            )
        """)

        await self.conn.commit()
        await cursor.close()

    async def add_user(self, tg_id, name, age, gender, looking_for, city, about, photo):
        user = await self.get_user(tg_id)
        if user:
            return False

        cursor = self.conn.cursor()

        await cursor.execute("""
            INSERT INTO users (tg_id, name, age, gender, looking_for, city, about, photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (tg_id, name, age, gender, looking_for, city, about, photo))

        await self.conn.commit()
        await cursor.close()
        return True

    async def get_user(self, tg_id):
        cursor = self.conn.cursor()

        await cursor.execute("""
            SELECT name, age, city, about, photo
            FROM users
            WHERE tg_id = %s
        """, (tg_id,))

        user = await cursor.fetchone()
        await cursor.close()
        return user

    async def delete_profile(self, tg_id):
        cursor = self.conn.cursor()

        await cursor.execute("""
            DELETE FROM users
            WHERE tg_id = %s
        """, (tg_id,))

        deleted_rows = cursor.rowcount
        await self.conn.commit()
        await cursor.close()

        return deleted_rows > 0

    async def update_user(self, tg_id, name, age, gender, looking_for, city, about, photo):
        cursor = self.conn.cursor()

        await cursor.execute("""
            UPDATE users
            SET name = %s,
                age = %s,
                gender = %s,
                looking_for = %s,
                city = %s,
                about = %s,
                photo = %s
            WHERE tg_id = %s
        """, (name, age, gender, looking_for, city, about, photo, tg_id))

        await self.conn.commit()
        await cursor.close()

    async def get_random_user(self, tg_id):
        cursor = self.conn.cursor()

        # Получаем данные текущего пользователя
        await cursor.execute("""
            SELECT gender, looking_for
            FROM users
            WHERE tg_id = %s
        """, (tg_id,))

        me = await cursor.fetchone()

        if not me:
            await cursor.close()
            return None

        my_gender, my_looking_for = me

        await cursor.execute("""
            SELECT tg_id, name, age, city, about, photo
            FROM users
            WHERE tg_id != %s

            AND gender = %s
            AND looking_for = %s

            AND tg_id NOT IN (
                SELECT to_user
                FROM likes
                WHERE from_user = %s
            )

            ORDER BY RANDOM()
            LIMIT 1
        """, (
            tg_id,
            my_looking_for,  # показываем тех, кого ищу я
            my_gender,  # и кто ищет таких как я
            tg_id
        ))

        user = await cursor.fetchone()

        await cursor.close()
        return user

    async def add_like(self, from_user, to_user):
        cursor = self.conn.cursor()

        await cursor.execute("""
            INSERT INTO likes (from_user, to_user)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (from_user, to_user))

        await self.conn.commit()
        await cursor.close()

    async def is_match(self, from_user, to_user):
        cursor = self.conn.cursor()

        await cursor.execute("""
            SELECT 1
            FROM likes
            WHERE from_user = %s
              AND to_user = %s
        """, (to_user, from_user))

        result = await cursor.fetchone()
        await cursor.close()

        return result is not None

    async def close(self):
        if self.conn:
            await self.conn.close()
    async def my_match(self, tg_id):
        cursor = self.conn.cursor()

        await cursor.execute("""
            SELECT users.tg_id, users.name, users.age, users.city, users.about, users.photo
            FROM likes
            JOIN users ON likes.to_user = users.tg_id
            WHERE likes.from_user = %s
        """, (tg_id, ))
        res = await cursor.fetchall()
        return res
    async def delete_match(self, from_user, to_user):
        cursor = self.conn.cursor()
        await cursor.execute("""
        DELETE FROM likes WHERE from_user = %s AND to_user = %s
        """, (from_user, to_user))
        await self.conn.commit()
        await cursor.close()
    async def count_users(self):
        cursor = self.conn.cursor()
        await cursor.execute("""
        SELECT COUNT(*) FROM users
        """)
        return (await cursor.fetchone())[0]
    async def count_likes(self):
        cursor = self.conn.cursor()
        await cursor.execute("""
        SELECT COUNT(*) from likes
        """)
        return (await cursor.fetchone())[0]
    async def get_all_users(self, tg_id):
        cursor = self.conn.cursor()
        await cursor.execute("""
        SELECT * FROM users WHERE tg_id != %s
        """, (tg_id,))
        return await cursor.fetchall()
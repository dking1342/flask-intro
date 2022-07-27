import os
import psycopg2


def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS')
    )
    return conn


def db_init_setup():
    conn = psycopg2.connect(
        host=os.environ.get("HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        port=os.environ.get('DB_PORT')
    )

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute('DROP TABLE IF EXISTS todos;')
    cur.execute('CREATE TABLE todos (id serial PRIMARY KEY,'
                'todo varchar (150) NOT NULL,'
                'is_completed boolean DEFAULT false NOT NULL,'
                'created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP);'
                )

    # Insert data into the table

    cur.execute('INSERT INTO todos (todo)'
                'VALUES (%s)',
                ('buy milk',)
                )

    conn.commit()
    cur.close()
    conn.close()

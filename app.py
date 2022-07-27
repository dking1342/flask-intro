from flask import Flask, request
import psycopg2.extras

from init_db import get_db_connection, db_init_setup

app = Flask(__name__)

# init db
# conn = get_db_connection()
# db_init_setup()


# routes
@app.route("/todos")
def index():
    todos = None
    error = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM todos;')
        todos = cur.fetchall()
        conn.commit()
        cur.close()

    except (Exception, psycopg2.DatabaseError) as err:
        return {
            "error": err
        }

    finally:
        conn.close()

    return {
        "data": todos,
        "error": error
    }


@app.route("/todos/<post_id>")
def get_todo(post_id):
    todo = None
    error = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM todos WHERE id = %s;', post_id)
        todo = cur.fetchone()

        if todo is None:
            error = "Invalid todo"

        conn.commit()
        cur.close()

    except (Exception, psycopg2.DatabaseError) as err:
        return {
            "error": err
        }

    finally:
        conn.close()

    return {
        "data": todo,
        "error": error
    }


@app.route("/todos/create", methods=["POST"])
def create_todo():
    new_todo = None
    error = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        todo = request.json['todo']
        cur.execute('INSERT INTO todos (todo)'
                    'VALUES (%s) RETURNING id, todo, is_completed, created_at',
                    (todo,)
                    )
        new_todo = cur.fetchone()

        conn.commit()
        cur.close()

    except (Exception, psycopg2.DatabaseError) as err:
        return {
            "error": err
        }

    finally:
        conn.close()

    return {
        "data": new_todo,
        "error": error
    }


@app.route("/todos/update/<post_id>", methods=["PUT"])
def todo_update(post_id):
    updated_todo = None
    error = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM todos WHERE id = %s;', post_id)
        saved_todo = cur.fetchone()

        if saved_todo:
            user_input = dict(**request.json)
            user_todo = user_input.get("todo")
            user_is_completed = user_input.get("is_completed")

            template_todo = saved_todo

            if user_todo:
                template_todo['todo'] = user_todo
            if user_is_completed:
                template_todo['is_completed'] = user_is_completed

            sql = """ UPDATE todos
                        SET todo = %s, is_completed = %s
                        WHERE id = %s"""
            cur.execute(sql, (template_todo['todo'], template_todo['is_completed'], post_id))

            if cur.rowcount > 0:
                cur.execute('SELECT * FROM todos WHERE id = %s;', post_id)
                updated_todo = cur.fetchone()
            else:
                error = "Invalid attempt"

            conn.commit()
            cur.close()
        else:
            error = "Invalid todo"
        conn.commit()
        cur.close()

    except (Exception, psycopg2.DatabaseError) as err:
        error = err

    finally:
        conn.close()

    return {
        "data": updated_todo,
        "error": error
    }


@app.route("/todos/delete/<post_id>", methods=["DELETE"])
def todo_delete(post_id):
    deleted_todo = None
    error = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        sql = """ 
                DELETE FROM todos
                WHERE id = %s"""
        cur.execute(sql, post_id)
        if cur.rowcount > 0:
            deleted_todo = f'Todo with id {post_id} has been deleted'
        else:
            error = "Invalid todo"

        conn.commit()
        cur.close()

    except (Exception, psycopg2.DatabaseError) as err:
        return {
            "error": err
        }

    finally:
        conn.close()

    return {
        "data": deleted_todo,
        "error": error
    }
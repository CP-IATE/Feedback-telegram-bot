import sqlite3
import os

# База будет лежать в папке data, которую мы пробросим через Docker
DATA_BASE_NAME = os.getenv("COMPOSE_DB_PATH", "data/supportBotDataBase.db")

# Створення БД
def create_db():
    try:
        connection = sqlite3.connect(DATA_BASE_NAME)
        cursor = connection.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS students(
            user_id INTEGER PRIMARY KEY,
            group_id INTEGER UNIQUE,
            name_surname TEXT DEFAULT 0,
            confirmed_student INTEGER DEFAULT 0 CHECK (confirmed_student IN (0, 1))
        );
        """

        cursor.execute(create_table_query)
        connection.commit()
        return True

    except sqlite3.Error as e:
        print(f"Помилка при створенні бази даних: {e}")
    
    finally:
        if connection:
            connection.close()

# Додавання до БД
def add_to_db(data, add_table="students"):
    """
    data: словник по типу {"column1": value1, "column2": value2}
    add_table: назва таблиці
    """
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    values = tuple(data.values())

    try:
        conn = sqlite3.connect(DATA_BASE_NAME)
        cursor = conn.cursor()
        if "user_id" in data:
            check_query = f"SELECT 1 FROM {add_table} WHERE user_id = ?"
            cursor.execute(check_query, (data["user_id"],))
            if cursor.fetchone():
                conn.close()
                return False
        add_query = f"INSERT INTO {add_table} ({columns}) VALUES ({placeholders})"
        cursor.execute(add_query, values)
        conn.commit()
        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"Помилка БД: {e}")
        return False

# Редагування в БД
def edit_in_db(filter_value, update_value, update_column="confirmed_student", search_filter="user_id", edit_table='students'):
    """
    filter_value: значення, за яким шукаємо
    search_filter: колонка, за якою шукаємо
    update_value: нове значення для колонки яку змінюємо
    update_column: колонка, за якою змінюємо значення
    edit_table: таблиця яку редагуємо
    """

    try:
        conn = sqlite3.connect(DATA_BASE_NAME)
        cursor = conn.cursor()

        check_query = f"SELECT 1 FROM {edit_table} WHERE {search_filter} = ?"
        cursor.execute(check_query, (filter_value,))
        
        if not cursor.fetchone():
            conn.close()
            return False

        update_query = f"UPDATE {edit_table} SET {update_column} = ? WHERE {search_filter} = ?"
        cursor.execute(update_query, (update_value, filter_value))
        
        conn.commit()
        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"Помилка БД: {e}")
        return False

# Видалення з БД
def delete_from_db(delete_value, delete_column="user_id", delete_table="students"):
    """
    delete_value: значення за яким видаляємо
    delete_column: колонка, за якою видаляємо
    delete_table: таблиця з якої видаляємо
    """

    try:
        conn = sqlite3.connect(DATA_BASE_NAME)
        cursor = conn.cursor()

        check_query = f"SELECT 1 FROM {delete_table} WHERE {delete_column} = ?"
        cursor.execute(check_query, (delete_value,))
        
        if not cursor.fetchone():
            conn.close()
            return False

        delete_query = f"DELETE FROM {delete_table} WHERE {delete_column} = ?"
        cursor.execute(delete_query, (delete_value,))
        
        conn.commit()
        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"Помилка БД: {e}")
        return False

# ----------------------------------------------------------------------

def get_student(user_id: int) -> dict | None:
    """Повертає dict з полями студента або None якщо не знайдено."""
    try:
        with sqlite3.connect(DATA_BASE_NAME) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT user_id, group_id, name_surname, confirmed_student "
                "FROM students WHERE user_id = ?", (user_id,)
            ).fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Помилка БД: {e}")
        return None

def get_user_by_thread(thread_id: int) -> int | None:
    """Повертає user_id за thread_id топіку або None."""
    try:
        with sqlite3.connect(DATA_BASE_NAME) as conn:
            row = conn.execute(
                "SELECT user_id FROM students WHERE group_id = ?", (thread_id,)
            ).fetchone()
            return row[0] if row else None
    except sqlite3.Error as e:
        print(f"Помилка БД: {e}")
        return None

def confirm_student(user_id: int, thread_id: int, name: str) -> bool:
    """Записує студента в БД як підтвердженого. Викликається тільки після approve."""
    try:
        with sqlite3.connect(DATA_BASE_NAME) as conn:
            conn.execute(
                "INSERT INTO students (user_id, group_id, name_surname, confirmed_student) "
                "VALUES (?, ?, ?, 1) "
                "ON CONFLICT(user_id) DO UPDATE SET "
                "group_id = excluded.group_id, "
                "name_surname = excluded.name_surname, "
                "confirmed_student = 1",
                (user_id, thread_id, name)
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Помилка БД: {e}")
        return False

def reset_student(user_id: int) -> bool:
    """Скидає статус студента після відхилення (group_id = NULL, confirmed = 0)."""
    try:
        with sqlite3.connect(DATA_BASE_NAME) as conn:
            conn.execute(
                "UPDATE students SET group_id = NULL, confirmed_student = 0 WHERE user_id = ?",
                (user_id,)
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Помилка БД: {e}")
        return False

def set_thread(user_id: int, thread_id: int) -> bool:
    """Оновлює group_id коли підтверджений студент відкриває новий чат."""
    return edit_in_db(filter_value=user_id, update_value=thread_id, update_column="group_id")

def clear_thread(user_id: int) -> bool:
    """Обнуляє group_id після закриття чату (/close)."""
    try:
        with sqlite3.connect(DATA_BASE_NAME) as conn:
            conn.execute(
                "UPDATE students SET group_id = NULL WHERE user_id = ?", (user_id,)
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Помилка БД: {e}")
        return False
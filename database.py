import sqlite3

DB_PATH = "database.db"
ALLOWED_FIELDS = ("name", "email", "phone", "address", "country")


def connect_to_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_db_table():
    conn = connect_to_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL
            )
            """
        )

        user_count = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
        if user_count == 0:
            sample_users = [
                (
                    "Haya Karanouh",
                    "haya@example.com",
                    "70123456",
                    "Beirut",
                    "Lebanon",
                ),
                (
                    "Ali Rahal",
                    "ali@example.com",
                    "70234567",
                    "Sidon",
                    "Lebanon",
                ),
                (
                    "Maya Nasser",
                    "maya@example.com",
                    "70345678",
                    "Tripoli",
                    "Lebanon",
                ),
            ]
            conn.executemany(
                "INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)",
                sample_users,
            )

        conn.commit()
        return True
    except sqlite3.Error as exc:
        conn.rollback()
        print(f"Database error: {exc}")
        return False
    finally:
        conn.close()


def insert_user(user):
    required_fields = ["name", "email", "phone", "address", "country"]
    if not isinstance(user, dict):
        raise ValueError("User must be provided as a dictionary.")

    missing_fields = [field for field in required_fields if field not in user or user[field] is None or str(user[field]).strip() == ""]
    if missing_fields:
        raise ValueError(f"Missing required user fields: {', '.join(missing_fields)}")

    conn = connect_to_db()
    try:
        cursor = conn.execute(
            """
            INSERT INTO users (name, email, phone, address, country)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(user["name"]).strip(),
                str(user["email"]).strip(),
                str(user["phone"]).strip(),
                str(user["address"]).strip(),
                str(user["country"]).strip(),
            ),
        )
        conn.commit()
        new_user_id = cursor.lastrowid
        return get_user_by_id(new_user_id)
    except sqlite3.Error as exc:
        conn.rollback()
        print(f"Insert user error: {exc}")
        return None
    finally:
        conn.close()


def get_users():
    conn = connect_to_db()
    try:
        rows = conn.execute("SELECT * FROM users ORDER BY user_id ASC").fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        print(f"Get users error: {exc}")
        return []
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = connect_to_db()
    try:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    except sqlite3.Error as exc:
        print(f"Get user by id error: {exc}")
        return None
    finally:
        conn.close()


def update_user(user):
    if not isinstance(user, dict):
        raise ValueError("User must be provided as a dictionary.")

    required_fields = ["user_id", "name", "email", "phone", "address", "country"]
    missing_fields = [field for field in required_fields if field not in user or user[field] is None or str(user[field]).strip() == ""]
    if missing_fields:
        raise ValueError(f"Missing required user fields: {', '.join(missing_fields)}")

    conn = connect_to_db()
    try:
        user_id = int(user["user_id"])
        cursor = conn.execute(
            """
            UPDATE users
            SET name = ?, email = ?, phone = ?, address = ?, country = ?
            WHERE user_id = ?
            """,
            (
                str(user["name"]).strip(),
                str(user["email"]).strip(),
                str(user["phone"]).strip(),
                str(user["address"]).strip(),
                str(user["country"]).strip(),
                user_id,
            ),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return None
        return get_user_by_id(user_id)
    except sqlite3.Error as exc:
        conn.rollback()
        print(f"Update user error: {exc}")
        return None
    finally:
        conn.close()


def patch_user(user_id, updates):
    if not isinstance(updates, dict) or not updates:
        raise ValueError("Updates must be provided as a non-empty dictionary.")

    invalid_fields = [field for field in updates if field not in ALLOWED_FIELDS]
    if invalid_fields:
        raise ValueError(f"Invalid field names: {', '.join(invalid_fields)}")

    if "user_id" in updates:
        raise ValueError("user_id cannot be changed using PATCH.")

    conn = connect_to_db()
    try:
        existing_user = get_user_by_id(user_id)
        if existing_user is None:
            return None

        query_fields = []
        params = []
        for field in ALLOWED_FIELDS:
            if field in updates:
                query_fields.append(f"{field} = ?")
                params.append(str(updates[field]).strip())

        if not query_fields:
            return existing_user

        params.append(user_id)
        conn.execute(
            f"UPDATE users SET {', '.join(query_fields)} WHERE user_id = ?",
            params,
        )
        conn.commit()
        return get_user_by_id(user_id)
    except sqlite3.Error as exc:
        conn.rollback()
        print(f"Patch user error: {exc}")
        return None
    finally:
        conn.close()


def delete_user(user_id):
    conn = connect_to_db()
    try:
        cursor = conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as exc:
        conn.rollback()
        print(f"Delete user error: {exc}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    create_db_table()

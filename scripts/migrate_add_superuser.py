from app import app, db


# Define a function to check if the field exists
def check_column_exists(engine, table_name, column_name):
    conn = engine.connect()
    result = conn.execute(f"PRAGMA table_info({table_name})")
    for row in result:
        if row[1] == column_name:
            return True
    return False


# Run the migration
if __name__ == "__main__":
    with app.app_context():
        # Check if is_superuser column exists in User table
        engine = db.get_engine()
        if not check_column_exists(engine, "user", "is_superuser"):
            print("Adding is_superuser column to User table...")
            # Add the column
            conn = engine.connect()
            conn.execute("ALTER TABLE user ADD COLUMN is_superuser BOOLEAN DEFAULT 0")
            conn.close()
            print("Column added successfully!")
        else:
            print("is_superuser column already exists in User table")

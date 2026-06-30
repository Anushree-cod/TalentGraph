from sqlalchemy import inspect, text

from backend.app.db.session import engine


APPLICATION_COLUMNS = {
    "full_name": "VARCHAR",
    "email": "VARCHAR",
    "phone": "VARCHAR",
    "location": "VARCHAR",
    "years_experience": "INTEGER",
    "expected_salary": "VARCHAR",
    "cover_letter": "TEXT",
    "analysis_json": "TEXT",
}

JOB_COLUMNS = {
    "skills_required": "TEXT",
    "experience_required": "VARCHAR",
    "location": "VARCHAR",
}


def _add_missing_columns(table_name: str, columns: dict[str, str]) -> None:
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns(table_name)}
    with engine.begin() as connection:
        for column_name, column_type in columns.items():
            if column_name not in existing:
                connection.execute(
                    text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                )


def run_migrations() -> None:
    _add_missing_columns("job_applications", APPLICATION_COLUMNS)
    _add_missing_columns("jobs", JOB_COLUMNS)

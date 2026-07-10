from pathlib import Path

from sqlalchemy import inspect

from app.database.db import (
    create_database_engine,
    create_session_factory,
    get_database_url,
    init_db,
)


def test_database_url_comes_from_config() -> None:
    assert get_database_url({"database_url": "sqlite:///data/ftmc.sqlite"}) == "sqlite:///data/ftmc.sqlite"


def test_engine_and_session_factory_use_configured_sqlite_url(tmp_path: Path) -> None:
    database_path = tmp_path / "ftmc.sqlite"
    engine = create_database_engine({"database_url": f"sqlite:///{database_path}"})
    session_factory = create_session_factory(engine)

    assert str(engine.url) == f"sqlite:///{database_path}"
    with session_factory() as session:
        assert session.bind is engine


def test_init_db_creates_sqlite_parent_directory_and_tables(tmp_path: Path) -> None:
    database_path = tmp_path / "nested" / "ftmc.sqlite"
    config = {"database_url": f"sqlite:///{database_path}"}
    engine = create_database_engine(config)

    init_db(config, db_engine=engine)

    assert database_path.exists()
    table_names = set(inspect(engine).get_table_names())
    assert {"utym", "camera", "table", "occupancy_event"}.issubset(table_names)

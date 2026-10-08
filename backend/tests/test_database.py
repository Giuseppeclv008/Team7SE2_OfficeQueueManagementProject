from unittest.mock import patch

import pytest
from sqlalchemy import Column, ForeignKey, Integer, MetaData, Table, text
from sqlalchemy.orm import Session

from app import database
from app.database import NAMING_CONVENTION, Base, SessionLocal, engine, get_db

# --- Base / naming convention -----------------------------------------------


def test_base_metadata_uses_naming_convention():
    assert Base.metadata.naming_convention == NAMING_CONVENTION


def test_naming_convention_produces_expected_constraint_names():
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    Table("parent", metadata, Column("id", Integer, primary_key=True))
    child = Table(
        "child",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("parent_id", Integer, ForeignKey("parent.id"), unique=True),
        Column("code", Integer, index=True),
    )

    names = {c.name for c in child.constraints} | {i.name for i in child.indexes}

    assert names == {
        "pk_child",
        "fk_child_parent_id_parent",
        "uq_child_parent_id",
        "ix_child_code",
    }


# --- engine / SessionLocal --------------------------------------------------


def test_engine_uses_configured_url_and_pre_ping():
    assert str(engine.url) == database.settings.database_url
    assert engine.pool._pre_ping is True


def test_session_factory_is_bound_and_configured():
    assert SessionLocal.kw["bind"] is engine
    assert SessionLocal.kw["autoflush"] is False
    assert SessionLocal.kw["expire_on_commit"] is False


# --- get_db -----------------------------------------------------------------


def test_get_db_yields_working_session_bound_to_engine():
    gen = get_db()
    session = next(gen)

    assert isinstance(session, Session)
    assert session.get_bind() is engine
    assert session.execute(text("SELECT 1")).scalar() == 1

    with pytest.raises(StopIteration):
        next(gen)


def test_get_db_closes_session_after_request():
    gen = get_db()
    session = next(gen)

    with patch.object(session, "close", wraps=session.close) as close:
        gen.close()

    close.assert_called_once()


def test_get_db_closes_session_when_request_raises():
    gen = get_db()
    session = next(gen)

    with patch.object(session, "close", wraps=session.close) as close:
        with pytest.raises(RuntimeError):
            gen.throw(RuntimeError("boom"))

    close.assert_called_once()


def test_get_db_yields_new_session_per_call():
    first, second = get_db(), get_db()

    assert next(first) is not next(second)

    first.close()
    second.close()

"""
Unit tests — AccountRepository.
"""

import pytest

from app.repositories.account import AccountRepository
from tests.helpers import make_account, make_user

pytestmark = pytest.mark.unit


def test_get_by_id_for_user_filters_owner(db_session):
    # Arrange
    owner = make_user(db_session, correo="a@x.com", usuario="a")
    other = make_user(db_session, correo="b@x.com", usuario="b")
    account = make_account(db_session, owner)

    # Act / Assert
    assert AccountRepository.get_by_id_for_user(
        db_session, account_id=account.id, user_id=owner.id
    ) is not None
    assert (
        AccountRepository.get_by_id_for_user(
            db_session, account_id=account.id, user_id=other.id
        )
        is None
    )


def test_list_by_user_ordered_desc(db_session):
    # Arrange
    user = make_user(db_session)
    first = make_account(db_session, user, banco="Uno")
    second = make_account(db_session, user, banco="Dos")

    # Act
    listed = AccountRepository.list_by_user(db_session, user.id)

    # Assert
    assert [a.id for a in listed] == [second.id, first.id]


def test_create_update_delete(db_session):
    # Arrange
    user = make_user(db_session)
    account = make_account(db_session, user, banco="X")

    # Act
    account.banco = "Y"
    AccountRepository.update(db_session, account)
    db_session.commit()
    AccountRepository.delete(db_session, account)
    db_session.commit()

    # Assert
    assert AccountRepository.get_by_id(db_session, account.id) is None

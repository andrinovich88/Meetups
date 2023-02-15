import datetime as dt

import pytest
from config.database import database
from meetups.models import Meetups, MeetupsUsers
from meetups.schemas import MeetupsBase, MeetupsUpdate
from meetups.utils.crud import (create_meetup_subscription, create_new_meetup,
                                delete_meetup_by_id, get_all_actual_meetups,
                                get_all_meetups, get_all_user_meetups,
                                remove_meetup_subscription, update_meetup_data)
from sqlalchemy import and_, select


@pytest.mark.unit
async def test_create_new_meetup(db_conn):
    meetup_a = MeetupsBase(
        id=1,
        tags="test",
        theme="test",
        location="90,90",
        place_name="test",
        meetup_name="test",
        description="test",
        date=str(dt.datetime.now() + dt.timedelta(days=1)),
    )

    meetup_c = MeetupsBase(
        tags="test",
        theme="test",
        location="90,90",
        place_name="test",
        meetup_name="test",
        description="test",
        date="1900-01-01T00:00:00",
    )

    meetup_d = MeetupsBase(
        tags="test",
        theme="test",
        location="string",
        place_name="test",
        meetup_name="test",
        description="test",
        date=str(dt.datetime.now() + dt.timedelta(days=1)),
    )

    response_a = await create_new_meetup(meetup_a)
    response_b = await create_new_meetup(meetup_a)
    response_c = await create_new_meetup(meetup_c)
    response_d = await create_new_meetup(meetup_d)

    expected_response_a = {
        'success': True, 'message': 'Meetup (meetup_id=1) has been created '
    }
    expected_response_b = {
        'success': False, 'message': 'Meetup already created'
    }
    expected_response_c = {
        'success': False,
        'message': 'You can not create meetups with an irrelevant date'
    }
    expected_response_d = {
        'success': False, 'message': 'Not a valid coordinates'
    }

    query = (
        select(Meetups.id)
        .where(Meetups.id == 1)
    )
    meetup_db = await database.fetch_one(query)

    assert meetup_db
    assert response_a == expected_response_a
    assert response_b == expected_response_b
    assert response_c == expected_response_c
    assert response_d == expected_response_d


@pytest.mark.unit
async def test_get_all_meetups(test_data):
    meetups = await get_all_meetups()
    meetups = [dict(meetup) for meetup in meetups]

    assert len(meetups) == 3


@pytest.mark.unit
async def test_get_all_actual_meetups(test_data):
    meetups = await get_all_actual_meetups()

    assert len(meetups) == 2


@pytest.mark.unit
async def test_delete_meetup_by_id(test_data):
    response_a = await delete_meetup_by_id(3)
    response_b = await delete_meetup_by_id(3)

    expected_response_a = {
        'success': True,
        'message': 'Meetup (meetup_id=3) has been deleted'
    }

    expected_response_b = {
        "success": False,
        "message": "Meetup (meetup_id=3) not found"
    }

    query = (
        select(Meetups.id)
        .where(Meetups.id == 3)
    )
    meetup_db = await database.fetch_one(query)

    assert meetup_db is None
    assert response_a == expected_response_a
    assert response_b == expected_response_b


@pytest.mark.unit
async def test_update_meetup_data(test_data):
    meetup_a = MeetupsUpdate(
        tags="meetup_a",
        theme="meetup_a",
        location="90,90",
        place_name="meetup_a",
        meetup_name="meetup_a",
        description="meetup_a",
        date=str(dt.datetime.now() + dt.timedelta(days=1)),
    )
    meetup_b = MeetupsUpdate(
        tags="meetup_b",
        theme="meetup_b",
        location="-300,+500",
        place_name="meetup_b",
        meetup_name="meetup_b",
        description="meetup_b"
    )
    meetup_d = MeetupsUpdate(
        date=str(dt.datetime.now())
    )

    response_a = await update_meetup_data(3, meetup_a)
    response_b = await update_meetup_data(3, meetup_b)
    response_c = await update_meetup_data(4, meetup_a)
    response_d = await update_meetup_data(3, meetup_d)

    expected_response_a = {
        'success': True,
        'message': 'Meetup (meetup_id=3) has been updated'
    }
    expected_response_b = {
        'success': False, 'message': 'Not a valid coordinates'
    }
    expected_response_c = {
        "success": False, "message": "Meetup does not exist"
    }
    expected_response_d = {
        'success': False, 'message': 'You can not use irrelevant date'
    }

    query = (
        select(Meetups)
        .where(Meetups.id == 3)
    )
    meetup_db = await database.fetch_one(query)

    assert response_a == expected_response_a
    assert response_b == expected_response_b
    assert response_c == expected_response_c
    assert response_d == expected_response_d
    assert meetup_db.meetup_name == 'meetup_a'
    assert meetup_db.description == 'meetup_a'


@pytest.mark.unit
async def test_create_meetup_subscription(test_data):
    response_a = await create_meetup_subscription(1, 1)
    response_b = await create_meetup_subscription(1, 1)

    expected_response_a = {
        'success': True, 'message': 'Subscription was successfully completed'
    }
    expected_response_b = {
        "success": False,
        "message": "The user is already subscribed to this meetup"
    }

    query = (
        select(MeetupsUsers.id)
        .where(and_(MeetupsUsers.user_id == 1,
                    MeetupsUsers.meetup_id == 1))
    )
    meetup_user = await database.fetch_one(query)

    assert meetup_user.id == 2
    assert response_a == expected_response_a
    assert response_b == expected_response_b


@pytest.mark.unit
async def test_get_all_user_meetups(test_data):
    response = await get_all_user_meetups(1)
    response, = [dict(meetup) for meetup in response]

    assert response['meetup_name'] == 'test_name_b'


@pytest.mark.unit
async def test_remove_meetup_subscription(test_data):
    await create_meetup_subscription(1, 1)

    response_a = await remove_meetup_subscription(1, 1)
    response_b = await remove_meetup_subscription(1, 1)

    expected_response_a = {
        'success': True,
        'message': 'Meetup subscription has been deleted (uid=1, mid=1)'
    }
    expected_response_b = {
            "success": False,
            "message": "Meetup subscription does not exist (uid=1, mid=1)"
        }

    query = (
        select(MeetupsUsers.id)
        .where(and_(MeetupsUsers.user_id == 1,
                    MeetupsUsers.meetup_id == 1))
    )
    meetup_user = await database.fetch_one(query)

    assert meetup_user is None
    assert response_a == expected_response_a
    assert response_b == expected_response_b

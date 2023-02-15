from datetime import datetime

from config.database import database
from meetups.models import Meetups, MeetupsUsers, Places, Themes
from meetups.schemas import MeetupsBase, MeetupsUpdate
from meetups.utils.meetups_utils import (create_new_place, create_new_theme,
                                         delete_place_by_id,
                                         delete_theme_by_id,
                                         get_meetup_by_date_name_place,
                                         get_meetup_by_id,
                                         get_meetup_users_by_userid_meetup_id,
                                         get_meetups_by_place_id,
                                         get_meetups_by_theme_id,
                                         get_place_by_name_location,
                                         get_theme_by_name_tags,
                                         is_valid_coordinates)
from sqlalchemy import and_, delete, insert, select, update


async def get_all_meetups() -> database:
    """ Function for getting all meetups """
    query = (
        select(
            Meetups.id, Meetups.meetup_name, Meetups.date,
            Meetups.description, Themes.theme, Themes.tags, Places.place_name,
            Places.location
        )
        .join(Places, Meetups.place_id == Places.id)
        .join(Themes, Meetups.theme_id == Themes.id)
    )

    return await database.fetch_all(query)


async def get_all_actual_meetups() -> database:
    """ Function for getting all actual meetups """
    query = (
        select(
            Meetups.id, Meetups.meetup_name, Meetups.date,
            Meetups.description, Themes.theme, Themes.tags, Places.place_name,
            Places.location
        )
        .join(Places, Meetups.place_id == Places.id)
        .join(Themes, Meetups.theme_id == Themes.id)
        .where(Meetups.date >= datetime.utcnow())
    )

    return await database.fetch_all(query)


async def create_new_meetup(meetup: MeetupsBase) -> dict:
    """
     Function for new meetup creation
    :param meetup: Incoming new meetup data
    :return: status message in JSON format
    """
    # Date check
    if meetup.date < datetime.utcnow():
        return {
            "success": False,
            "message": "You can not create meetups with an irrelevant date"
        }
    if not is_valid_coordinates(meetup.location):
        return {"success": False, "message": "Not a valid coordinates"}

    # Theme processing
    theme_id = await get_theme_by_name_tags(meetup.theme, meetup.tags)
    if not theme_id:
        theme_id = await create_new_theme(meetup.theme, meetup.tags)

    # Place processing
    place_id = await get_place_by_name_location(
        meetup.place_name, meetup.location
    )
    if not place_id:
        place_id = await create_new_place(meetup.place_name, meetup.location)

    # Check existing meetup
    meetup_db = await get_meetup_by_date_name_place(
        meetup.meetup_name, meetup.date, place_id, theme_id
    )
    if meetup_db:
        return {"success": False, "message": "Meetup already created"}

    # New meetup creation
    meetup_query = (
        insert(Meetups)
        .values(date=meetup.date,
                theme_id=theme_id,
                place_id=place_id,
                meetup_name=meetup.meetup_name,
                description=meetup.description)
        .returning(Meetups.id)
    )
    meetup = await database.fetch_one(meetup_query)
    return {"success": True,
            "message": f"Meetup (meetup_id={meetup.id}) has been created "}


async def delete_meetup_by_id(meetup_id: int) -> dict:
    """
    Function for meetup removal.
    :param meetup_id: meetup ID in integer format
    :return: result in JSON format
    """
    # Existing meetup processing
    meetup_db = await get_meetup_by_id(meetup_id)
    if not meetup_db:
        return {"success": False,
                "message": f"Meetup (meetup_id={meetup_id}) not found"}

    # Meetup removal
    meetup_delete_query = (
        delete(Meetups)
        .where(Meetups.id == meetup_id)
        .returning(Meetups.theme_id, Meetups.place_id)
    )
    ids = await database.fetch_one(meetup_delete_query)

    # Deleting unnecessary entries
    meetups = await get_meetups_by_theme_id(ids.theme_id)
    if not meetups:
        await delete_theme_by_id(ids.theme_id)

    meetups = await get_meetups_by_place_id(ids.place_id)
    if not meetups:
        await delete_place_by_id(ids.place_id)

    return {"success": True,
            "message": f"Meetup (meetup_id={meetup_id}) has been deleted"}


async def update_meetup_data(
        meetup_id: int, meetup_data: MeetupsUpdate
) -> dict:
    """
    Function for meetup data updating
    :param meetup_id: target meetup ID in integer format
    :param meetup_data: serialized data for update
    :return: response with result in JSON format
    """
    meetup_query = (
        select(Meetups.id, Meetups.theme_id, Meetups.place_id)
        .where(Meetups.id == meetup_id)
    )
    meetup = await database.fetch_one(meetup_query)
    if not meetup:
        return {"success": False, "message": "Meetup does not exist"}

    meetup_values, themes_values, places_values = {}, {}, {}

    meetup_update_query = (
        update(Meetups)
        .where(Meetups.id == meetup_id)
        .returning(Meetups.id)
    )

    themes_update_query = (
        update(Themes)
        .where(Themes.id == meetup.theme_id)
    )

    places_update_query = (
        update(Places)
        .where(Places.id == meetup.place_id)
    )

    if meetup_data.meetup_name:
        meetup_values["meetup_name"] = meetup_data.meetup_name

    if meetup_data.date:
        if meetup_data.date >= datetime.utcnow():
            meetup_values["date"] = meetup_data.date
        else:
            return {"success": False,
                    "message": "You can not use irrelevant date"}

    if meetup_data.description:
        meetup_values["description"] = meetup_data.description

    if meetup_data.theme:
        themes_values["theme"] = meetup_data.theme

    if meetup_data.tags:
        themes_values["tags"] = meetup_data.tags

    if meetup_data.place_name:
        places_values["place_name"] = meetup_data.place_name

    if meetup_data.location:
        if not is_valid_coordinates(meetup_data.location):
            return {"success": False, "message": "Not a valid coordinates"}
        places_values["location"] = meetup_data.location

    if meetup_values:
        await database.fetch_one(
            query=meetup_update_query, values=meetup_values
        )
    if themes_values:
        await database.fetch_one(
            query=themes_update_query, values=themes_values
        )
    if places_values:
        await database.fetch_one(
            query=places_update_query, values=places_values
        )

    return {"success": True,
            "message": f"Meetup (meetup_id={meetup_id}) has been updated"}


async def create_meetup_subscription(user_id: int, meetup_id: int) -> dict:
    """
    Function for creating a user subscription to a meetup
    :param user_id: user ID in integer format
    :param meetup_id: meetup ID in integer format
    :return: result message in JSON format
    """
    user_meetup_db = await get_meetup_users_by_userid_meetup_id(
        user_id, meetup_id
    )
    if user_meetup_db:
        return {"success": False,
                "message": "The user is already subscribed to this meetup"}

    query = (
        insert(MeetupsUsers)
        .values(user_id=user_id,
                meetup_id=meetup_id)
    )
    await database.fetch_one(query)
    return {"success": True,
            "message": "Subscription was successfully completed"}


async def remove_meetup_subscription(user_id: int, meetup_id: int) -> dict:
    """
    Function for meetup subscription removal
    :param user_id: user ID in integer format
    :param meetup_id: meetup ID in integer format
    :return: result message in JSON format
    """
    user_meetup_db = await get_meetup_users_by_userid_meetup_id(
        user_id=user_id, meetup_id=meetup_id
    )
    if not user_meetup_db:
        return {
            "success": False,
            "message": f"Meetup subscription does not exist (uid={user_id}, "
                       f"mid={meetup_id})"
        }

    query = (
        delete(MeetupsUsers)
        .where(and_(MeetupsUsers.meetup_id == meetup_id,
                    MeetupsUsers.user_id == user_id))
    )

    await database.fetch_one(query)

    return {
        "success": True,
        "message": f"Meetup subscription has been deleted (uid={user_id}, "
                   f"mid={meetup_id})"
    }


async def get_all_user_meetups(user_id: int) -> database:
    """
    A function to get all the meetups the user is subscribed to
    :param user_id: user ID in integer format
    :return: list of database objects
    """
    query = (
        select(
            Meetups.id, Meetups.meetup_name, Meetups.date,
            Meetups.description, Themes.theme, Themes.tags, Places.place_name,
            Places.location
        )
        .join(Places, Meetups.place_id == Places.id)
        .join(Themes, Meetups.theme_id == Themes.id)
        .join(MeetupsUsers, and_(MeetupsUsers.user_id == user_id,
                                 MeetupsUsers.meetup_id == Meetups.id))
        .where(Meetups.date >= datetime.utcnow())
    )

    return await database.fetch_all(query)

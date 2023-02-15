import csv
import os
from datetime import datetime

import requests
from config.database import database
from config.settings import settings
from fastapi import HTTPException
from meetups.models import Meetups, MeetupsUsers, Places, Themes
from meetups.utils.pdf import TablePDF
from meetups_logging import logger
from middlewares.request_middleware import get_client_ip
from pydantic import FutureDate
from sqlalchemy import and_, delete, insert, select


async def get_theme_by_name_tags(name: str, tags: str) -> int | None:
    """
    Function for getting meetup theme by name
    :param name: theme name in string format
    :param tags: theme tags in string format
    :return: theme ID in integer format if exist
    """
    theme_query = (
        select(Themes.id)
        .where(and_(Themes.theme == name, Themes.tags == tags))
    )
    theme = await database.fetch_one(theme_query)
    if theme:
        return theme.id


async def get_meetup_by_id(meetup_id: int) -> database:
    """
    Function for getting meetup by ID
    :param meetup_id: meetup ID in integer format
    :return: database object with meetup if exist
    """
    query = (
        select(Meetups)
        .where(Meetups.id == meetup_id)
    )
    return await database.fetch_one(query)


async def get_meetups_by_place_id(place_id: int) -> list[int]:
    """
    Function for getting meetups by place ID
    :param place_id: place ID in integer format
    :return: list of meetups IDs in integer format
    """
    query = (
        select(Meetups.id)
        .where(Meetups.place_id == place_id)
    )
    meetups = await database.fetch_all(query)

    return [meetup.id for meetup in meetups]


async def delete_place_by_id(place_id: int):
    """
    Function for place removal by place ID
    :param place_id: place ID value in integer format
    """
    query = (
        delete(Places)
        .where(Places.id == place_id)
    )
    await database.fetch_one(query)


async def delete_theme_by_id(theme_id: int):
    """
    Function for theme removal by theme ID
    :param theme_id: theme ID in integer format
    """
    query = (
        delete(Themes)
        .where(Themes.id == theme_id)
    )
    await database.fetch_one(query)


async def get_meetups_by_theme_id(theme_id: int) -> list:
    """
    Function for getting meetup by theme ID
    :param theme_id: the,e ID in integer format
    :return: List of Meetups IDs in integer format
    """
    query = (
        select(Meetups.id)
        .where(Meetups.theme_id == theme_id)
    )
    meetups_list = await database.fetch_all(query)
    return [meetup.id for meetup in meetups_list]


async def get_meetup_by_date_name_place(
        meetup_name: str, date: FutureDate, place_id: int, theme_id: int
) -> database:
    """
    Function for getting meetup by name, date, place_id, theme_id
    :param meetup_name: meetup name in string format
    :param date: meetup date
    :param place_id: place ID in integer format
    :param theme_id: theme ID in integer format
    :return: database object if meetup exist
    """
    meetup_select = (
        select(Meetups)
        .where(and_(Meetups.meetup_name == meetup_name,
                    Meetups.date == date,
                    Meetups.place_id == place_id,
                    Meetups.theme_id == theme_id))
    )
    return await database.fetch_one(meetup_select)


async def create_new_place(place_name: str, location: str) -> int:
    """
    Function for new place creation
    :param place_name: place name in string format
    :param location: place location in string format
    :return: place ID in integer format
    """
    place_insert = (
        insert(Places)
        .values(place_name=place_name,
                location=location)
        .returning(Places.id)
    )
    place = await database.fetch_one(place_insert)
    return place.id


async def get_place_by_name_location(name: str, location: str) -> int | None:
    """
    Function for getting place ID by place name and place location
    :param name: place name in string format
    :param location: place location in string format
    :return: place ID in integer format if exist
    """
    place_query = (
        select(Places.id)
        .where(and_(Places.place_name == name,
                    Places.location == location))
    )
    place = await database.fetch_one(place_query)

    if place:
        return place.id


async def create_new_theme(theme_name: str, tags: str) -> int:
    """
    Function for new meetup theme creation
    :param theme_name: meetup theme name in string format
    :param tags: theme tags in string format
    :return: meetup theme ID in integer format
    """
    theme_insert = (
        insert(Themes)
        .values(theme=theme_name, tags=tags)
        .returning(Themes.id)
    )
    theme = await database.fetch_one(theme_insert)
    return theme.id


async def get_meetup_users_by_userid_meetup_id(
        user_id: int, meetup_id: int
) -> database:
    """
    Function for getting MeetupUsers database object by user ID and meetup ID
    :param user_id: user ID in integer format
    :param meetup_id: meetup ID in integer format
    :return: MeetupUsers database object if exist
    """
    query = (
        select(MeetupsUsers)
        .where(and_(MeetupsUsers.meetup_id == meetup_id,
                    MeetupsUsers.user_id == user_id))
    )
    return await database.fetch_one(query)


def convert_database_records_to_list(records_list: database) -> list:
    """
    Function for processing database Records list
    :param records_list: database Records object
    :return: list with data
    """
    return [tuple(_ for _ in record.values()) for record in records_list]


def create_report_csv(user_id: int, meetups_list: list) -> dict:
    """
    Function for writing all available meetups to CSV file
    :param user_id: user ID in integer format
    :param meetups_list: list of database Record with meetups
    :return: result response message in JSON format
    """
    # Create paths variables
    base_path = f"storage/{user_id}/reports/csv"
    file_path = f"{base_path}/report_{datetime.utcnow()}.csv"

    # Writing data to CSV file
    try:
        os.makedirs(base_path, exist_ok=True)
        with open(file_path, 'w') as csv_file:
            writer = csv.writer(csv_file,
                                delimiter=',',
                                lineterminator='\n',
                                quoting=csv.QUOTE_MINIMAL)
            writer.writerows(meetups_list)
    except Exception as e:
        logger.error(str(e))
        return {
            "success": False,
            "message": f"Writing the file to disk failed. Exception: "
                       f"'{str(e)}'"
        }

    return {"path": file_path}


def create_report_pdf(
        user_id: int, tittles: tuple, meetups_list: list
) -> dict:
    """
    Function for PDF report creation
    :param user_id: user ID in integer format
    :param tittles: tuple of columns names
    :param meetups_list: list with meetups data
    :return: result message in JSON format
    """
    # Create paths variables
    base_path = f"storage/{user_id}/reports/pdf"
    file_path = f"{base_path}/report_{datetime.utcnow()}.pdf"

    pdf = TablePDF(
        data_list=meetups_list,
        file_path=file_path,
        tittles=tittles,
        orientation='L',
        font="Times",
        format='A4',
        size=10,
    )

    pdf.add_page()
    pdf.set_title("Available meetups list")

    try:
        os.makedirs(base_path, exist_ok=True)
        pdf.draw_table()
    except Exception as e:
        logger.error(str(e))
        return {"success": False,
                "message": f"Smth went worong with PDF report creation. "
                           f"Exception '{str(e)}'"}

    return {"path": file_path}


def get_ip() -> str:
    """
    Function for getting client ipv4 address
    :return: ipv4 address in string format
    """
    if settings.ENV == 'local':
        try:
            response = requests.get("https://api64.ipify.org?format=json")
            ip = response.json().get("ip")
        except Exception as e:
            logger.error(str(e))
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "message": f"Cannot get client ip. Exception '{str(e)}'"
                }
            )
    else:
        ip = get_client_ip()

    return ip


def get_coordinates_by_ip(ip: str) -> dict:
    """
    Function for getting geographical location by ip
    :param ip: ipv4 address
    :return: dictionary with longitude and latitude
    """
    try:
        response = requests.get(f"http://ipinfo.io/{ip}/json").json()
        lat_lon = response.get("loc")
        lat, lon = lat_lon.split(",")
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Cannot find coordinates by ip. Exception: "
                           f"'{str(e)}'"
            }
        )

    return {"lon": lon, "lat": lat}


def is_valid_coordinates(coordinates: str) -> bool:
    """
    Function for checking geographical coordinates
    :param coordinates: string with latitude and longitude
    :return: True if coordinates is valid, False - is incorrect
    """
    try:
        lat, lon = coordinates.split(",")
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return False

    if -90 <= lat <= 90 and -180 <= lon <= 180:
        return True

    return False


def get_token(header: str) -> str | None:
    """
    The function for getting token from incoming auth header
    :param header: auth header in string format
    :return: auth token in string format or None if not exist
    """
    try:
        _, token = header.split(" ")
    except AttributeError:
        return None
    except ValueError:
        return None
    return token

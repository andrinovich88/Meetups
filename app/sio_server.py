import socketio
from auth.utils.auth_utils import get_user_by_token
from celery_tasks.tasks import (create_csv_report_celery,
                                create_pdf_report_celery)
from config.settings import settings
from elasticsearch import Elasticsearch
from meetups.schemas import MeetupsBase, MeetupsUpdate
from meetups.utils.crud import (create_meetup_subscription, create_new_meetup,
                                delete_meetup_by_id, get_all_actual_meetups,
                                get_all_meetups, get_all_user_meetups,
                                remove_meetup_subscription, update_meetup_data)
from meetups.utils.meetups_utils import convert_database_records_to_list
from meetups_logging import logger

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
es = Elasticsearch(hosts=[f"{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"])


# Connection methods definition
@sio.on("disconnect_request")
async def disconnect_request(sid):
    logger.info(f"Disconnect request by sid '{sid}'")
    await sio.disconnect(sid)


@sio.event
def disconnect(*args, **kwargs):
    logger.info("Client disconnected")


@sio.event
async def connect(sid, environ, auth):
    try:
        auth_user = await get_user_by_token(auth.get("token"))
        if not auth_user:
            await sio.emit("my_response", {"data": "User not authenticated"},
                           room=sid)
            await sio.emit("disconnect")
    except AttributeError:
        await sio.emit("my_response", {"data": "User not authenticated"},
                       room=sid)
        await sio.emit("disconnect")


# Rooms methods definition
@sio.on("join")
async def join(sid, message):
    sio.enter_room(sid, message["room"])
    await sio.emit("my_response", {"data": "Entered room: " + message["room"]},
                   room=sid)


@sio.on("leave")
async def leave(sid, message):
    sio.leave_room(sid, message["room"])
    await sio.emit("my_response", {"data": "Left room: " + message["room"]},
                   room=sid)


@sio.on("close_room")
async def close(sid, message):
    await sio.emit('my_response',
                   {"data": "Room " + message["room"] + " is closing."},
                   room=message["room"])
    await sio.close_room(message["room"])


@sio.on("send_room_message")
async def send_room_message(sid, message):
    await sio.emit("my_response", {"data": message["data"]},
                   room=message["room"])


# Meetups processing
@sio.on("view_all_meetups")
async def view_all_meetups(sid):
    meetups = await get_all_meetups()
    data = [
        {**dict(meetup), "date": str(dict(meetup)["date"])}
        for meetup in meetups
    ]
    await sio.emit(
        'my_response', {
            "data": f"View all meetups logic has been completed. Sid: {sid}"
        },
        room=sid
    )
    return data


@sio.on("create_meetup")
async def create_meetup(sid, data):
    data = MeetupsBase(**data)
    message = await create_new_meetup(data)
    await sio.emit("my_response", {"data": message.get("message")}, room=sid)

    return message


@sio.on("update_meetup")
async def update_meetup(sid, data):
    meetup_data = data.get("data")
    meetup_id = data.get("meetup_id")

    unique_values = set(meetup_data.values())

    if None in unique_values and len(unique_values) == 1:
        message = f"No data to update (meetup_id={meetup_id})"
        await sio.emit("my_response", {"data": message}, room=sid)
        return {
            "success": False,
            "message": message
        }

    if meetup_data.get("date"):
        meetup_data = {
            **dict(meetup_data["data"]),
            "date": str(dict(meetup_data)["date"])
        }

    meetup_data = MeetupsUpdate(**meetup_data)
    message = await update_meetup_data(meetup_id, meetup_data)
    await sio.emit("my_response", {"data": message.get("message")}, room=sid)

    return message


@sio.on("delete_meetup")
async def delete_meetup(sid, m_id):
    message = await delete_meetup_by_id(m_id["meetup_id"])
    await sio.emit("my_response", {"data": message.get("message")}, room=sid)
    return message


@sio.on("follow_meetup")
async def follow_meetup(sid, message):
    user_id = message.get("user_id")
    meetup_id = message.get("meetup_id")
    message = await create_meetup_subscription(user_id, meetup_id)
    await sio.emit("my_response", {"data": message.get("message")}, room=sid)
    return message


@sio.on("unfollow_meetup")
async def unfollow_meetup(sid, message):
    user_id = message.get("user_id")
    meetup_id = message.get("meetup_id")
    message = await remove_meetup_subscription(user_id, meetup_id)
    await sio.emit("my_response", {"data": message.get("message")}, room=sid)
    return message


@sio.on("browse_user_meetups")
async def browse_user_meetups(sid, message):
    user_id = message.get("user_id")
    meetups = await get_all_user_meetups(user_id)
    meetups = [
        {**dict(meetup), "date": str(dict(meetup)["date"])}
        for meetup in meetups
    ]
    await sio.emit(
        "my_response", {
            "data": f"Browse_user_meetups has been completed. Sid: {sid}"
        }, room=sid
    )
    return meetups


@sio.on("get_meetups_report")
async def get_meetups_report(sid, message):
    user_id = message.get("user_id")
    mode = message.get("mode")

    if mode.lower() not in ['csv', 'pdf']:
        await sio.emit(
            "my_response", {"data": f"Incorrect report mode Sid: {sid}"},
            room=sid
        )
        return {"success": False, "message": "Incorrect mode"}

    result = None
    meetups_records_list = await get_all_actual_meetups()
    meetups_title = tuple(meetups_records_list[-1].keys())
    meetups_list = convert_database_records_to_list(meetups_records_list)

    if mode == 'csv':
        try:
            result = create_csv_report_celery.apply_async(
                args=[user_id, meetups_list]
            ).get()
        except Exception as e:
            msg = {
                "success": False,
                "message": f"Smth went wrong with report creation: '{str(e)}'"
            }
            logger.error(msg)
            return msg

    elif mode == 'pdf':
        try:
            result = create_pdf_report_celery.apply_async(
                args=[user_id, meetups_title, meetups_list]
            ).get()
        except Exception as e:
            msg = {
                "success": False,
                "message": f"Smth went wrong with report creation: '{str(e)}'"
            }
            logger.error(msg)
            return msg

    await sio.emit(
        "my_response",
        {"data": f"Report created successfully. Sid: {sid}"},
        room=sid
    )
    return result


@sio.on("search")
async def search(sid, query_body):
    search_result = es.search(
        index="meetups",
        body=query_body,
        _source_excludes=[
            "_meta", "places.id", "themes.id", "theme_id", "place_id"
        ],
    )
    await sio.emit(
        "my_response",
        {"data": f"Searching has been completed. Sid {sid}"},
        room=sid
    )

    return [
        {
            **meetup["_source"].pop("places"),
            **meetup["_source"].pop("themes"),
            **meetup["_source"]
        }
        for meetup in search_result["hits"]["hits"]
    ]

from typing import List, Union

from auth.schemas import SimpleMessage
from dependencies import get_current_user, superuser_required
from fastapi import APIRouter, Depends, HTTPException, Request
from meetups.schemas import (Meetups, MeetupsBase, MeetupsReportCSV,
                             MeetupsUpdate)
from meetups.utils.elastic import query_builder
from meetups.utils.meetups_utils import get_token
from meetups_logging import logger
from sio_client import sio
from socketio.exceptions import ConnectionError
from starlette.responses import JSONResponse

router = APIRouter()
router_admin = APIRouter()


@router_admin.get(
    "/", response_model=Union[List[Meetups], SimpleMessage],
    dependencies=[Depends(get_current_user), Depends(superuser_required)]
)
async def view_all_meetups(request: Request):
    """ The API endpoint for getting all meetups """
    token = get_token(request.headers.get("authorization"))

    try:
        await sio.connect("http://localhost:8000/", auth={"token": token})
    except ConnectionError:
        pass

    try:
        message = await sio.call(event="view_all_meetups")
        if type(message) == dict and not message.get("success"):
            return JSONResponse(status_code=500, content=message)
        return JSONResponse(status_code=200, content=message)

    except Exception as e:
        logger.error(str(e))
        message = {
            "success": False,
            "message": f"Smth went wrong with getting data. "
                       f"Exception: '{str(e)}'"
        }
        return JSONResponse(status_code=500, content=message)


@router_admin.post("/create", response_model=SimpleMessage,
                   dependencies=[Depends(get_current_user),
                                 Depends(superuser_required)])
async def create_meetup(request: Request, new_meetup: MeetupsBase):
    """
    The API endpoint for new meetup create. Superuser permissions required
    """
    token = get_token(request.headers.get("authorization"))
    new_meetup = {**dict(new_meetup), "date": str(dict(new_meetup)["date"])}

    try:
        await sio.connect("http://localhost:8000/", auth={"token": token})
    except ConnectionError:
        pass

    try:
        message = await sio.call(event="create_meetup", data=new_meetup)
        if not message.get("success"):
            return JSONResponse(status_code=500, content=message)
        return JSONResponse(status_code=201, content=message)

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500, detail={
                "success": False,
                "message": f"Smth went wrong with new meetup creation. "
                           f"Exception: '{str(e)}'"
            }
        )


@router_admin.put("/update_meetup/{meetup_id}", response_model=SimpleMessage,
                  dependencies=[Depends(get_current_user),
                                Depends(superuser_required)])
async def update_meetup(
        request: Request, meetup_id: int, meetup_data: MeetupsUpdate
):
    """ The API endpoint for meetup data updating """
    token = get_token(request.headers.get("authorization"))
    meetup_data = dict(meetup_data)

    try:
        await sio.connect("http://localhost:8000/", auth={"token": token})
    except ConnectionError:
        pass

    try:
        message = await sio.call(event="update_meetup",
                                 data={"meetup_id": meetup_id,
                                       "data": meetup_data})
        if not message.get("success"):
            return JSONResponse(status_code=500, content=message)
        return JSONResponse(status_code=200, content=message)

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500, detail={
                "success": False,
                "message": f"Smth went wrong with meetup updating. "
                           f"Exception: '{str(e)}'"
            }
        )


@router_admin.delete(
    "/delete_meetup/{meetup_id}", response_model=SimpleMessage,
    dependencies=[Depends(get_current_user), Depends(superuser_required)]
)
async def delete_meetup(request: Request, meetup_id: int):
    """ The API endpoint for meetup removal """
    token = get_token(request.headers.get("authorization"))

    try:
        await sio.connect("http://localhost:8000/", auth={"token": token})
    except ConnectionError:
        pass

    try:
        message = await sio.call(event="delete_meetup",
                                 data={"meetup_id": meetup_id})
        if not message.get("success"):
            return JSONResponse(status_code=500, content=message)
        return JSONResponse(status_code=200, content=message)

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500, detail={
                "success": False,
                "message": f"Smth went wrong with meetup removal. "
                           f"Exception: '{str(e)}'"
            }
        )


@router.post("/follow/{meetup_id}", response_model=SimpleMessage,
             dependencies=[Depends(get_current_user)])
async def follow_meetup(meetup_id: int, request: Request):
    """ The API endpoint for meetup subscription creation """
    user_id = request.user.id
    token = get_token(request.headers.get("authorization"))

    try:
        await sio.connect("http://localhost:8000/", auth={"token": token})
    except ConnectionError:
        pass

    try:
        message = await sio.call(event="follow_meetup",
                                 data={"meetup_id": meetup_id,
                                       "user_id": user_id})

        if not message.get("success"):
            return JSONResponse(status_code=500, content=message)
        return JSONResponse(status_code=201, content=message)

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500, detail={
                "success": False,
                "message": f"Smth went wrong with meetup subscription. "
                           f"Exception: '{str(e)}'"
            }
        )


@router.delete("/unfollow/{meetup_id}", response_model=SimpleMessage,
               dependencies=[Depends(get_current_user)])
async def unfollow_meetup(meetup_id: int, request: Request):
    """ The API endpoint for meetup subscription removal """
    user_id = request.user.id
    token = get_token(request.headers.get("authorization"))

    try:
        await sio.connect("http://localhost:8000/", auth={"token": token})
    except ConnectionError:
        pass

    try:
        message = await sio.call(event="unfollow_meetup",
                                 data={"meetup_id": meetup_id,
                                       "user_id": user_id})

        if not message.get("success"):
            return JSONResponse(status_code=500, content=message)
        return JSONResponse(status_code=201, content=message)

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500, detail={
                "success": False,
                "message": f"Smth went wrong with meetup subscription removal."
                           f" Exception: '{str(e)}'"
            }
        )


@router.get(
    "/user_meetups", response_model=Union[List[Meetups], SimpleMessage],
    dependencies=[Depends(get_current_user)]
)
async def browse_user_meetups(request: Request):
    """ The API endpoint for browsing all user's subscribed meetups """
    user_id = request.user.id
    token = get_token(request.headers.get("authorization"))

    try:
        await sio.connect("http://localhost:8000/", auth={"token": token})
    except ConnectionError:
        pass

    try:
        message = await sio.call(event="browse_user_meetups",
                                 data={"user_id": user_id})
        if type(message) == dict and not message.get("success"):
            return JSONResponse(status_code=500, content=message)
        return JSONResponse(status_code=200, content=message)

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500, detail={
                "success": False,
                "message": f"Smth went wrong with browsing user meetups."
                           f" Exception: '{str(e)}'"
            }
        )


@router.get(
    "/report/{mode}", response_model=Union[SimpleMessage, MeetupsReportCSV],
    dependencies=[Depends(get_current_user)]
)
async def get_meetups_report(request: Request, mode: str):
    """ The API endpoint for meetups report generating """
    user_id = request.user.id
    token = get_token(request.headers.get("authorization"))

    try:
        await sio.connect("http://localhost:8000/", auth={"token": token})
    except ConnectionError:
        pass

    try:
        message = await sio.call(event="get_meetups_report",
                                 data={"user_id": user_id,
                                       "mode": mode})

        if not message.get('success') and not message.get('path'):
            return JSONResponse(status_code=500, content=message)
        return JSONResponse(status_code=200, content=message)

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500, detail={
                "success": False,
                "message": f"Smth went wrong with meetup report creation."
                           f" Exception: '{str(e)}'"
            }
        )


@router.get("/search",
            dependencies=[Depends(get_current_user)],
            response_model=Union[List[Meetups], SimpleMessage])
async def search(
        request: Request, query_body: dict = Depends(query_builder.build())
):
    """ The API endpoint for searching meetups using ElasticSearch client"""
    token = get_token(request.headers.get("authorization"))
    try:
        await sio.connect("http://localhost:8000/", auth={"token": token})
    except ConnectionError:
        pass

    try:
        response = await sio.call(event="search", data=query_body)

        if type(response) == dict and not response.get("success"):
            return JSONResponse(status_code=500, content=response)
        return JSONResponse(status_code=200, content=response)

    except Exception as e:
        logger.info(str(e))
        raise HTTPException(
            status_code=500, detail={
                "success": False,
                "message": f"Smth went wrong with meetup report creation."
                           f" Exception: '{str(e)}'"
            }
        )

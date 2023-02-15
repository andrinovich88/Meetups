import socketio
from meetups_logging import logger

sio = socketio.AsyncClient()


@sio.event
async def connect():
    logger.info('connection established')


@sio.event
def my_response(data):
    logger.info(data['data'])


@sio.event
async def disconnect():
    await sio.disconnect()
    logger.info('disconnected from server')

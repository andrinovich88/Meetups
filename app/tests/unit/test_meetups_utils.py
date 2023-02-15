import os
import re

import pytest
from fastapi import HTTPException
from meetups.utils.crud import get_all_actual_meetups
from meetups.utils.meetups_utils import (convert_database_records_to_list,
                                         create_new_place, create_new_theme,
                                         create_report_csv, create_report_pdf,
                                         delete_place_by_id,
                                         delete_theme_by_id,
                                         get_coordinates_by_ip, get_ip,
                                         get_meetup_by_date_name_place,
                                         get_meetup_by_id,
                                         get_meetup_users_by_userid_meetup_id,
                                         get_meetups_by_place_id,
                                         get_meetups_by_theme_id,
                                         get_place_by_name_location,
                                         get_theme_by_name_tags, get_token,
                                         is_valid_coordinates)


@pytest.mark.unit
async def test_get_theme_by_name_tags(test_data):
    name = "test theme"
    tags = "test tag"

    response = await get_theme_by_name_tags(name, tags)

    assert response == 1


@pytest.mark.unit
async def test_get_meetup_by_id(test_data):
    response = await get_meetup_by_id(1)

    assert response.id == 1
    assert response.meetup_name == 'test_name_a'
    assert response.description == 'test desc a'


@pytest.mark.unit
async def test_get_meetups_by_place_id(test_data):
    response = await get_meetups_by_place_id(1)
    assert response == [1, 3]


@pytest.mark.unit
async def test_delete_place_by_id(test_data_partial):
    try:
        await delete_place_by_id(1)
    except Exception as e:
        assert False, f"'delete_place_by_id' raised an exception {str(e)}"


@pytest.mark.unit
async def test_delete_theme_by_id(test_data_partial):
    try:
        await delete_theme_by_id(1)
    except Exception as e:
        assert False, f"'delete_theme_by_id' raised an exception {str(e)}"


@pytest.mark.unit
async def test_get_meetups_by_theme_id(test_data):
    response = await get_meetups_by_theme_id(1)
    assert response == [1, 2, 3]


@pytest.mark.unit
async def test_get_meetup_by_date_name_place(test_data):
    response = await get_meetup_by_date_name_place(
        'test_name_a', test_data, 1, 1
    )

    assert response.id == 1
    assert response.theme_id == 1
    assert response.place_id == 1
    assert response.meetup_name == 'test_name_a'
    assert response.description == 'test desc a'


@pytest.mark.unit
async def test_create_new_place(db_conn):
    response_a = await create_new_place('test', 'test')
    response_b = await create_new_place('test', 'test')

    assert response_a == 1
    assert response_b == 2


@pytest.mark.unit
async def test_get_place_by_name_location(test_data):
    response_a = await get_place_by_name_location('test', 'test')
    response_b = await get_place_by_name_location('test_b', '53.9, 27.5667')
    response_c = await get_place_by_name_location('test_a', '52.4345, 30.9754')

    assert response_a is None
    assert response_b == 2
    assert response_c == 1


@pytest.mark.unit
async def test_create_new_theme(db_conn):
    response_a = await create_new_theme('test', 'test')
    response_b = await create_new_theme('test', 'test')

    assert response_a == 1
    assert response_b == 2


@pytest.mark.unit
async def test_get_meetup_users_by_userid_meetup_id(test_data):
    response_a = await get_meetup_users_by_userid_meetup_id(1, 1)
    response_b = await get_meetup_users_by_userid_meetup_id(1, 2)

    assert response_a is None
    assert response_b.id == 1
    assert response_b.user_id == 1
    assert response_b.meetup_id == 2


@pytest.mark.unit
async def test_convert_database_records_to_list(test_data):
    records_list = await get_all_actual_meetups()

    response = convert_database_records_to_list(records_list)

    expected_response = [
        (1, 'test_name_a', test_data, 'test desc a', 'test theme', 'test tag',
         'test_a', '52.4345, 30.9754'),
        (2, 'test_name_b', test_data, 'test desc b', 'test theme', 'test tag',
         'test_b', '53.9, 27.5667'),
    ]

    assert response == expected_response


@pytest.mark.unit
def test_create_report_csv():
    meetups_list = [
        (1, 'test_name_a', '2020-01-01', 'test desc a', 'test theme',
         'test tag', 'test_a', '52.4345, 30.9754'),
        (2, 'test_name_b', '2021-01-01', 'test desc b', 'test theme',
         'test tag', 'test_b', '53.9, 27.5667'),
    ]

    response = create_report_csv(1, meetups_list)

    pattern = r'storage/1/reports/csv/report_\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:' \
              r'\d{2}.\d{6}.csv'

    local_path = './' + response['path']

    assert re.match(pattern, response['path'])
    assert os.path.exists(local_path)

    os.remove(local_path)


@pytest.mark.unit
def test_create_report_pdf():
    tittles = ('id', 'meetup_name', 'date', 'description', 'theme', 'tags',
               'place_name', 'location')

    meetups_list = [
        (1, 'test_name_a', '2020-01-01', 'test desc a', 'test theme',
         'test tag', 'test_a', '52.4345, 30.9754'),
        (2, 'test_name_b', '2021-01-01', 'test desc b', 'test theme',
         'test tag', 'test_b', '53.9, 27.5667'),
    ]

    response = create_report_pdf(1, tittles, meetups_list)

    pattern = r'storage/1/reports/pdf/report_\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:' \
              r'\d{2}.\d{6}.pdf'

    local_path = './' + response['path']

    assert re.match(pattern, response['path'])
    assert os.path.exists(local_path)

    os.remove(local_path)


@pytest.mark.unit
def test_get_ip():
    ip = get_ip()
    octets = list(map(int, ip.split('.')))

    assert True if min(octets) >= 0 and max(octets) <= 255 else False


@pytest.mark.unit
def test_get_coordinates_by_ip():
    ip_a = '178.121.164.182'
    ip_b = '255.255.255.255'

    response_a = get_coordinates_by_ip(ip_a)
    expected_response_a = {'lon': '28.8801', 'lat': '52.6440'}

    assert response_a == expected_response_a

    with pytest.raises(HTTPException):
        get_coordinates_by_ip(ip_b)


@pytest.mark.unit
def test_is_valid_coordinates():
    coordinates_a = 'test coordinates'
    coordinates_b = '28.8801, 52.6440'
    coordinates_c = '-91, 52.6440'
    coordinates_d = '28.8801, 181'
    coordinates_e = '91, 52.6440'
    coordinates_f = '28.8801, -181'

    response_a = is_valid_coordinates(coordinates_a)
    response_b = is_valid_coordinates(coordinates_b)
    response_c = is_valid_coordinates(coordinates_c)
    response_d = is_valid_coordinates(coordinates_d)
    response_e = is_valid_coordinates(coordinates_e)
    response_f = is_valid_coordinates(coordinates_f)

    assert response_a is False
    assert response_b is True
    assert response_c is False
    assert response_d is False
    assert response_e is False
    assert response_f is False


@pytest.mark.unit
def test_get_token():
    header_a = 'Test'
    header_b = 'Test token'

    token_a = get_token(header_a)
    token_b = get_token(header_b)

    assert token_a is None
    assert token_b == 'token'

from typing import Optional

from fastapi import Query
from fastapi_elasticsearch import ElasticsearchAPIQueryBuilder
from meetups.utils.meetups_utils import (get_coordinates_by_ip, get_ip,
                                         is_valid_coordinates)

query_builder = ElasticsearchAPIQueryBuilder()


@query_builder.filter()
def filter_distance(client_point: Optional[str] = Query(None),
                    distance: int = Query(100)):
    """ Function for geo searching creation """
    if client_point and is_valid_coordinates(client_point):
        lat, lon = client_point.split(',')
        coordinates = {"lat": lat, "lon": lon}
    else:
        ip = get_ip()
        coordinates = get_coordinates_by_ip(ip)

    return {
        "geo_distance": {
            "distance": f"{distance}km",
            "places.location": coordinates
        }
    }


@query_builder.filter()
def filter_date():
    """ Function for filtering available dates in result """
    return {
        "range": {
            "date": {
                "gte": "now"
            }
        }
    }


@query_builder.sorter()
def sort_by():
    """ Function for sorting result values by date """
    return {
        "date": "desc"
    }


@query_builder.matcher()
def match_fields(search_string: Optional[str] = Query(None)):
    """ Function for searching required meetups by keywords """
    return {
        "multi_match": {
            "query": search_string,
            "fuzziness": "AUTO",
            "fields": ["*"]
        }
    } if search_string is not None else None

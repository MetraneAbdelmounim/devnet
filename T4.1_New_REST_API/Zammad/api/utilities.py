"""
Utility functions used by API objects
"""


def _process_get_response(response, Model):
    """Process the returned payload from a GET request

    Given a payload from a GET request and the target object type
    return one of three possible values:
      1. None if nothing returned (or a 404 status)
      2. An instance of the target object if a single item in payload
      3. A list of target objects if a list of items is in the payload

      :param requests.Response response: A Response object from requests
      :param Class model: A model representing a Zammad object
      :return None, Object, [Object]
      :raises HTTPError: If there was an error during the request
    """

    # catch no object found error before general raise_for_status
    if response.status_code == 404:
        return None
    response.raise_for_status()

    payload = response.json()

    # A single ticket lookup should return a dict
    if type(payload) == dict:
        return Model(payload)
    elif type(payload) == list:
        return [Model(item) for item in payload]


def _process_search_response(response, Model):
    """Process the returned payload from a GET search request

    Given a payload from a GET search request and the target object type
    return one of three possible values:
      1. None if no matches found
      2. A list of target objects matching search. Even a single match
         will return a list.

      :param requests.Response response: A Response object from requests
      :param Class model: A model representing a Zammad object
      :return None, [Object]
      :raises HTTPError: If there was an error during the request
    """

    response.raise_for_status()

    search_payload = response.json()

    # Check if nothing was returned from search
    if len(search_payload["assets"]) == 0:
        return None

    payload = search_payload["assets"][Model.__name__]
    results = [Model(match) for id, match in payload.items()]

    # Returned objects where found
    if len(results) == 0:
        return None
    else:
        return results

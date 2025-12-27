"""
Utility functions used across models.
"""

import json


def _load_payload(dest, properties, payload):
    """Load a given set of properties from a payload into a 
    destination dictionary.

    :param dict dest: The target disctionary to add values to
    :param list properties: A list of keys to lookup from payload
        and add to the dest
    :param dict payload: An API payload containing values to load
    :raises ValueError: If an expected property is not found in the 
        payload
    """

    # TODO: Change to a dictionary with the type of data indicated
    #       would allow time/date loading into objects better

    try:
        for property in properties:
            dest[property] = payload[property]

    except KeyError:
        raise ValueError(f"property '{property}'' missing from payload.\n{payload}")


def _new_object(dest, properties):
    """Create a new object with empty values for each property

    :param dict dest: The target dictionary to add values to
    :param list properties: A list of keys to lookup from payload
        and add to the dest
    """

    for property in properties:
        dest[property] = None


def _api_prep_object(object, properties=None):
    """Return a dict of an object for API actions

    :param object object: The object to convert to a JSON string
    :param dict properties: A dict with keys "required" and "optional"
        container lists of the properties of the object to serialize.
        If not provided, all object properties will be serialized.
    :raises KeyError: If an expected property is not found for the object
    """

    prepared_object = {}

    # Verify required properties
    for property in properties["required"]:
        if property not in object.__dict__.keys():
            raise KeyError(f"The property '{property}' is requried to have a value.")
        else:
            prepared_object[property] = object.__dict__[property]

    #Add optional properties
    for property in properties["optional"]:
        if object.__dict__[property]:
            prepared_object[property] = object.__dict__[property]

    return prepared_object

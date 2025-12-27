"""
Python object representing a Zammad User
"""

from .utilities import _load_payload, _new_object


class User(object):
    """A Python object representation of a Zammad user. If
    a payload from the Zammad API is provided, user created 
    from those values. If not, a user object without any values 
    is created.

    :param dict api_payload: A payload from the Zammad API to
        a user from. Default "None"
    :Examples:

    >>> import Zammad
    >>> user = Zammad.User()
    >>> user.firstname = "John"
    >>> user.lastname = "Doe"
    """

    # TODO: change to a dictionary with the type of data indicated
    #       would allow time/date loading into objects better
    user_properties = [
        "active",
        "verified",
        "login",
        "last_login",
        "id",
        "organization_id",
        "firstname",
        "lastname",
        "email",
        "web",
        "phone",
        "fax",
        "mobile",
        "department",
        "street",
        "zip",
        "city",
        "country",
        "address",
        "note",
        "out_of_office",
        "out_of_office_start_at",
        "out_of_office_end_at",
        "out_of_office_replacement_id",
        "created_by_id",
        "created_at",
        "updated_at",
        "role_ids",
        "organization_ids",
        "group_ids",
    ]

    def __init__(self, api_payload=None):
        if api_payload:
            self._from_api(api_payload)
        else:
            _new_object(self.__dict__, User.user_properties)

    def __str__(self):
        return self.login

    def _from_api(self, payload):
        """Create a User object from Zammad API payload

        :param dict payload: An API payload containing values to load
        """

        _load_payload(self.__dict__, User.user_properties, payload)

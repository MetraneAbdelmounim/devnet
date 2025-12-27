"""
Python object representing a Zammad Article
"""

from .utilities import _load_payload, _new_object, _api_prep_object


class Article(object):
    """A Python object representation of a Zammad article"""
    
    article_types = {
        "email": {
            "id": 1,
        },
        "sms": {
            "id": 2,
        },
        "chat": {
            "id": 3,
        },
        "fax": {
            "id": 4,
        },
        "phone": {
            "id": 5,
        },
        "twitter status": {
            "id": 6,
        },
        "twitter direct-message": {
            "id": 7,
        },
        "facebook feed post": {
            "id": 8,
        },
        "facebook feed comment": {
            "id": 9,
        },
        "note": {
            "id": 10,
        },
        "web": {
            "id": 11,
        },
        "telegram personal-message": {
            "id": 12,
        },
        "facebook direct-message": {
            "id": 13,
        },
    }

    article_properties = [
        "id",
        "ticket_id",
        "type_id",
        "sender_id",
        "from",
        "to",
        "cc",
        "subject",
        "reply_to",
        "message_id",
        "message_id_md5",
        "in_reply_to",
        "content_type",
        "references",
        "body",
        "internal",
        "preferences",
        "updated_by_id",
        "created_by_id",
        "origin_by_id",
        "created_at",
        "updated_at",
        "attachments",
    ]

    # For when serializing an article for creation activities
    post_properties = {
        "required": [
            "ticket_id",
            "body",
        ],
        "optional": [
            "type_id",
            "sender_id",
            "to",
            "cc",
            "subject",
            "reply_to",
            "in_reply_to",
            "content_type",
            "references",
            "internal",
        ],
    }

    # For when serializing an article for update activities
    # Note: Only the internal flag on an article can be updated
    put_properties = {
        "required": [],
        "optional": [
            "internal",
        ],
    }

    def __init__(self, api_payload=None):
        if api_payload:
            self._from_api(api_payload)
        else:
            _new_object(self.__dict__, Article.article_properties)

    def __str__(self):
        return self.body

    def _from_api(self, payload):
        """Create a article object from the Zammad API payload

        :param dict payload: An API payload containing values to load
        """

        _load_payload(self.__dict__, Article.article_properties, payload)

    def serialize(self, method=None):
        """Generate a dict representation of the object for API use

        :param str method: Target API method for serialization
            Options of 'post' or 'put' will format accordingly.
            If not given, will return all properties of object.
        :return dict:
        :raises TypeError: If method provided is invalid
        :raises ValueError: If a required property is missing.
        """

        if method and method.lower() not in ["post", "put"]:
            raise TypeError(f"method '{method}' not a valid value of 'post' or 'put'")
        elif method.lower() == "post":
            return _api_prep_object(self, Article.post_properties)
        elif method.lower() == "put":
            return _api_prep_object(self, Article.put_properties)
        else:
            return _api_prep_object(self)

"""
Python object representing a Zammad Ticket
"""


from .utilities import _load_payload, _new_object, _api_prep_object


class Ticket(object):
    """A Python object representation of a Zammad ticket. If
    a payload from the Zammad API is provided, ticket created 
    from those values. If not, a Ticket object without any values 
    is created.

    :param dict api_payload: A payload from the Zammad API to
        a ticket from. Default "None"
    :Examples:

    >>> import Zammad
    >>> ticket = Zammad.Ticket()
    >>> ticket.title = "New Ticket"
    >>> ticket.note = "A new ticket"
    """

    # TODO: change to a dictionary with the type of data indicated
    #       would allow time/date loading into objects better
    # TODO: lookup states and map to id
    ticket_properties = [
        "id",
        "group_id",
        "priority_id",
        "state_id",
        "organization_id",
        "number",
        "title",
        "owner_id",
        "customer_id",
        "note",
        "first_response_at",
        "first_response_escalation_at",
        "first_response_in_min",
        "first_response_diff_in_min",
        "close_at",
        "close_escalation_at",
        "close_in_min",
        "close_diff_in_min",
        "update_escalation_at",
        "update_in_min",
        "update_diff_in_min",
        "last_contact_at",
        "last_contact_agent_at",
        "last_contact_customer_at",
        "last_owner_update_at",
        "create_article_type_id",
        "create_article_sender_id",
        "article_count",
        "escalation_at",
        "pending_time",
        "type",
        "time_unit",
        "preferences",
        "updated_by_id",
        "created_by_id",
        "created_at",
        "updated_at",
    ]

    # For when serializing a Ticket for creation activities
    # Also required in a post is the key "article" for the
    # first article.
    post_properties = {
        "required": [
            "title",
            "group_id",
            "customer_id",
        ],
        "optional": [
            "priority_id",
            "state_id",
            "organization_id",
            "number",
            "owner_id",
            "note",
            "type",
        ],
    }

    # Properties supported for Update actions
    put_properties = {
        "required": [],
        "optional": [
            "title",
            "owner_id",
            "priority_id",
            "organization_id",
            "customer_id",
            "state_id", # Requires pending_time
            "pending_time",
            "note",
        ],
    }

    def __init__(self, api_payload=None):
        if api_payload:
            self._from_api(api_payload)
        else:
            _new_object(self.__dict__, Ticket.ticket_properties)

        # Create empty list of articles for ticket
        self.articles = []

    def __str__(self):
        return self.title

    def _from_api(self, payload):
        """Create a ticket object from the Zammad API payload

        :param dict payload: An API payload containing values to load
        """

        _load_payload(self.__dict__, Ticket.ticket_properties, payload)

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
            if len(self.articles) != 1:
                raise ValueError(
                    f"A new ticket created with post requires a single initial Article."
                )
            result = _api_prep_object(self, Ticket.post_properties)

            # Add the first article to the result for posting.
            result["article"] = self.articles[0].serialize(method="post")
            del result["article"]["ticket_id"]

            return result
        elif method.lower() == "put":
            return _api_prep_object(self, Ticket.put_properties)
        else:
            return _api_prep_object(self)

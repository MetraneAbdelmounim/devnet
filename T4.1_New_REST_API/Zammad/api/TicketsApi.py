"""
Python Object for the Tickets endpoint
"""

from Zammad.api.utilities import _process_get_response, _process_search_response
from Zammad.models.Ticket import Ticket
from Zammad.api.ArticlesApi import ArticlesApi


class TicketsApi(object):
    """Zammad tickets API endpoints"""

    def __init__(self, api):
        self.api = api

        # Create related API endpoints
        self.articles = ArticlesApi(self.api)

    def get(self, id=None, retrieve_articles=True):
        """Retrieve a ticket by id or return all tickets.

        :param int id: The id of a Ticket object from Zammad
        :param bool get_articles: Whether to lookup all articles
            for returned tickets. Default True
        :returns Ticket, [Ticket], None.
        :raises ValueError: If the id provided is not an integer
        :Examples:

        >>> import Zammad
        >>> zammad = Zammad.Api(
                address = "http://localhost:8080",
                username = "myuser@domain.local",
                password = "userpassword"
            )
        >>> myticket = zammad.tickets.get(id=2)
        >>> alltickets = zammad.tickets.get()
        """

        url = f"{self.api._base_url}/tickets"
        try:
            if id:
                url = f"{url}/{int(id)}"
        except ValueError:
            raise ValueError("An 'id' must be an integer.")

        response = self.api.http_session.get(url)

        result = _process_get_response(response, Ticket)

        #Lookup articles for result if indicated
        if retrieve_articles:
            if result is None:
                pass
            elif type(result) == list:
                for ticket in result:
                    ticket.articles = self.articles.get(ticket_id=ticket.id)
            else:
                result.articles = self.articles.get(ticket_id=result.id)

        return result

    def search(self, query):
        """Search for tickets matching a query

        :param str query: A string to search for tickets matching
        :returns [Ticket], None
        :Examples:

        >>> import Zammad
        >>> zammad = Zammad.Api(
                address = "http://localhost:8080",
                username = "myuser@domain.local",
                password = "userpassword"
            )
        >>> myticket = zammad.tickets.search("My Ticket")
        """

        # TODO: Craft the correct URL for Zammad to SEARCH for tickets matching the "query"
        url = f"{self.api._base_url}/tickets/search?query={query}"

        # TODO: Send the proper request to Zammad using 'self.api.http_session' for a SEARCH
        # NOTE: Look at the .get, .post, and .delete methods 'response = self.api.http_session' lines
        #       for examples on how this method
        response = self.api.http_session.get(url)
        response.raise_for_status()

        # NOTE: The following conditional is in place to only attempt to run the
        #       '_process_search_response' function if a search API request was sent.
        #       No changes are necessary to this part of the script.
        if response is not None:
            return _process_search_response(response, Ticket)
        else:
            raise ValueError("Search Error.")

    def post(self, ticket):
        """Add a new ticket to Zammad given a Ticket object

        :param Ticket ticket: A Python Ticket object
        :returns Ticket: A new Ticket object representing the newly 
            added ticket
        :raises ValueError: If the Ticket to be added already has an id
            Tickets that already exist should be updated with put
        :raises HTTPError: If an error is detected during request.
            The underlying requests module can identify problems and 
            raise errors through the 'response.raise_for_status()' method
        :Examples:

        >>> import Zammad
        >>> zammad = Zammad.Api(
                address = "http://localhost:8080",
                username = "myuser@domain.local",
                password = "userpassword"
            )
        >>> new_ticket = Zammad.Ticket()
        >>> new_ticket.title = "A New Ticket"
        >>> new_ticket.group_id = 1
        >>> new_ticket.customer_id = 3
        >>> new_article = Zammad.Article()
        >>> new_article.body = "This is the first article on a new ticket"
        >>> new_ticket.articles.append(new_article)
        >>> new_ticket = zammad.tickets.post(new_ticket)
        """

        # Verify Ticket object is valid for posting
        if ticket.id is not None:
            raise ValueError(
                f"ticket.id={ticket.id}. A new ticket object must not have an id assigned."
            )

        # Build JSON body for new Ticket
        payload = ticket.serialize(method="post")

        # Send post
        url = f"{self.api._base_url}/tickets"
        response = self.api.http_session.post(url, json=payload)
        response.raise_for_status()

        if response.status_code == 201:
            return Ticket(api_payload=response.json())

    def put(self, ticket):
        """Update a ticket in Zammad given a Ticket object

        :param Ticket ticket: A Python Ticket object
        :returns Ticket: A Ticket object representing the newly
            updated ticket
        :raises ValueError: If the Ticket to be updated lacks an id
        :raises HTTPError: If an error is detected during request.
            The underlying requests module can identify problems and
            raise errors through the 'response.raise_for_status()' method
        :Examples:

        >>> import Zammad
        >>> zammad = Zammad.Api(
                address = "http://localhost:8080",
                username = "myuser@domain.local",
                password = "userpassword"
            )
        >>> ticket = zammad.tickets.get(id=10)
        >>> ticket.title = "Updating ticket title"
        >>> ticket = zammad.tickets.put(ticket)
        """

        # Verify Ticket object is valid for putting
        if ticket.id is None:
            raise ValueError(f"Ticket {ticket.title} lacks an 'id'.")

        # TODO: Build an Update method that will correctly update and return a Ticket
        # Note: Below the code from the CREATE method (post) has been provided as a
        #       starting point. Make whatever changes necessary to meet the requirements

        # # Build JSON body for new Ticket
        payload = ticket.serialize(method="put")

        # Send post
        url = f"{self.api._base_url}/tickets/{ticket.id}"
        response = self.api.http_session.put(url, json=payload)
        response.raise_for_status()

        if response.status_code == 200:
           return Ticket(api_payload=response.json())

    def delete(self, ticket):
        """Delete a ticket in Zammad given a Ticket object

        :param Ticket ticket: A Python Ticket object
        :returns bool: True or False about success of deletion
        :raises ValueError: If the Ticket to be updated lacks an id
        :raises HTTPError: If an error is detected during request.
            The underlying requests module can identify problems and
            raise errors through the 'response.raise_for_status()' method
        :Examples:

        >>> import Zammad
        >>> zammad = Zammad.Api(
                address = "http://localhost:8080",
                username = "myuser@domain.local",
                password = "userpassword"
            )
        >>> ticket = zammad.tickets.get(id=10)
        >>> delete_result = zammad.tickets.delete(ticket)
        """

        # Verify Ticket object is valid for posting
        if ticket.id is None:
            raise ValueError(f"Ticket {ticket.title} lacks an 'id'.")

        # Send delete
        url = f"{self.api._base_url}/tickets/{ticket.id}"
        response = self.api.http_session.delete(url)
        response.raise_for_status()

        return True

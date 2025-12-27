"""
Python Object for the Articles endpoint
"""

from Zammad.api.utilities import _process_get_response
from Zammad.models.Article import Article


class ArticlesApi(object):
    """Zammad ticket_articles API endpoints"""

    def __init__(self, api):
        self.api = api

    def get(self, id=None, ticket_id=None):
        """Retrieve ticket articles

        If an article id is provided, return a specific article.
        If a ticket-id is provided, return all articles for that ticket.
        If neither are provided, retrun all ticket articles.

        :param int id: The id of an Article object from Zammad.
        :param int ticket_id: The id of a Ticket object from Zammad.
        :returns Article, [Article], None.
        :raise ValueError: If the ids provided are not an integer:
        :Examples:

        >>> import Zammad
        >>> zammad = Zammad.Api(
                address = "http://localhost:8080",
                username = "myuser@domain.local",
                password = "userpassword"
            )
        >>> myarticle = zammad.tickets.articles.get(id=2)
        >>> ticketarticles = zammad.tickets.articles.get(ticket_id=1)
        >>> allarticles = zammad.tickets.articles.get()
        """

        url = f"{self.api._base_url}/ticket_articles"
        try:
            if id:
                url = f"{url}/{int(id)}"
            elif ticket_id:
                url = f"{url}/by_ticket/{int(ticket_id)}"
        except ValueError:
            raise ValueError("An 'id' must be an integer.")

        response = self.api.http_session.get(url)

        return _process_get_response(response, Article)

    def post(self, article):
        """Add a new article to Zammad given an Article object

        :param Article article: A Python Article object
        :returns Article: A new Article object representing the newly 
            added article
        :raises ValueError: If the Article to be added already has an id
            Articles that already exist should be updated with put
        :raises ValueError: If a required article property is missing
        :raises HTTPError: If an error is detected during post
        :Examples:

        >>> import Zammad
        >>> zammad = Zammad.Api(
                address = "http://localhost:8080",
                username = "myuser@domain.local",
                password = "userpassword"
            )
        >>> ticket = zammad.tickets.get(id=10)
        >>> new_article = Zammad.Article()
        >>> new_article.body = "This is a new article"
        >>> new_article.ticket_id = ticket_id
        >>> new_article = zammad.tickets.articles.post(new_article)
        """

        # Verify Article object is valid for posting
        if article.id != None:
            raise ValueError(
                f"article.id={article.id}. A new article object must not have an id assigned."
            )

        # Build JSON body for new Ticket
        payload = article.serialize(method="post")

        # Send post
        url = f"{self.api._base_url}/ticket_articles"
        response = self.api.http_session.post(url, json=payload)
        response.raise_for_status()

        if response.status_code == 201:
            return Article(api_payload=response.json())

    def put(self, article):
        """Update an article in Zammad given an Article object

        :param Article article: A Python Article object
        :returns Article: An Article object representing the newly
            updated article
        :raises ValueError: If the Article to be added lacks an id
        :raises ValueError: If a required article property is missing
        :raises HTTPError: If an error is detected during post
        :Examples:

        >>> import Zammad
        >>> zammad = Zammad.Api(
                address = "http://localhost:8080",
                username = "myuser@domain.local",
                password = "userpassword"
            )
        >>> article = zammad.tickets.get(id=10)
        >>> article.intenal = True
        >>> article = zammad.tickets.articles.put(article)
        """

        # Verify Article object is valid for puting
        if article.id is None:
            raise ValueError("Article {article.body} lacks an 'id'.")

        # Build JSON body for new Ticket
        payload = article.serialize(method="put")

        # Send put
        url = f"{self.api._base_url}/ticket_articles/{article.id}"
        response = self.api.http_session.put(url, json=payload)
        response.raise_for_status()

        if response.status_code == 200:
            return Article(api_payload=response.json())

    def delete(self, article):
        """Delete an article in Zammad given an Article object

        :param Article article: A Python Article object
        :returns bool: True or False about success of deletion
        :raises ValueError: If the Article to be deleted lacks an id
        :raises HTTPError: If an error is detected during post
        :Examples:

        >>> import Zammad
        >>> zammad = Zammad.Api(
                address = "http://localhost:8080"
                username = "myuser@domain.local"
                password = "userpassword"
            )
        >>> article = zammad.tickets.articles.get(id=10)
        >>> article = zammad.tickets.articles.delete(article)
        """

        # Verify Ticket object is valid for deletion
        if article.id == None:
            raise ValueError(f"Article {article.body} lacks an 'id'.")

        # Send delete
        url = f"{self.api._base_url}/ticket_articles/{article.id}"
        response = self.api.http_session.delete(url)
        response.raise_for_status()

        if response.status_code == 200:
            return True
        else:
            return False

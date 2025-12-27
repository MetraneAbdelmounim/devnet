"""
Python object representing the Zammad REST API connection
"""

import requests
from Zammad.api.UsersApi import UsersApi
from Zammad.api.TicketsApi import TicketsApi


class Api(object):
    """A Python Object used to interact with the Zammad REST API

    Create an instance of an Api() object by providing the address
    and authentication details for the Zammad host.

    :param str address: The address of the Zammad server
    :param str username: The username for a Zammad user
    :param str password: The password for a Zammad user
    :param str token: An HTTP Token for a Zammad user
    :param str api_version: The API version to use. Default "v1"
    :raises ValueError: If neither a username/password combination or a token
        is provided
    :Examples:

    >>> import Zammad
    >>> zammad = Zammad.Api(
            address = "http://localhost:8080",
            username = "myuser@domain.local",
            password = "userpassword"
        )
    >>> me = zammad.users.me
    """

    def __init__(
        self, address, username=None, password=None, token=None, api_version="v1"
    ):
        self.address = address
        self.username = username
        self.password = password
        self.token = token
        self.api_version = api_version

        if (self.username is None or self.password is None) and self.token is None:
            raise ValueError('A "username/password" pair or a "token" must be provided')

        self._check_address()
        self._base_url = f"{self.address}/api/{self.api_version}"
        self.http_session = requests.Session()

        # Setup authentication for http session. Prefer token over user/pass
        # TODO This part is missing , you have to complete it # 
        
        if self.token:
            self.http_session.headers.update(
                {
                    "Authorization": f"Token token={self.token}"
                }
            )
        else:
            self.http_session.auth = (self.username, self.password)

        # Setup API resource endpoints
        self.users = UsersApi(self)
        self.tickets = TicketsApi(self)

    def _check_address(self):
        """Validate the address provided is formatted correctly"""

        if not ("http://" == self.address[:7] or "https://" == self.address[:8]):
            # address provided doesn't include a protocol. Default to http://
            self.address = f"http://{self.address}"

        if self.address[-1:] == "/":
            # address provided included trailing slash, remove it
            self.address = self.address[0:-1]

    @property
    def version(self):
        """Zammad server version"""

        url = f"{self,_base_url}/version"

        server_version = self.http_session.get(url)
        server_version.raise_for_status()

        return server_version.json()["version"]

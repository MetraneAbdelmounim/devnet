"""
Python Object for the UsersAPI endpoint
"""

from Zammad.models.User import User


class UsersApi(object):
    """Zammad users API endpoints"""

    def __init__(self, api):
        self.api = api
        self._me = None

    @property
    def me(self):
        """Current user"""

        if not self._me:
            url = f"{self.api._base_url}/users/me"
            me_response = self.api.http_session.get(url)
            me_response.raise_for_status()
            self._me = User(api_payload=me_response.json())

        return self._me

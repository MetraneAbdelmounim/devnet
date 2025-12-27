Python Library for interacting with the Zammad REST API

Under development:

This is a work in progress Python library for interacting with the Zammad REST API. Current functionality includes:
- A Zammad.api.Api class top level that controls HTTP session management and authentication. Also includes a version property to return the version of Zammad on the server
- A very basic Zammad.api.UserApi class that provides access to the details about the user authenticated to the API
- The skeleton and framework for a Zammad.api.TicketApi covering all CRUD activities
	Note: All API methods return "Placeholder" for now. TODO blocks indicate work to be done
- Python classes representing Users, Tickets, and Articles from Zammad and based on the returned data schema from the API
	- Zammad.models.Users
	- Zammad.models.Ticket
	- Zammad.models.Article
- "utility" functions for both api and models that provide for common workflows
	- Zammad.api.utilities
	- Zammad.models.utilities


Example using the library to interact with Zammad

import Zammad

# Credentials for a development instance of Zammad
address = "http://dev-zammad.ppm.example.com"
username = "user@login.address"
password = "PassWord:"

# Create a Zammad.Api() object
Zammad = Zammad.Api(address=address, username=username, password=password)
#MISSING
#! /usr/bin/env python
""" Sample script for testing functionality of Zammad API Library"""

from lib2to3.pgen2 import token
import os
from multiprocessing.sharedctypes import Value
from time import sleep
import Zammad

# TODO: Update environment variables hadling TOKEN login
# Collect Zammad server info from ENV
address = os.getenv("ZAMMAD_ADDRESS")
username = os.getenv("ZAMMAD_USERNAME") # this line will not be in exam
password = os.getenv("ZAMMAD_PASSWORD") # this line will not be in exam
verbose = bool(os.getenv("ZAMMAD_VERBOSE"))

# TODO comment the below 'input' line you see in the exam
token = input("Enter your token: ")

if not ((address and username and password) or token):
    raise ValueError("Missing ENV for Zammad address, username, or password")

# create a Zammad.API() object
print("·" * 80)
print("Creating a Zammad API object")
zammad = Zammad.Api(address=address, username=username, password=password, token=token)

# Lookup all tickets, loop over them printing out key details
print("·" * 80)
print("Looking up all tickets in Zammad.")
tickets = zammad.tickets.get()
if verbose:
    print("Tickets:")
    for ticket in tickets:
        print(f"Ticket Number {ticket.number}: {ticket.title}")
        print(f"  Created at {ticket.created_at} by user id {ticket.created_by_id}")
        print(f"  Customer ID: {ticket.customer_id}")
        print(f"  Article Count: {ticket.article_count}")

# Create a new ticket
# Notes:
#   - title, group_id, and customer_id are required attributes for new tickets
#   - a new ticket requires an initial article
print("·" * 80)
print("Creating a new Ticket in Zammad.")
new_ticket = Zammad.Ticket()
new_ticket.title = "Ticket created from Python to test Create/Update"
new_ticket.group_id = 1
new_ticket.customer_id = 6
new_ticket_article = Zammad.Article()
new_ticket_article.body = (
    "This is the initial article on a ticket testing ticket Create/Update"
)
new_ticket.articles.append(new_ticket_article)
new_ticket = zammad.tickets.post(new_ticket)

# Update the customer of the ticket
print("·" * 80)
print("Updating the Ticket customer.")
new_ticket.customer_id = 7
updated_ticket = zammad.tickets.put(new_ticket)

# Verifying the update worked
print("·" * 80)
print("Checking if the update was successful.")
if isinstance(updated_ticket, Zammad.Ticket):
    if updated_ticket.customer_id != 7:
        raise ValueError(
            f"Error: Updated Ticket Customer ID is {updated_ticket.customer_id} and should be 7."
        )
else:
    raise ValueError(
        f"Error: Updated Ticket is NOT a Ticket Object. It is a {type(updated_ticket)}"
    )

# Delete a ticket
# Note:
#   - First a ticket created that can be deleted for the test
#   - A ticket search is ran to find the "mistake" ticket(s)
#   - A loop is run over all tickets found
print("·" * 80)
print("Creating a Ticket for Search and Delete Tests.")
mistake_ticket = Zammad.Ticket()
mistake_ticket.title = "Mistake Ticket created from Python to test Delete"
mistake_ticket.group_id = 1
mistake_ticket.customer_id = 6
mistake_ticket_article = Zammad.Article()
mistake_ticket_article.body = (
    "This is the initial article on a ticket testing ticket Deletion/Searching"
)
mistake_ticket.articles.append(mistake_ticket_article)
mistake_ticket = zammad.tickets.post(mistake_ticket)
# Sleep for 5s to ensure new ticket fully added and ready for searching
sleep(5)

# Run query for all mistake tickets to process
print('·' * 80)
print("Searching for the Ticket to Delete")
mistake_query = zammad.tickets.search(query="Mistake")
for ticket in mistake_query:
    print(f"Deleting ticket {ticket}")
    if zammad.tickets.delete(ticket) == False:
        print("  Deletion unsuccessful")
    else:
        print("  Deletion successful")

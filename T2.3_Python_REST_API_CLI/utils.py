from colorama import Fore, Style
import requests
from typing import Dict, List


def _get_all_data(url: str, headers: Dict, params: Dict = {}) -> List:
    """Iterate over all pages of data to return everything from a paginated API.

    Args:
        url (str): Initial URL to fetch the data
        headers (Dict): Dictionary representing the headers to send
        params (Dict): Optional dictionary of GET parameters

    Returns:
        result (List): List of elements
    """
    more_pages = True
    result = []
    
    while more_pages:
        found_next = False
        
        response = requests.get(url, headers=headers, params=params, verify=False)
        response.raise_for_status()

        result.extend(response.json())
        if "Link" in response.headers:
            links = requests.utils.parse_header_links(response.headers["Link"])

            for link in links:
                if link["rel"] == "next":
                    url = link["url"]
                    found_next = True
                    break

            if found_next:
                continue

            more_pages = False
        else:
            more_pages = False

    return result


def _colorize_status(status:str) -> str:
    """Return a stylized string based on status.

    Args:
        status (str): String representing the status

    Returns:
        colorized_status (str): Status string with color markers
    """
    color = ""
    if status == "failed":
        color = Fore.RED
    elif status == "succes":
        color = Fore.GREEN

    return color + status + Style.RESET_ALL

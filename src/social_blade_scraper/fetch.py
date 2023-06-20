import requests
from fake_useragent import UserAgent
from requests import Response


def fetch(target_url: str, params: dict = None, extra_headers: dict = None) -> Response:
    # Create a UserAgent object
    user_agent = UserAgent()

    # Generate a random user agent string for Firefox
    firefox_user_agent = user_agent.firefox

    headers = {
        "User-Agent": firefox_user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    if extra_headers:
        headers = {**headers, **extra_headers}

    return requests.get(target_url, params=params, headers=headers)

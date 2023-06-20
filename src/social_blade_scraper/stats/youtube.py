from concurrent.futures import ThreadPoolExecutor, wait
from typing import Union, List

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests import Response

import re

from dataclasses import dataclass


@dataclass(frozen=True)
class DailyStat:
    """
    A dataclass to hold daily stat of YouTube channel
    """

    date: str
    subscribers_growth: str
    subscribers_count: str
    is_video_streamed: bool
    views_growth: str
    total_views: str
    estimated_earnings: str


@dataclass
class YouTubeChannel:
    """
    A data class to hold YouTubeChannel information
    """

    monthly_earning: str
    yearly_earning: str
    daily_stats: List[DailyStat]


def fetch(target_url: str) -> Response:
    # Create a UserAgent object
    user_agent = UserAgent()

    # Generate a random user agent string for Firefox
    firefox_user_agent = user_agent.firefox

    headers = {
        "User-Agent": firefox_user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    return requests.get(target_url, headers=headers)


def monthly_earnings_search(soup: BeautifulSoup) -> Union[str, None]:
    """
    Logic to search for the monthly earnings data. Cleans the found raw data and returns new fresh data.
    :param soup: BeautifulSoup object
    :return: str
    """

    tag = soup.find('p', attrs={'style': 'font-size: 1.4em; color:#41a200; font-weight: 600; padding-top: 20px;'})
    if tag:
        # Remove garbage value. eg: $298.1K \xa0-\xa0 $4.8M
        raw_text = tag.text.strip().split(' ')
        return f'{raw_text[0]} - {raw_text[-1]}'


def yearly_earnings_search(soup: BeautifulSoup) -> Union[str, None]:
    """
    Logic to search for the yearly earnings data. Cleans the found raw data and returns new fresh data.
    :param soup: BeautifulSoup object
    :return: str
    """

    tag = soup.find('p', attrs={'style': 'font-size: 2em; color:#41a200; font-weight: 600; padding-top: 20px;'})
    if tag:
        # Remove garbage value. eg: $298.1K \xa0-\xa0 $4.8M
        raw_text = tag.text.strip().split(' ')
        return f'{raw_text[0]} - {raw_text[-1]}'


def daily_stats_search(soup: BeautifulSoup) -> List[DailyStat]:
    """
    Logic to search for the daily stat data. Removes unnecessary data and creates new DailyStat objects with cleaned
    data.

    :param soup: BeautifulSoup object
    :return List[DailyStat]:
    """

    data = []
    # Using regex to extract all divs with the staring following style value because of even odd row style is used
    rows = soup.find_all('div', attrs={'style': re.compile('^width: 860px; height: 32px; line-height: 32px;')})
    for row in rows:

        # Find only direct children
        cols = row.find_all('div', recursive=False)
        date = cols[0].text.strip()

        subscribers = cols[2].find_all('div')
        subscribers_growth = subscribers[0].text.strip()
        subscribers_count = subscribers[1].text.strip()

        # Check if `LIVE` text is shown in subscriber count text. Eg: 161M LIVE
        subscribers_col_more = subscribers_count.split(' ')
        is_video_streamed = False

        # Check if there is more data in subscribers count text
        if len(subscribers_col_more) > 1:
            # The more data is probably the LIVE text
            is_video_streamed = True

        # Check if there is no subscriber growth
        if subscribers_growth == '--':
            subscribers_growth = None

        videos = cols[3].find_all('div')
        views_growth = videos[0].text.strip()

        # Check if there is no views growth
        if views_growth == '--':
            views_growth = None

        total_views = videos[1].text.strip()

        estimated_earnings = cols[4].text.strip()
        # Remove all garbage values. Eg: $11.7K \xa0\xa0-\xa0\xa0 $187.7K'
        estimated_earnings = estimated_earnings.split(' ')
        estimated_earnings = f'{estimated_earnings[0]} - {estimated_earnings[-1]}'

        record = DailyStat(
            date=date,
            subscribers_growth=subscribers_growth,
            subscribers_count=subscribers_count,
            is_video_streamed=is_video_streamed,
            views_growth=views_growth,
            total_views=total_views,
            estimated_earnings=estimated_earnings
        )

        data.append(record)

    return data


def social_blade_scrape(content: str) -> YouTubeChannel:
    # Create a BeautifulSoup object with the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit the tasks to the executor
        future_monthly_earning = executor.submit(monthly_earnings_search, soup)
        future_yearly_earning = executor.submit(yearly_earnings_search, soup)
        future_daily_stats = executor.submit(daily_stats_search, soup)

        # Wait for futures to complete
        wait([future_monthly_earning, future_yearly_earning, future_daily_stats])

        return YouTubeChannel(
            monthly_earning=future_monthly_earning.result(),
            yearly_earning=future_yearly_earning.result(),
            daily_stats=future_daily_stats.result()
        )


def get_username_from_url(url: str) -> Union[str, None]:
    # Example YouTube channel link: https://www.youtube.com/@MrFeast
    url_split = url.split('@')

    if len(url_split) > 0:
        return url_split[-1]


def youtube(url: str = None, channel_name: str = None, content: str = None) -> Union[YouTubeChannel, None]:
    """
    Priority order: content, channel_name, url
    Start scraping social blade easily.

    # Using URL
    >> channel = youtube(url='https://www.youtube.com/@MrFeast')

    # Using channel name
    >> channel = youtube(url='MrFeast')

    # Using your custom fetch content. This can be useful when you want to send custom header or use proxy for scraping
    >> channel = youtube(content=response.text)

    # Example usage
    >> channel.monthly_earning
    >> channel.yearly_earning
    >> channel.daily_stats

    You can also directly pass your html code to the keyword argument.

    :param url: YouTube channel url
    :param channel_name: YouTube channel name
    :param content: HTML code of the page
    :return: Union[YouTubeChannel, None]
    """

    if content:
        return social_blade_scrape(content)

    if not (url or channel_name):
        return None

    target_url = 'https://socialblade.com/youtube/c/'
    if channel_name:
        target_url += channel_name

    elif url:
        target_url += get_username_from_url(url)

    response = fetch(target_url)
    if not response.ok:
        return None

    return social_blade_scrape(response.text)

import asyncio
from typing import Union, List, Tuple

from bs4 import BeautifulSoup
import re

from dataclasses import dataclass, asdict

from src.social_blade_scraper.fetch import fetch
from json import dumps


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

    identifier: str = None
    profile: str = None
    banner: str = None
    category: str = None
    estimated_monthly_earning: str = None
    estimated_yearly_earning: str = None
    total_uploads: int = None
    total_subscribers: int = None
    total_views: int = None
    country: str = None
    date_created: str = None
    daily_stats: List[DailyStat] = None

    @property
    def __dict__(self) -> dict:
        return asdict(self)

    @property
    def json(self) -> str:
        return dumps(self.__dict__)


def identifier_search(soup: BeautifulSoup) -> Union[str, None]:
    """
    Logic to search channel identifier

    :param soup: BeautifulSoup object
    :return: str
    """

    tag = soup.select_one('#fav-bubble')
    if tag:
        return tag['class'][0]


def profile_search(soup: BeautifulSoup) -> Union[str, None]:
    """
    Logic to search profile url

    :param soup: BeautifulSoup object
    :return: str
    """

    tag = soup.select_one('#YouTubeUserTopInfoAvatar')
    if tag:
        return tag['src']


def estimated_monthly_earnings_search(soup: BeautifulSoup) -> Union[str, None]:
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


def estimated_yearly_earnings_search(soup: BeautifulSoup) -> Union[str, None]:
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


async def fetch_homepage(channel_name: str) -> Union[str, None]:
    """
    Returns home page source code

    :param channel_name: YouTube channel name
    :return: Union[str, None]
    """
    target_url = f'https://socialblade.com/youtube/c/{channel_name}'
    response = await fetch(target_url)

    if response.status_code == 200:
        return response.text


async def fetch_monthly_page(channel_name: str) -> Union[str, None]:
    """ Returns source code of monthly stats page

    :param channel_name: YouTube channel name
    :return: Union[str, None]
    """

    target_url = f'https://socialblade.com/youtube/c/{channel_name}/monthly'
    response = await fetch(target_url)

    if response.status_code == 200:
        return response.text


def total_uploads_search(soup: BeautifulSoup) -> Union[int, None]:
    """
    Logic to search total uploads

    :param soup: BeautifulSoup object
    :return: str
    """

    tag = soup.select_one('#youtube-stats-header-uploads')
    if tag:
        return int(tag.text.strip())


def total_subscribers_search(soup: BeautifulSoup) -> Union[str, None]:
    """
    Logic to search total subscribers

    :param soup: BeautifulSoup object
    :return: str
    """

    tag = soup.select_one('#youtube-stats-header-subs')
    if tag:
        return tag.text.strip()


def total_views_search(soup: BeautifulSoup) -> Union[int, None]:
    """
    Logic to search total views
    :param soup: BeautifulSoup object
    :return: str
    """

    tag = soup.select_one('#youtube-stats-header-views')
    if tag:
        return int(tag.text.strip())


def country_search(soup: BeautifulSoup) -> Union[str, None]:
    """
    Logic to search channel's country

    :param soup: BeautifulSoup object
    :return: str
    """

    tag = soup.select_one('#youtube-user-page-country')
    if tag:
        return tag.text.strip()


def date_created_search(soup: BeautifulSoup) -> Union[str, None]:
    """
    Logic to search channel's country

    :param soup: BeautifulSoup object
    :return: str
    """

    tags = soup.select('.YouTubeUserTopInfo')
    if not len(tags) > 0:
        return

    selected_tag = tags[-1]
    spans = selected_tag.find_all('span')
    return spans[-1].text.strip()


def channel_category_search(soup: BeautifulSoup) -> Union[str, None]:
    """
       Logic to search channel category

       :param soup: BeautifulSoup object
       :return: str
       """

    tag = soup.select_one('#youtube-stats-header-channeltype')
    if tag:
        return tag.text.strip()


async def home_page_scrape(channel_name: str, channel: YouTubeChannel) -> bool:
    """
    Returns True if home page is scraped successfully else false
    :param channel_name: YouTube channel name
    :param channel: temporary channel instance to store information
    :return: bool
    """

    code = await fetch_homepage(channel_name)
    if not code:
        return False

    soup = BeautifulSoup(code, 'html.parser')

    channel.date_created = date_created_search(soup)

    # Check if the page has date created information. If the page don't have, stop scanning further
    if not channel.date_created:
        # Using date_created field as a primary source to check whether the page
        # is valid or not
        return False

    channel.identifier = identifier_search(soup)
    channel.profile = profile_search(soup)
    channel.category = channel_category_search(soup)
    channel.banner = f'https://www.banner.yt/{channel.identifier}'
    channel.estimated_monthly_earning = estimated_monthly_earnings_search(soup)
    channel.estimated_yearly_earning = estimated_yearly_earnings_search(soup)
    channel.total_uploads = total_uploads_search(soup)
    channel.total_subscribers = total_subscribers_search(soup)
    channel.total_views = total_views_search(soup)
    channel.country = country_search(soup)
    return True


async def daily_stats_scrape(channel_name: str) -> List[DailyStat]:
    """
    Returns  30 days daily stats

    :param channel_name: YouTube channel name
    :return:
    """

    code = await fetch_monthly_page(channel_name)
    if not code:
        return []

    soup = BeautifulSoup(code, 'html.parser')
    return daily_stats_search(soup)


async def social_blade_scrape(channel_name: str) -> Union[YouTubeChannel, None]:
    # Create a BeautifulSoup object with the HTML content

    channel = YouTubeChannel()
    scrape_tasks = await asyncio.gather(home_page_scrape(channel_name, channel), daily_stats_scrape(channel_name))
    home_page_scrape_future, daily_stats_scrape_future, = scrape_tasks

    # Check if the home page is scraped successfully
    if not home_page_scrape_future:
        # Maybe got 404 status because channel don't exist or something went wrong
        return None

    channel.daily_stats = daily_stats_scrape_future
    return channel


def get_username_from_url(url: str) -> Union[str, None]:
    # Example YouTube channel link: https://www.youtube.com/@MrFeast
    url_split = url.split('@')

    if len(url_split) > 0:
        return url_split[-1]


async def youtube(url: str = None, channel_name: str = None) -> Union[YouTubeChannel, None]:
    """
    Priority order: channel_name, url
    Start scraping social blade easily.

    # Using URL
    >> channel = youtube(url='https://www.youtube.com/@MrFeast')

    # Using channel name
    >> channel = youtube(url='MrFeast')

    # Example usage
    >> channel.monthly_earning
    >> channel.yearly_earning
    >> channel.daily_stats

    You can also directly pass your html code to the keyword argument.

    :param url: YouTube channel url
    :param channel_name: YouTube channel name
    :return: Union[YouTubeChannel, None]
    """

    if not (url or channel_name):
        return None

    if url:
        # Extract username from URL
        channel_name = get_username_from_url(url)

    if not channel_name:
        return None

    return await social_blade_scrape(channel_name)


def subscribers_count_access_tokens_search(soup: BeautifulSoup) -> Union[Tuple[str, str], None]:
    """
    Finds tokens to access subscribers count page

    :param soup: BeautifulSoup object
    :return: Union[Tuple[str, str], None]:
    """

    encoded_query = soup.select_one('#rawUser')
    token = soup.select_one('#rawToken')

    if encoded_query and token:
        return encoded_query.text.strip(), token.text.strip()


async def subscribers_count_access_tokens(channel_name: str) -> Union[Tuple[str, str], None]:
    target_url = f'https://socialblade.com/youtube/user/{channel_name}/realtime'
    response = await fetch(target_url)

    if not response.status_code == 200:
        return None

    code = response.text
    soup = BeautifulSoup(code, 'html.parser')
    return subscribers_count_access_tokens_search(soup)


async def live_subscriber_count(encoded_query: str, token: str) -> Union[int, None]:
    """
    Returns live subscriber number

    :param encoded_query User Query
    :param token: View token
    :return: str
    """

    url = 'https://bastet.socialblade.com/youtube/lookup'
    params = {
        'query': encoded_query,
        'token': token
    }

    response = await fetch(url, params=params, extra_headers={
        'Origin': 'https://socialblade.com',
        'Referer': 'https://socialblade.com/',
    })

    if response.status_code == 200:
        return int(response.text)

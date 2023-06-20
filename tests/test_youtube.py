import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.social_blade_scraper.stats.youtube import youtube, subscribers_count_access_tokens, live_subscriber_count

print('Please provide channel handle. Eg: MrFeast')
target_channel = input('Type here: ')


def show_basic():
    channel = youtube(channel_name=target_channel)
    if not channel:
        print('Channel don\'t exist')
        return

    print('-------------------------------------------------------')
    print('Monthly earnings: ', channel.estimated_monthly_earning)
    print('Yearly earnings: ', channel.estimated_yearly_earning)
    print('-------------------------------------------------------\n')

    print('Daily stats')

    print('-------------------------------------------------------')
    for stat in channel.daily_stats:
        print(f'{stat.date} | {stat.estimated_earnings} | {stat.subscribers_count} | {stat.total_views}')
    print('-------------------------------------------------------')

    print('Total uploads:', channel.total_uploads)
    print('Total subscribes:', channel.total_subscribers)
    print('Total views:', channel.total_views)
    print('Country:', channel.country)
    print('Date created:', channel.date_created)


show_basic()
tokens = subscribers_count_access_tokens(channel_name=target_channel)

if tokens:
    encoded_user, token = tokens
    total_subscribers = live_subscriber_count(encoded_user, token)
    print(f'Live subscribers: {total_subscribers}')

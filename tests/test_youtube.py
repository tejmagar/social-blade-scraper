import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.social_blade_scraper.stats.youtube import youtube

print(youtube(channel_name='MrFeast'))

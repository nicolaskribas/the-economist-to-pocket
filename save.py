import aiohttp
import asyncio
import calendar
import feedparser
import os
import time
from pocket import Pocket

topics = [
    'the-world-this-week',
    'leaders',
    'letters',
    'by-invitation',
    'briefing',
    'united-states',
    'the-americas',
    'asia',
    'china',
    'middle-east-and-africa',
    'europe',
    'britain',
    'international',
    'special-report',
    'business',
    'finance-and-economics',
    'science-and-technology',
    'culture',
    'economic-and-financial-indicators',
    'graphic-detail',
    'obituary',
]

global_tag = 'The Economist'


def published_since(time):
    return lambda article: calendar.timegm(article.published_parsed) >= time


async def fetch_rss(session, topic):
    feed_url = 'https://www.economist.com/' + topic + '/rss.xml'

    async with session.get(feed_url) as resp:
        feed = await resp.text()
        parsed = feedparser.parse(feed)

        one_day_ago = int(time.time()) - 24 * 60 * 60
        articles = filter(published_since(one_day_ago), parsed.entries)

        return parsed.feed.title, articles


async def get_recent_articles():
    async with aiohttp.ClientSession() as session:
        articles = map(lambda topic: fetch_rss(session, topic), topics)
        return await asyncio.gather(*articles)


def get_saved_articles(pocket):
    three_days_ago = int(time.time()) - 3 * 24 * 60 * 60
    result = pocket.get(state='all', tag=global_tag,
                        detailType='simple', since=three_days_ago)

    saved = result[0]['list']
    saved = saved.values() if isinstance(saved, dict) else saved
    return set(map(lambda article: article['given_url'], saved))


def main():
    consumer_key = os.environ['CONSUMER_KEY']
    access_token = os.environ['ACCESS_TOKEN']

    pocket = Pocket(consumer_key, access_token)

    try:
        already_saved = get_saved_articles(pocket)
    except Exception as e:
        print('Error querying Pocket about saved articles:', e)
        return

    for topic_tag, articles in asyncio.run(get_recent_articles()):
        for article in articles:
            if article.link not in already_saved:
                pocket.bulk_add(title=article.title, url=article.link,
                                tags=[global_tag, topic_tag])
                print('Saving: ' + topic_tag + ' | ' + article.title)

    # send one request containing all the articles to be saved
    if pocket._bulk_query:
        try:
            pocket.commit()
        except Exception as e:
            print('Error saving articles to Pocket:', e)


if __name__ == '__main__':
    main()


def lambda_handler(event, context):  # aws lambda function
    main()

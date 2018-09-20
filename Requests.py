import asyncio
import aiohttp
import json
import configparser
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime as dt

import feedparser

config = configparser.ConfigParser()
config.read('Settings')


ip_api_token = config['SETTINGS']['IP Locater Api Code']

weather_api_token = config['SETTINGS']['Weather Api Code']
weather_lang = config['SETTINGS']['Language']
weather_unit = config['SETTINGS']['Country Code']

def main():
    r = Request()
    loop = asyncio.new_event_loop()
    print( json.dumps(loop.run_until_complete( r.get_weather_data() )))


class Request:

    async def get( url ):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get( url ) as response:
                return await response.text()

    async def get_weather_data():
        location_data = await Request.get_location_data()
        weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, location_data['latitude'], location_data['longitude'], weather_lang, weather_unit)

        return json.loads( await Request.get( weather_req_url ))

    async def get_location_data():
        location_req_url = "http://api.ipstack.com/%s?access_key=%s&output=json" % (await Request.get_ip(), ip_api_token )
        r = await Request.get(location_req_url)
        return json.loads(r)

    async def get_ip():
        ip_url = "http://jsonip.com/"
        req = await Request.get(ip_url)
        ip_json = json.loads(req)
        return ip_json['ip']

    async def get_news_feed():
        feed = await Request.get("https://news.google.com/news/rss" )#% config['SETTINGS']['Country Code'])
        return feedparser.parse( feed )

    async def get_calendar_data():
        SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

        store = file.Storage('assets/token.json')
        creds = store.get()

        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('assets/credentials.json', SCOPES )
            creds = tools.run_flow(flow, store)
        service = build( 'calendar', 'v3', http=creds.authorize(Http()))
        # Call the calendar API
        now = dt.datetime.utcnow().isoformat() + 'Z'
        events_results = service.events().list(calendarId='primary', timeMin=now, maxResults=3, singleEvents=True, orderBy='startTime').execute()

        return events_results.get( 'items', [] )


if __name__ == '__main__':
    main()

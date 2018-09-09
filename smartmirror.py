import asyncio
from Display import *
from Requests import Request

def main():
    loop = asyncio.new_event_loop()
    r = Request()
    weather_data = loop.run_until_complete( r.get_weather_data() )
    news_data = loop.run_until_complete( r.get_news_feed() )
    calendar_data = loop.run_until_complete( r.get_calendar_data() )

    window = FullscreenWindow()
    window.update_clock()
    window.update_news( news_data )
    window.update_weather( weather_data )
    window.update_calendar( calendar_data )
    window.tk.mainloop()
    #TODO write your own mainloop :)
    #TODO update idvidiual screen elements

if __name__ == '__main__':
    main()

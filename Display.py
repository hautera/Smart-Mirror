import datetime as dt
import time
import configparser
import PIL.Image
import PIL.ImageTk
from tkinter import *
import asyncio
from Requests import Request


config = configparser.ConfigParser()
config.read('Settings')

GOOGLE_DATE_FORMAT = r'%Y-%m-%d'
GOOGLE_TIME_FORMAT = r'T%H:%M'


time_format = '%H:%M' if  config['SETTINGS']['Twenty Four Hour Clock'] == 'True' else '%I:%M %p'

date_format = config['SETTINGS']['Date Format'].replace( "M", r'%b').replace("D", r'%d').replace("Y", '%y')

weather_lang = config['SETTINGS']['Language']
weather_unit = config['SETTINGS']['Country Code']

XLARGE_TEXT_SIZE = 94
LARGE_TEXT_SIZE = 48
MEDIUM_TEXT_SIZE = 28
SMALL_TEXT_SIZE = 18

icon_lookup = {
    'clear-day': "assets/Sun.png",  # clear sky day
    'wind': "assets/Wind.png",   #wind
    'cloudy': "assets/Cloud.png",  # cloudy day
    'partly-cloudy-day': "assets/PartlySunny.png",  # partly cloudy day
    'rain': "assets/Rain.png",  # rain day
    'snow': "assets/Snow.png",  # snow day
    'snow-thin': "assets/Snow.png",  # sleet day
    'fog': "assets/Haze.png",  # fog day
    'clear-night': "assets/Moon.png",  # clear sky night
    'partly-cloudy-night': "assets/PartlyMoon.png",  # scattered clouds night
    'thunderstorm': "assets/Storm.png",  # thunderstorm
    'tornado': "assests/Tornado.png",    # tornado
    'hail': "assests/Hail.png"  # hail
}

class Clock(Frame):
    # TODO analog clock ?
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        # initialize time label
        self.timeLbl = Label(self, font=('Helvetica', LARGE_TEXT_SIZE), fg="white", bg="black")
        self.timeLbl.pack(side=TOP, anchor=E)

        # initialize day of week
        self.dayOWLbl = Label(self, text='', font=('Helvetica', SMALL_TEXT_SIZE), fg="white", bg="black")
        self.dayOWLbl.pack(side=TOP, anchor=E)

        # initialize date label
        self.dateLbl = Label(self, text='', font=('Helvetica', SMALL_TEXT_SIZE), fg="white", bg="black")
        self.dateLbl.pack(side=TOP, anchor=E)


    def update( self ):
        new_date_time = dt.datetime.now()
        day_of_week = new_date_time.strftime('%A')
        date = new_date_time.strftime(date_format)
        time = new_date_time.strftime(time_format)
        self.timeLbl.config(text=time)
        self.dayOWLbl.config(text=day_of_week)
        self.dateLbl.config(text=date)

class Weather(Frame):

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')

        self.windFrm = Frame(self, bg='black')
        self.windFrm.pack( side=TOP, anchor=W )

        self.degreeFrm = Frame(self, bg="black")
        self.degreeFrm.pack(side=TOP, anchor=W)

        self.temperatureLbl = Label(self.degreeFrm, font=('Helvetica', XLARGE_TEXT_SIZE), fg="white", bg="black")
        self.temperatureLbl.pack(side=LEFT, anchor=N)

        self.iconLbl = Label(self.degreeFrm, bg="black")
        self.iconLbl.pack(side=LEFT, anchor=N, padx=20)

        self.windLbl = Label( self.windFrm, fg='white', bg='black' )
        self.windLbl.pack( side=BOTTOM, anchor=N, padx=20 )

        self.wind_barb_label = Label(self.windFrm, bg='black')
        self.wind_barb_label.pack(side=LEFT, anchor=N, padx=20)

        self.currentlyLbl = Label(self, font=('Helvetica', MEDIUM_TEXT_SIZE), fg="white", bg="black")
        self.currentlyLbl.pack(side=TOP, anchor=W)

        self.forecastLbl = Label(self, font=('Helvetica', SMALL_TEXT_SIZE), fg="white", bg="black", justify=LEFT, wraplength=200)
        self.forecastLbl.pack(side=TOP, anchor=W)

        self.locationLbl = Label(self, font=('Helvetica', SMALL_TEXT_SIZE), fg="white", bg="black")
        self.locationLbl.pack(side=TOP, anchor=W)

    async def update( self ):
        weather_obj = await Request.get_weather_data()
        degree_sign= u'\N{DEGREE SIGN}'
        temperature = "%s%s" % (str(int(weather_obj['currently']['temperature'])), degree_sign)

        # Get weather in english description
        currently = weather_obj['currently']['summary']
        forecast = weather_obj["hourly"]["summary"]
        # TODO FORMAT THE FORECAST NICELY SUCH THAT THERE IS NO OVERLAP :)

        # Lil weather icon
        icon_id = weather_obj['currently']['icon']
        icon = icon_lookup['rain'] if not icon_id in icon_lookup else icon_lookup[icon_id]
        image = PIL.Image.open(icon)
        image = image.resize((100, 100), PIL.Image.ANTIALIAS)
        image = image.convert('RGB')
        photo = PIL.ImageTk.PhotoImage(image)

        # Get that there wind
        wind_speed = int(weather_obj['currently']['windSpeed'])
        wind_gust = int(weather_obj['currently']['windGust'])
        wind_direction = int(weather_obj['currently']['windBearing'])

        # Cardinal direction of the wind (There's gotta be a better way to do this )
        if wind_direction in range(0,30) or wind_direction in range(330, 360):
            cardinal_wind_direction = "N"
        elif wind_direction in range(30,60):
            cardinal_wind_direction = "NE"
        elif wind_direction in range(60, 120):
            cardinal_wind_direction = "E"
        elif wind_direction in range(120, 150):
            cardinal_wind_direction = "SE"
        elif wind_direction in range(150, 210):
            cardinal_wind_direction = "S"
        elif wind_direction in range(210, 240):
            cardinal_wind_direction = "SW"
        elif wind_direction in range(240, 300):
            cardinal_wind_direction = "W"
        else:
            cardinal_wind_direction = "NW"

        wind_str = "%dknts %s, with gusts of %dknts" % (wind_speed, cardinal_wind_direction, wind_gust )

        # Rounds the windspeed to the nearest 5 knts
        wind_est = wind_speed  - (wind_speed % 5)

        # Gets the wind barb image ready
        wind_image = PIL.Image.open( "assets/PNG/%dknts.png" % wind_est ) if wind_est <= 30 else PIL.Image.open( "assets/PNG/panic.png" )
        wind_image = wind_image.rotate( wind_direction ).resize((100, 100), PIL.Image.ANTIALIAS).convert('RGB')
        wind_image = PIL.ImageTk.PhotoImage( wind_image )

        self.iconLbl.config(image=photo)
        self.iconLbl.image = photo

        self.wind_barb_label.config(image=wind_image)
        self.wind_barb_label.image = wind_image

        self.currentlyLbl.config(text=currently)
        self.forecastLbl.config(text=forecast)
        self.temperatureLbl.config(text=temperature)
        self.windLbl.config(text=wind_str)


    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32

class News(Frame):

    class NewsHeadline(Frame):
        def __init__(self, parent, event_name=""):
            Frame.__init__(self, parent, bg='black')

            image = PIL.Image.open("assets/Newspaper.png")
            image = image.resize((25, 25), PIL.Image.ANTIALIAS)
            image = image.convert('RGB')
            photo = PIL.ImageTk.PhotoImage(image)

            self.iconLbl = Label(self, bg='black', image=photo)
            self.iconLbl.pack(side=LEFT, anchor=N)

            self.eventNameLbl = Label(self, text=event_name, font=('Helvetica', SMALL_TEXT_SIZE), fg="white", bg="black")
            self.eventNameLbl.pack(side=LEFT, anchor=N)

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg='black')

        self.newsLbl = Label(self, text='News', font=('Helvetica', MEDIUM_TEXT_SIZE), fg="white", bg="black")
        self.newsLbl.pack(side=TOP, anchor=W)

        self.headlinesContainer = Frame(self, bg="black")
        self.headlinesContainer.pack(side=TOP)


    async def update(self):
        feed = await Request.get_news_feed()
        for widget in self.headlinesContainer.winfo_children():
            widget.destroy()

        for post in feed.entries[0:5]:
            headline = self.NewsHeadline(self.headlinesContainer, post.title)
            headline.pack(side=TOP, anchor=W)

class Calendar(Frame):

    class CalendarEvent(Frame):
        def __init__(self, parent, event_name, event_start_date):
            Frame.__init__(self, parent, bg='black')
            dt_format = date_format
            if 'dateTime' in event_start_date.keys():
                # Formats the date and time nicely :)
                dt_format = date_format + "\n" + time_format
                date = dt.datetime.strptime( event_start_date['dateTime'][:-9], GOOGLE_DATE_FORMAT + GOOGLE_TIME_FORMAT )
            else:
                date = dt.datetime.strptime(event_start_date['date'], GOOGLE_DATE_FORMAT)

            self.eventNameLbl = Label(self, text=event_name +": "+date.strftime(dt_format), font=('Helvetica', SMALL_TEXT_SIZE), fg="white", bg="black")

            self.eventNameLbl.pack(side=TOP, anchor=E)

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.calendarLbl = Label(self, text='Upcoming Schedule', font=('Helvetica', MEDIUM_TEXT_SIZE), fg="white", bg="black")
        self.calendarLbl.pack(side=TOP, anchor=E)
        self.calendarEventContainer = Frame(self, bg='black')
        self.calendarEventContainer.pack(side=TOP, anchor=E)

    async def update(self):
        events = await Request.get_calendar_data()
        for widget in  self.calendarEventContainer.winfo_children():
            widget.destroy()

        for event in events:
            calendar_event = self.CalendarEvent(self.calendarEventContainer, event["summary"], event['start'])
            calendar_event.pack(side=TOP, anchor=E)

class FullscreenWindow:

    def __init__(self):
        self.tk = Tk()
        self.tk.configure(background='black')
        self.topFrame = Frame(self.tk, background = 'black')
        self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)

        self.bottomFrame = Frame(self.tk, background = 'black')
        self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)

        self.is_full_screen = False

        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        self.tk.bind('s', self.show_widgets)
        self.tk.bind('h', self.hide_widgets)

        self.widgets_exist = {}
        self.widgets = {}

        # weather
        self.widgets_exist['weather'] = config["DISPLAY OPTIONS"]["Weather"] == 'True'
        if self.widgets_exist['weather'] :
            self.widgets['weather'] = Weather(self.topFrame)

        # clock
        self.widgets_exist['clock'] = config['DISPLAY OPTIONS']['Clock'] == 'True'
        if self.widgets_exist['clock']:
            self.widgets['clock'] = Clock(self.topFrame)

        # news ( I don't like the news )
        self.widgets_exist['news'] = config["DISPLAY OPTIONS"]["News"] == "True"
        if self.widgets_exist['news']:
            self.widgets['news'] = News(self.bottomFrame)

        # calender - removing for now
        self.widgets_exist['calendar'] = config["DISPLAY OPTIONS"]["Calendar"] == "True"
        if self.widgets_exist['calendar']:
            self.widgets['calendar'] = Calendar(self.bottomFrame)

        for widget in self.widgets.values():
            widget.pack(side = LEFT, anchor=S, padx=100, pady=60)

    def toggle_fullscreen(self, event=None):
        self.is_full_screen = not self.is_full_screen  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.is_full_screen)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

    def hide_widgets(self, event=None):
        for widget in self.widgets.values():
            widget.pack_forget()

    def show_widgets(self, event=None):
        for widget in self.widgets.values():
            widget.pack(side = LEFT, anchor=S, padx=100, pady=60)

    async def update_clock(self):
        if self.widgets_exist['clock']:
            self.widgets['clock'].update()

    async def update_news( self ):
        if self.widgets_exist['news']:
            return await self.widgets['news'].update()

    async def update_weather( self ):
        if self.widgets_exist['weather']:
            return await self.widgets['weather'].update( )

    async def update_calendar(self):
        if self.widgets_exist['calendar']:
            return await self.widgets['calendar'].update()

    def quit( self ):
        self.tk.destroy()

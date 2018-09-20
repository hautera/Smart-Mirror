import asyncio
from Display import *
import speech_recognition as sr
from wit import Wit
import functools
import configparser

config = configparser.ConfigParser()
config.read('Settings')

WIT_ACCESS_TOKEN = "CW66PU3TS5SIUGQYWXQXPOJ6VSCWSAYV"
SLEEP_AFTER_MINUTES = int( config['DISPLAY OPTIONS']['Sleep After'])
WINDOW_UPDATES_PER_SECOND = 6

class app():
    def __init__(self):
        # App global variables
        self.loop = asyncio.get_event_loop()
        self.wit_client = Wit(access_token=WIT_ACCESS_TOKEN)
        self.window = FullscreenWindow()
        self.sleep_timer = 0
        self.display_asleep = False


        # Defines some nice app window update behavior

        #starts the main loop
        self.loop.run_until_complete(self.app_main_loop())


    async def app_main_loop(self):
        # get some microphones up in here
        m = sr.Microphone()
        r = sr.Recognizer()

        with m as source:
            r.adjust_for_ambient_noise(source)
        # APP main loop
        audio = r.listen_in_background(source, functools.partial(self.audio_callback))
        try:
            await self.whole_window_update()
            while True:
                self.window.tk.update_idletasks()
                self.window.tk.update()
                await asyncio.sleep( 1.0/WINDOW_UPDATES_PER_SECOND )
                if not self.display_asleep:
                    if self.sleep_timer > WINDOW_UPDATES_PER_SECOND * 60 * SLEEP_AFTER_MINUTES:
                        await self.sleep()
                        r.adjust_for_ambient_noise(source)
                    else:
                        await self.loop.create_task(self.window.update_clock())

                    self.sleep_timer += 1

        except KeyboardInterrupt:
            print("Shutting down")
            audio.stop_listening()
            self.window.quit()
            self.loop.close()

    async def sleep(self):
        self.sleep_timer = 0
        self.display_asleep = True
        self.window.hide_widgets()

    async def awake(self):
        self.display_asleep =False
        await self.whole_window_update()
        self.window.show_widgets()

    # Handles voice command call backs
    def audio_callback( self, recognizer, audio):
        data = audio.get_wav_data()
        json_data = self.wit_client.speech(data, None, {'Content-Type': 'audio/wav'})
        self.voice_control_callback(json_data)

    def voice_control_callback(self, json_data):
        print( json_data )
        if 'self' in json_data['entries']:
            if 'hello' in json_data['entities']:
                self.loop.create_task(self.awake())

            if 'bye' in json_data['entities']:
                self.loop.create_task(self.sleep())

    async def whole_window_update(self):
        await self.loop.create_task(self.window.update_news())
        await self.loop.create_task(self.window.update_clock())
        await self.loop.create_task(self.window.update_calendar())
        await self.loop.create_task(self.window.update_weather())

def main():
    main_app = app()

if __name__ == '__main__':
    main()

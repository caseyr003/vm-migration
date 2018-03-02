from kivy.properties import BooleanProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

import webbrowser


class HelpScreen(Screen):

    carousel = ObjectProperty()
    next_btn = ObjectProperty()
    prev_btn = ObjectProperty()

    first = True
    last = False
    index = 0

    def __init__(self, *args, **kwargs):
        super(HelpScreen, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.prepare, 0)

    def prepare(self, *args):
        images = ['data/help/1.png', 'data/help/2.png', 'data/help/3.png', 'data/help/4.png', 'data/help/5.png']
        # for img in images:
        #     image = AsyncImage(source=img, allow_stretch=True)
        #     self.carousel.add_widget(image)
        screen1 = HelpScreen1()
        screen2 = HelpScreen2()
        screen3 = HelpScreen3()
        screen4 = HelpScreen4()
        screen5 = HelpScreen5()
        self.carousel.add_widget(screen1)
        self.carousel.add_widget(screen2)
        self.carousel.add_widget(screen3)
        self.carousel.add_widget(screen4)
        self.carousel.add_widget(screen5)

    def next(self):
        print self.carousel.current_slide.name
        if self.carousel.current_slide.name == 'helpscreen5':
            App.get_running_app().view_accounts()
            return
        self.prepare_next_screen()
        self.carousel.load_next()

    def previous(self):
        print self.carousel.current_slide.name
        self.prepare_prev_screen()
        self.carousel.load_previous()

    def prepare_next_screen(self):
        if self.carousel.current_slide.name == 'helpscreen4':
            self.next_btn.text = 'Get Started'
            self.next_btn.background_color = [0.02, 0.45, 0.81, 1]
        else:
            self.next_btn.text = 'Next'
            self.next_btn.background_color = [0.75, 0.75, 0.75, 1]
            self.prev_btn.disabled = False

    def prepare_prev_screen(self):
        if self.carousel.current_slide.name == 'helpscreen2':
            self.prev_btn.disabled = True
        else:
            self.next_btn.text = 'Next'
            self.next_btn.background_color = [0.75, 0.75, 0.75, 1]
            self.prev_btn.disabled = False

class HelpScreen1(BoxLayout):
    name = 'helpscreen1'

class HelpScreen2(BoxLayout):
    name = 'helpscreen2'

    def get_info(self):
        print "get info"
        webbrowser.open("https://docs.us-phoenix-1.oraclecloud.com/Content/API/Concepts/apisigningkey.htm?Highlight=User%20OCID")


class HelpScreen3(BoxLayout):
    name = 'helpscreen3'

class HelpScreen4(BoxLayout):
    name = 'helpscreen4'

class HelpScreen5(BoxLayout):
    name = 'helpscreen5'

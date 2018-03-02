from kivy.properties import BooleanProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import Screen
from kivy.app import App


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
        for img in images:
            image = AsyncImage(source=img, allow_stretch=True)
            self.carousel.add_widget(image)

    def next(self):
        if self.carousel.current_slide.source == 'data/help/5.png':
            App.get_running_app().view_accounts()
            return
        self.prepare_next_screen()
        self.carousel.load_next()

    def previous(self):
        self.prepare_prev_screen()
        self.carousel.load_previous()

    def prepare_next_screen(self):
        if self.carousel.current_slide.source == 'data/help/4.png':
            self.next_btn.text = 'Get Started'
        else:
            self.next_btn.text = 'Next'
            self.prev_btn.disabled = False

    def prepare_prev_screen(self):
        if self.carousel.current_slide.source == 'data/help/2.png':
            self.prev_btn.disabled = True
        else:
            self.next_btn.text = 'Next'
            self.prev_btn.disabled = False

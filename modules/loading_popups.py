from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class LoadingPopup(FloatLayout):
    popup_container = ObjectProperty(None)
    popup_label = ObjectProperty(None)

import os
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.button import Button

from loading_popups import LoadDialog


# filechoosers.py

# Widget to select which image file the user wants to upload
class ImageFileChooser(BoxLayout):
    file_btn = ObjectProperty(None)
    file_btn_name = StringProperty()
    image_type = StringProperty()

    def __init__(self, *args, **kwargs):
        super(ImageFileChooser, self).__init__(*args, **kwargs)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select VMDK or QCOW2 file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        try:
            image_file_path = os.path.join(path, filename[0])
        except:
            return
        vmdk_type = image_file_path[-4:]
        qcow2_type = image_file_path[-5:]

        if vmdk_type.lower() == 'vmdk':
            self.image_type='VMDK'
            self.parent.parent.parent.image_file_path = image_file_path
            self.parent.parent.parent.image_type = self.image_type
            self.file_btn.text = image_file_path
            self.dismiss_popup()
        elif qcow2_type.lower() == 'qcow2':
            self.image_type = 'QCOW2'
            self.parent.parent.parent.image_file_path = image_file_path
            self.parent.parent.parent.image_type = self.image_type
            self.file_btn.text = image_file_path
            self.dismiss_popup()
        else:
            self.dismiss_popup()
            content = LoadingPopup()
            self._popup = Popup(title="Oracle Cloud Infrastructure VM Migration", content=content,
                                size_hint=(0.8, 0.4))
            btn = Button(text="Okay", size_hint_y=None, height=100, on_release=lambda btn: self.dismiss_popup())
            self._popup.content.popup_container.add_widget(btn)
            self._popup.content.popup_label.text = "Please choose VMDK or QCOW2 file"
            self._popup.open()
            return


# Widget to select location of private key for account
class KeyFileChooser(BoxLayout):
    file_btn = ObjectProperty(None)
    file_btn_name = StringProperty()

    def __init__(self, *args, **kwargs):
        super(KeyFileChooser, self).__init__(*args, **kwargs)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select Private Key", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        try:
            key_file_path = os.path.join(path, filename[0])
        except:
            return
        self.parent.parent.parent.key_file_path = key_file_path
        self.file_btn.text = key_file_path
        self.dismiss_popup()

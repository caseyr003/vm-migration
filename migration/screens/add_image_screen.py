"""
Oracle VM Migration
=====

Application to move local images in VMDK or QCOW2 format to OCI VM

"""

from threading import Thread

from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.app import App


__version__ = '0.1'



class AddImageScreen(Screen):
    image_file_path = ObjectProperty(None)
    image_type = StringProperty()
    selected_bucket = ObjectProperty(None)
    selected_compartment = ObjectProperty(None)
    custom_image_name = ObjectProperty(None)
    account = ObjectProperty(None)
    bucket_list = ObjectProperty(None)
    compartment_list = ObjectProperty(None)
    bucket_dropdown = ObjectProperty(None)
    compartment_dropdown = ObjectProperty(None)
    image_chooser = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(AddImageScreen, self).__init__(*args, **kwargs)

    def get_compartment(self, compartment):
        App.get_running_app().show_load()
        self.selected_compartment = compartment
        Thread(target=self.get_bucket_list).start()

    def get_bucket_list(self):
        compartment = self.selected_compartment
        config_file = App.get_running_app().config_file
        self.bucket_dropdown.bucket_dropdown.clear_widgets()
        self.bucket_dropdown.bucket_button.text = '-'
        self.bucket_dropdown.bucket_button.disabled = True
        bucket_res = self.account.get_buckets(config_file, compartment.id)
        if bucket_res[1]:
            self.bucket_list = bucket_res[0]
            try:
                self.bucket_dropdown.create_bucket_dropdown(self.bucket_list)
            except:
                App.get_running_app().dismiss_popup()

            App.get_running_app().dismiss_popup()
        else:
            self.bucket_dropdown.bucket_button.text = '-'
            self.bucket_dropdown.bucket_button.disabled = True
            self.bucket_dropdown.bucket_dropdown.clear_widgets()
            App.get_running_app().dismiss_popup()
            App.get_running_app().show_load()
            App.get_running_app().show_error("Compartment is Unavailable")

    def get_bucket(self, bucket):
        self.selected_bucket = bucket

    def add_vm(self):
        App.get_running_app().load_vm_options(self.account, self.selected_compartment,
                                              self.selected_bucket, self.image_file_path,
                                              self.custom_image_name.text, self.image_type)
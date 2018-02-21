"""
Virtual Machine Migration Tool
=====

Application to move local images in VMDK or QCOW2 format to OCI VM

"""

from threading import Thread

from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.app import App

from account_data import Account

class AddAccountScreen(Screen):
    display_name_input = ObjectProperty(None)
    tenancy_ocid_input = ObjectProperty(None)
    user_ocid_input = ObjectProperty(None)
    region_input = ObjectProperty(None)
    fingerprint_input = ObjectProperty(None)
    key_file_path = ObjectProperty(None)
    key_chooser = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(AddAccountScreen, self).__init__(*args, **kwargs)

    def cancel(self):
        self.clear_input()
        self.parent.transition.direction = 'right'
        self.parent.current = App.get_running_app().accounts.name

    def clear_input(self):
        self.display_name_input.text = ''
        self.tenancy_ocid_input.text = ''
        self.user_ocid_input.text = ''
        self.region_input.text = ''
        self.fingerprint_input.text = ''
        self.key_file_path = ''
        self.key_chooser.file_btn.text = 'Choose File'

    def save_account(self):
        App.get_running_app().show_load()
        Thread(target=self.save_account_thread).start()

    def save_account_thread(self):
        name = self.display_name_input.text
        tenancy_ocid = self.tenancy_ocid_input.text
        user_ocid = self.user_ocid_input.text
        region = self.region_input.text
        fingerprint = self.fingerprint_input.text
        key_location = self.key_file_path

        if (name == '' or tenancy_ocid == '' or user_ocid == '' or region == ''
            or fingerprint == '' or key_location == None):
            App.get_running_app().show_error("Error: Missing Fields")
            return

        config_file = App.get_running_app().config_file
        data_file = App.get_running_app().data_file

        new_account = Account(name, tenancy_ocid, user_ocid, region, fingerprint, key_location, [])

        if new_account.is_active(config_file):
            new_account.save_account(data_file)
        else:
            App.get_running_app().show_error("Error Connecting to OCI Account")
            return

        App.get_running_app().load_data()
        self.clear_input()
        App.get_running_app().dismiss_popup()
        self.parent.transition.direction = 'right'
        self.parent.current = App.get_running_app().accounts.name

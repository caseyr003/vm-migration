"""
Oracle VM Migration
=====

Application to move local images in VMDK or QCOW2 format to OCI VM

"""

from kivy.properties import ListProperty, ObjectProperty, Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.app import App


class Accounts(Screen):
    data = ListProperty()
    account_listview = ObjectProperty()
    title_box = ObjectProperty()
    get_started_btn = None

    def __init__(self, *args, **kwargs):
        super(Accounts, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.prepare, 0)

    def prepare(self, *args):
        if self.data == []:
            self.get_started_btn = Button(text='Get Started', bold=True, font_size='18dp',color=[1,1,1,1])
            self.get_started_btn.bind(on_press=self.get_help)
            self.title_box.add_widget(self.get_started_btn)
            self.title_box.height = '154dp'
        else:
            try:
                self.title_box.remove_widget(self.get_started_btn)
                self.title_box.height = '54dp'
            except:
                print "no button"

    def get_help(self, instance):
        App.get_running_app().get_help()

    def args_converter(self, row_index, item):
        return {
            'account_index': row_index,
            'account_name': item.name,
            'account_tenancy': item.tenancy_ocid,
            'account_user': item.user_ocid,
            'account_region': item.region,
            'account_fingerprint': item.fingerprint,
            'account_key': item.key_location}

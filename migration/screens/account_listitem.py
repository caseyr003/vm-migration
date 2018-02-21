"""
Oracle VM Migration
=====

Application to move local images in VMDK or QCOW2 format to OCI VM

"""

from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from kivy.app import App



__version__ = '0.1'



class AccountListItem(BoxLayout):
    account_index = NumericProperty()
    account_name = StringProperty()
    account_tenancy = StringProperty()
    account_user = StringProperty()
    account_region = StringProperty()
    account_fingerprint = StringProperty()
    account_key = StringProperty()

    def __init__(self, **kwargs):
        print kwargs
        super(AccountListItem, self).__init__(**kwargs)

    def account_details(self):
        App.get_running_app().load_account(self.account_index)
"""
Oracle VM Migration
=====

Application to move local images in VMDK or QCOW2 format to OCI VM

"""

from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.screenmanager import Screen



__version__ = '0.1'


class Accounts(Screen):
    data = ListProperty()
    account_listview = ObjectProperty()

    def args_converter(self, row_index, item):
        return {
            'account_index': row_index,
            'account_name': item.name,
            'account_tenancy': item.tenancy_ocid,
            'account_user': item.user_ocid,
            'account_region': item.region,
            'account_fingerprint': item.fingerprint,
            'account_key': item.key_location}
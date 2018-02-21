"""
Oracle VM Migration
=====

Application to move local images in VMDK or QCOW2 format to OCI VM

"""

from kivy.properties import ListProperty, Clock, ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.app import App


__version__ = '0.1'


class VMScreen(Screen):
    data = ListProperty()
    account_title = ObjectProperty()
    account = ObjectProperty()

    def args_converter(self, row_index, item):
        return {
            'vm_index': row_index,
            'vm_name': item['name'],
            'vm_ocid': item['ocid'],
            'vm_ip': item['ip'],
            'vm_status': item['status'],
            'vm_complete': item['complete'],
            'vm_failed': item['failed']}

    def add_vm(self):
        App.get_running_app().load_image_options()

    def refresh(self):
        App.get_running_app().reload_account()

"""
Oracle VM Migration
=====

Application to move local images in VMDK or QCOW2 format to OCI VM

"""

from kivy.properties import ListProperty, Clock, ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.label import Label


class VMScreen(Screen):
    data = ListProperty()
    account_title = ObjectProperty()
    account = ObjectProperty()
    title_box = ObjectProperty()
    no_vm_label = None

    # def __init__(self, *args, **kwargs):
    #     super(VMScreen, self).__init__(*args, **kwargs)
    #     Clock.schedule_once(self.prepare, 0)

    def prepare(self, *args):
        print "need to fix prepare"
        # if self.data == []:
        #     self.no_vm_label = Label(text='No VMs Migrated', bold=True, font_size='18dp',color=[0.3,0.3,0.3,1])
        #     self.title_box.add_widget(self.no_vm_label)
        #     self.title_box.height = '154dp'
        # else:
        #     try:
        #         self.title_box.remove_widget(self.no_vm_label)
        #         self.title_box.height = '54dp'
        #     except:
        #         print "no button"

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

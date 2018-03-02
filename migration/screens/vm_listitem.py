"""
Oracle VM Migration
=====

Application to move local images in VMDK or QCOW2 format to OCI VM

"""
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout



__version__ = '0.1'


class VMListItem(BoxLayout):
    vm_index = NumericProperty()
    vm_name = StringProperty()
    vm_ocid = StringProperty()
    vm_ip = StringProperty()
    vm_status = StringProperty()
    vm_complete = BooleanProperty()
    vm_failed = BooleanProperty()
    vm_label = ObjectProperty()
    status_box = ObjectProperty()

    def __init__(self, **kwargs):
        print kwargs
        super(VMListItem, self).__init__(**kwargs)
        if self.vm_complete:
            self.vm_label.color = [0/255.0, 168/255.0, 28/255.0, 1]
            self.status_box.source = "data/status/success.png"
        elif self.vm_failed:
            self.vm_label.color = [0.84, 0, 0.1, 1]
            self.status_box.source = "data/status/failed.png"
        else:
            self.vm_label.color = [0.79, 0.73, 0, 1]
            self.status_box.source = "data/status/pending.png"

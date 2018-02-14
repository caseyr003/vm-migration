"""
Oracle VM Migration
=====

Application to move local images in VMDK or QCOW2 format to OCI VM

"""
import json
import os
from os.path import join

from kivy.properties import NumericProperty, ListProperty, BooleanProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.app import App

from modules.account_data import Account
from modules.loading_popups import LoadingPopup


__version__ = '0.1'


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

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadingPopup()
        self._popup = Popup(title="Oracle Cloud Infrastructure VM Migration", content=content,
                            size_hint=(0.8, 0.4))
        self._popup.open()

    def cancel(self):
        self.clear_input()
        self.parent.transition.direction = 'right'
        self.parent.current = Accounts().name

    def clear_input(self):
        self.display_name_input.text = ''
        self.tenancy_ocid_input.text = ''
        self.user_ocid_input.text = ''
        self.region_input.text = ''
        self.fingerprint_input.text = ''
        self.key_file_path = ''
        self.key_chooser.file_btn.text = 'Choose File'

    def save_account(self):
        self.show_load()

        name = self.display_name_input.text
        tenancy_ocid = self.tenancy_ocid_input.text
        user_ocid = self.user_ocid_input.text
        region = self.region_input.text
        fingerprint = self.fingerprint_input.text
        key_location = self.key_file_path

        if (name == '' or tenancy_ocid == '' or user_ocid == '' or region == ''
            or fingerprint == '' or key_location == None):
            btn = Button(text="Okay", size_hint_y=None, height=40, on_release=lambda btn: self.dismiss_popup())
            self._popup.content.popup_container.add_widget(btn)
            self._popup.content.popup_label.text = "Error: Missing Fields"
            return

        config_file = App.get_running_app().config_file
        data_file = App.get_running_app().data_file

        new_account = Account(name, tenancy_ocid, user_ocid, region, fingerprint, key_location, [])

        if new_account.is_active(config_file):
            new_account.save_account(data_file)
        else:
            btn = Button(text="Okay", size_hint_y=None, height=40, on_release=lambda btn: self.dismiss_popup())
            self._popup.content.popup_container.add_widget(btn)
            self._popup.content.popup_label.text = "Error Connecting to OCI Account"
            return

        App.get_running_app().load_data()
        self.dismiss_popup()
        self.clear_input()
        self.parent.transition.direction = 'right'
        self.parent.current = Accounts().name


class VMListItem(BoxLayout):
    vm_index = NumericProperty()
    vm_name = StringProperty()
    vm_ocid = StringProperty()
    vm_ip = StringProperty()

    def __init__(self, **kwargs):
        print kwargs
        super(VMListItem, self).__init__(**kwargs)


class VMScreen(Screen):
    data = ListProperty()
    account_title = ObjectProperty()
    account = ObjectProperty()

    def args_converter(self, row_index, item):
        return {
            'vm_index': row_index,
            'vm_name': item['name'],
            'vm_ocid': item['ocid'],
            'vm_ip': item['ip']}

    def add_vm(self):
        App.get_running_app().load_image_options()


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
        self.show_load()
        self.selected_compartment = compartment
        config_file = App.get_running_app().config_file
        self.bucket_dropdown.bucket_dropdown.clear_widgets()
        self.bucket_dropdown.bucket_button.text = '-'
        self.bucket_dropdown.bucket_button.disabled = True
        bucket_res = self.account.get_buckets(config_file, compartment.id)
        if bucket_res[1]:
            self.bucket_list = bucket_res[0]
            self.bucket_dropdown.create_bucket_dropdown(self.bucket_list)
            self.dismiss_popup()
        else:
            btn = Button(text="Okay", size_hint_y=None, height=40, on_release=lambda btn: self.dismiss_popup())
            self._popup.content.popup_container.add_widget(btn)
            self._popup.content.popup_label.text = "Compartment is Unavailable"
            self.bucket_dropdown.bucket_button.text = '-'
            self.bucket_dropdown.bucket_button.disabled = True
            self.bucket_dropdown.bucket_dropdown.clear_widgets()
            return

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadingPopup()
        self._popup = Popup(title="Oracle Cloud Infrastructure VM Migration", content=content,
                            size_hint=(0.8, 0.4))
        self._popup.open()

    def get_bucket(self, bucket):
        self.selected_bucket = bucket

    def add_vm(self):
        App.get_running_app().load_vm_options(self.account, self.selected_compartment,
                                              self.selected_bucket, self.image_file_path,
                                              self.custom_image_name.text, self.image_type)


class AddVMScreen(Screen):
    launch_vm_switch = ObjectProperty(None)
    launch_with_vm = BooleanProperty(True)
    selected_availability_domain = ObjectProperty(None)
    selected_vcn = ObjectProperty(None)
    selected_subnet = ObjectProperty(None)
    selected_shape = ObjectProperty(None)
    compartment_dropdown = ObjectProperty(None)
    image_file_path = ObjectProperty(None)
    selected_bucket = ObjectProperty(None)
    selected_compartment = ObjectProperty(None)
    image_name = ObjectProperty(None)
    image_type = StringProperty()
    account = ObjectProperty(None)
    ad_list = ObjectProperty(None)
    vcn_list = ObjectProperty(None)
    subnet_list = ObjectProperty(None)
    shape_list = ObjectProperty(None)
    ad_dropdown = ObjectProperty(None)
    vcn_dropdown = ObjectProperty(None)
    subnet_dropdown = ObjectProperty(None)
    shape_dropdown = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(AddVMScreen, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.prepare, 0)

    def prepare(self, *args):
        self.launch_vm_switch.active = self.launch_with_vm
        self.launch_vm_switch.bind(active=self.callback)

    def callback(self, value, x):
        self.launch_with_vm = x

    def launch(self):
        self.show_load()
        if self.launch_vm_switch.active:
            self.launch_vm()
        else:
            self.launch_image()

    def launch_image(self):
        config_file = App.get_running_app().config_file
        bucket_name = self.selected_bucket.name
        file_name = self.image_name
        file_path = self.image_file_path
        upload = self.account.upload_image(config_file, bucket_name, file_name, file_path)
        if upload[0]:
            namespace = upload[1]
        else:
            print "Error uploading"
            return

        display_name = file_name
        image_type = self.image_type
        compartment_id = self.selected_compartment.id
        image = self.account.create_image(config_file, namespace, bucket_name, file_name,
                                          display_name, image_type, compartment_id)
        if image[0]:
            print "Custom Image import complete"
            image_id = image[1]
        else:
            print "Error creating image"
            return

        data_file = App.get_running_app().data_file
        index = App.get_running_app().current_index
        self.account.add_vm(data_file, index, file_name, image_id, "n/a")
        self.dismiss_load()
        App.get_running_app().reload_account(index)

    def launch_vm(self):
        config_file = App.get_running_app().config_file
        bucket_name = self.selected_bucket.name
        file_name = self.image_name
        file_path = self.image_file_path
        upload = self.account.upload_image(config_file, bucket_name, file_name, file_path)
        if upload[0]:
            namespace = upload[1]
        else:
            print "Error uploading"
            return

        display_name = file_name
        image_type = self.image_type
        compartment_id = self.selected_compartment.id
        image = self.account.create_image(config_file, namespace, bucket_name, file_name,
                                          display_name, image_type, compartment_id)
        if image[0]:
            image_id = image[1]
        else:
            print "Error creating image"
            return


        ad_name = self.selected_availability_domain.name
        shape = self.selected_shape.name
        subnet_id = self.selected_subnet.id
        vm = self.account.provision_vm(config_file, subnet_id, ad_name, compartment_id,
                                       display_name, image_id, shape)
        if vm[0]:
            instance_id = vm[1]
            instance_ip = vm[2]
        else:
            print "Error provisioning vm"
            return
        data_file = App.get_running_app().data_file
        index = App.get_running_app().current_index

        self.account.add_vm(data_file, index, display_name, instance_id, instance_ip)
        self.dismiss_load()
        App.get_running_app().reload_account(index)

    def get_availability_domain(self, ad):
        self.selected_availability_domain = ad

    def get_vcn(self, vcn):
        self.selected_vcn = vcn
        config_file = App.get_running_app().config_file
        self.subnet_dropdown.subnet_dropdown.clear_widgets()
        self.subnet_dropdown.subnet_button.text = '-'
        self.subnet_dropdown.subnet_button.disabled = True
        self.subnet_list = self.account.get_subnets(config_file, self.selected_compartment.id, vcn.id)
        self.subnet_dropdown.create_subnet_dropdown(self.subnet_list)

    def get_subnet(self, subnet):
        self.selected_subnet = subnet

    def get_shape(self, shape):
        self.selected_shape = shape

    def image_complete(self):
        App.get_running_app().cancel_vm()

    def dismiss_load(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadingPopup()
        self._popup = Popup(title="Oracle Cloud Infrastructure VM Migration", content=content,
                            size_hint=(0.8, 0.4))
        self._popup.open()


class ScreenManagement(ScreenManager):
    pass


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


class MigrationApp(App):
    def build(self):
        self.title = 'Oracle VM Migration'
        self.current_index = 0
        self.transition = SlideTransition(duration=.35)
        self.accounts = Accounts()
        self.account = VMScreen()
        self.image_screen = AddImageScreen()
        self.vm_screen = AddVMScreen()
        self.add_account_screen = AddAccountScreen()
        root = ScreenManager(transition=self.transition)
        root.add_widget(self.accounts)
        root.add_widget(self.add_account_screen)
        root.add_widget(self.account)
        root.add_widget(self.image_screen)
        root.add_widget(self.vm_screen)
        self.load_data()
        return root

    def load_data(self):
        #todo: make data file
        if os.stat(self.data_file).st_size == 0:
            return

        with open(self.data_file) as data_file:
            data = json.load(data_file)
            account_list = []
            for index, x in enumerate(data["accounts"]):
                account = Account(x["name"], x["tenancy_ocid"], x["user_ocid"], x["region"],
                                  x["fingerprint"], x["key_location"], x["vms"])
                account_list.append(account)
            self.accounts.data = account_list

    def load_account(self, index):
        self.account.account = self.accounts.data[index]
        self.current_index = index
        if self.account.account.is_active(self.config_file):
            self.account.account_title.text = self.accounts.data[index].name
            self.account.data = self.accounts.data[index].vm_list
            self.transition.direction = 'left'
            self.root.current = self.account.name
        else:
            print "Account Error"
            return

    def reload_account(self, index):
        self.load_data()
        self.account.account = self.accounts.data[index]
        self.current_index = index
        if self.account.account.is_active(self.config_file):
            self.account.account_title.text = self.accounts.data[index].name
            self.account.data = self.accounts.data[index].vm_list
            self.transition.direction = 'right'
            self.root.current = self.account.name
        else:
            print "Account Error"
            return

    def load_image_options(self):
        self.image_screen.account = self.account.account
        self.image_screen.compartment_list = self.image_screen.account.get_compartments(self.config_file)
        self.image_screen.compartment_dropdown.create_compartment_dropdown(self.image_screen.compartment_list)
        self.transition.direction = 'left'
        self.root.current = self.image_screen.name

    def load_vm_options(self, account, compartment, bucket, image_file_path, image_name, image_type):
        self.vm_screen.account = account
        self.vm_screen.selected_compartment = compartment
        self.vm_screen.selected_bucket = bucket
        self.vm_screen.image_file_path = image_file_path
        self.vm_screen.image_type = image_type
        self.vm_screen.image_name = image_name
        self.vm_screen.ad_list = self.vm_screen.account.get_availability_domains(self.config_file, compartment.id)
        self.vm_screen.ad_dropdown.create_availability_domain_dropdown(self.vm_screen.ad_list)
        self.vm_screen.vcn_list = self.vm_screen.account.get_vcns(self.config_file, compartment.id)
        self.vm_screen.vcn_dropdown.create_vcn_dropdown(self.vm_screen.vcn_list)
        self.vm_screen.shape_list = self.vm_screen.account.get_shapes(self.config_file, compartment.id)
        self.vm_screen.shape_dropdown.create_shape_dropdown(self.vm_screen.shape_list)
        self.root.current = self.vm_screen.name

    def view_accounts(self):
        view = Accounts()
        self.transition.direction = 'right'
        self.root.current = view.name

    def cancel_image(self):
        self.clear_compartment_dropdown()
        self.clear_bucket_dropdown()
        self.clear_image_chooser()
        self.transition.direction = 'right'
        self.root.current = self.account.name

    def back_vm(self):
        self.clear_ad_dropdown()
        self.clear_shape_dropdown()
        self.clear_vcn_dropdown()
        self.clear_subnet_dropdown()
        self.transition.direction = 'right'
        self.root.current = self.image_screen.name

    def cancel_vm(self):
        self.clear_vm_options()
        view = VMScreen()
        self.transition.direction = 'right'
        self.root.current = view.name

    def clear_vm_options(self):
        self.clear_compartment_dropdown()
        self.clear_bucket_dropdown()
        self.clear_ad_dropdown()
        self.clear_shape_dropdown()
        self.clear_vcn_dropdown()
        self.clear_subnet_dropdown()
        self.clear_image_chooser()

    def clear_image_chooser(self):
        self.image_screen.image_chooser.file_btn.text = 'Choose File'

    def clear_compartment_dropdown(self):
        self.image_screen.compartment_dropdown.compartment_dropdown.clear_widgets()
        self.image_screen.compartment_dropdown.compartment_button.text = '-'
        self.image_screen.compartment_dropdown.compartment_button.disabled = True

    def clear_bucket_dropdown(self):
        self.image_screen.bucket_dropdown.bucket_dropdown.clear_widgets()
        self.image_screen.bucket_dropdown.bucket_button.text = '-'
        self.image_screen.bucket_dropdown.bucket_button.disabled = True

    def clear_ad_dropdown(self):
        self.vm_screen.ad_dropdown.availability_domain_dropdown.clear_widgets()
        self.vm_screen.ad_dropdown.availability_domain_button.text = '-'
        self.vm_screen.ad_dropdown.availability_domain_button.disabled = True

    def clear_shape_dropdown(self):
        self.vm_screen.shape_dropdown.shape_dropdown.clear_widgets()
        self.vm_screen.shape_dropdown.shape_button.text = '-'
        self.vm_screen.shape_dropdown.shape_button.disabled = True

    def clear_vcn_dropdown(self):
        self.vm_screen.vcn_dropdown.vcn_dropdown.clear_widgets()
        self.vm_screen.vcn_dropdown.vcn_button.text = '-'
        self.vm_screen.vcn_dropdown.vcn_button.disabled = True

    def clear_subnet_dropdown(self):
        self.vm_screen.subnet_dropdown.subnet_dropdown.clear_widgets()
        self.vm_screen.subnet_dropdown.subnet_button.text = '-'
        self.vm_screen.subnet_dropdown.subnet_button.disabled = True

    def add_account(self):
        self.transition.direction = 'left'
        self.root.current = self.add_account_screen.name

    def add_image(self):
        view = AddImageScreen()
        self.transition.direction = 'left'
        self.root.current = view.name

    def clear_input(self):
        print 'input cleared'

    @property
    def data_file(self):
        return join(self.user_data_dir, 'data.json')

    @property
    def config_file(self):
        return join(self.user_data_dir, 'config')


if __name__ == '__main__':
    MigrationApp().run()

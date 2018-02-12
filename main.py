'''
Oracle VM Migration
=====

Application to move local images in VMDK or QCOW2 format to OCI VM

'''

__version__ = '0.1'


import json
import os
from os.path import join, exists
import kivy
kivy.require("1.10.0")
from kivy.core.window import Window
from kivy.config import Config
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import *
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.properties import ListProperty, StringProperty, \
        NumericProperty, BooleanProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
import oci
import time
from functools import partial
import threading
from oci.object_storage.transfer.constants import MEBIBYTE
from modules import *


class AccountScreen(Screen):
    data = ListProperty()

    def args_converter(self, row_index, item):
        return {
            'account_index': row_index,
            'account_name': item['name'],
            'account_tenancy': item['tenancy'],
            'account_user': item['user'],
            'account_region': item['region'],
            'account_fingerprint': item['fingerprint'],
            'account_key': item['key']}

class AccountItem(BoxLayout):
    def __init__(self, **kwargs):
        print(kwargs)
        del kwargs['index']
        super(AccountItem, self).__init__(**kwargs)
    name = StringProperty()
    tenancy = StringProperty()
    user = StringProperty()
    region = StringProperty()
    fingerprint = StringProperty()
    key = StringProperty()


class AddAccountScreen(Screen):
    display_name_input = ObjectProperty(None)
    tenancy_ocid_input = ObjectProperty(None)
    user_ocid_input = ObjectProperty(None)
    region_input = ObjectProperty(None)
    fingerprint_input = ObjectProperty(None)
    key_file_path = ObjectProperty(None)

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
        self.parent.current = Accounts().name

    def clear_input(self):
        self.display_name_input.text = ''
        self.tenancy_ocid_input.text = ''
        self.user_ocid_input.text = ''
        self.region_input.text = ''
        self.fingerprint_input.text = ''
        self.key_file_path = ''

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
        self.parent.current = Accounts().name

class VMListItem(BoxLayout):

    def __init__(self, **kwargs):
        print(kwargs)
        del kwargs['index']
        super(VMListItem, self).__init__(**kwargs)

    vm_index = NumericProperty()
    vm_name = StringProperty()
    vm_ocid = StringProperty()

class VMScreen(Screen):
    data = ListProperty()
    account_title = ObjectProperty()
    account = ObjectProperty()

    def args_converter(self, row_index, item):
        return {
            'vm_index': row_index,
            'vm_name': item['name'],
            'vm_ocid': item['vm_ocid']}

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
        App.get_running_app().load_vm_options(self.account, self.selected_compartment, self.selected_bucket, self.image_file_path, self.custom_image_name.text, self.image_type)

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
        if self.launch_vm_switch.active:
            self.popup_thread()
        else:
            self.launch_image()

    def launch_image(self):
        content = LoadingPopup()
        self._popup = Popup(title="Oracle Cloud Infrastructure VM Migration", content=content,
                            size_hint=(0.8, 0.4))

        self._popup.content.popup_label.text = "Step 1/2: Uploading Image to Object Storage"
        self._popup.open()
        config_file = App.get_running_app().config_file
        config = oci.config.from_file(file_location=config_file)

        identity_store = oci.identity.identity_client.IdentityClient(config)
        compute_store = oci.core.compute_client.ComputeClient(config)
        obj_store = oci.object_storage.ObjectStorageClient(config)

        namespace = obj_store.get_namespace().data
        bucket_selected = self.selected_bucket.name
        file_name = self.image_name
        region = self.account.region
        file_path = self.image_file_path
        source_image_type = self.image_type
        display_name = self.image_name
        compartment_selected = self.selected_compartment.id
        launch_mode="EMULATED"

        part_size = 1000 * MEBIBYTE
        upload_man = oci.object_storage.UploadManager(obj_store, allow_parallel_uploads=True, parallel_process_count=3)
        print 'Starting upload to OCI object storage...'
        print 'Uploading... 0%%'
        upload_res = upload_man.upload_file(namespace, bucket_selected, file_name, file_path, part_size=part_size, progress_callback=self.progress_callback)
        self._popup.content.popup_label.text = "Image Successfully uploaded to Object Storage"

        source_uri="https://objectstorage.%s.oraclecloud.com/n/%s/b/%s/o/%s" % (region, namespace, bucket_selected, file_name)


        print 'Starting image import from object storage...'
        image_source_details = oci.core.models.ImageSourceViaObjectStorageUriDetails(source_image_type=source_image_type, source_type="objectStorageUri", source_uri=source_uri)
        create_image_details = oci.core.models.CreateImageDetails(compartment_id=compartment_selected, display_name=display_name, image_source_details=image_source_details, launch_mode=launch_mode)
        create_image_res = compute_store.create_image(create_image_details=create_image_details)
        image_id=create_image_res.data.id

        image_status = compute_store.get_image(image_id=image_id).data.lifecycle_state
        self._popup.content.popup_label.text = "Step 2/2: Importing Image from Object Storage"
        while image_status != "AVAILABLE":
            if image_status != "IMPORTING":
                btn = Button(text="Okay", size_hint_y=None, height=40, on_release=lambda btn: self.dismiss_popup())
                self._popup.content.popup_container.add_widget(btn)
                self._popup.content.popup_label.text = "Image Import was not successful"
                return
                exit()
            time.sleep(20)
            image_status = compute_store.get_image(image_id=image_id).data.lifecycle_state

        btn = Button(text="Okay", size_hint_y=None, height=40, on_release=lambda btn: self.image_complete())
        self._popup.content.popup_container.add_widget(btn)
        self._popup.content.popup_label.text = "Custom Image Successfully Created"

    def progress_callback(self, bytes_uploaded):
        print "uploading"

    def launch_vm(self):
        # self._popup.content.popup_label.text = "Step 1/3: Uploading Image to Object Storage"

        config_file = App.get_running_app().config_file
        config = oci.config.from_file(file_location=config_file)

        identity_store = oci.identity.identity_client.IdentityClient(config)
        compute_store = oci.core.compute_client.ComputeClient(config)
        obj_store = oci.object_storage.ObjectStorageClient(config)

        namespace = obj_store.get_namespace().data
        bucket_selected = self.selected_bucket.name
        file_name = self.image_name
        region = self.account.region
        file_path = self.image_file_path
        source_image_type = self.image_type
        display_name = self.image_name
        compartment_selected = self.selected_compartment.id
        launch_mode="EMULATED"

        ad_selected = self.selected_availability_domain.name
        shape_selected = self.selected_shape.name
        subnet_selected = self.selected_subnet.id

        part_size = 1000 * MEBIBYTE
        upload_man = oci.object_storage.UploadManager(obj_store, allow_parallel_uploads=True, parallel_process_count=3)
        upload_res = upload_man.upload_file(namespace, bucket_selected, file_name, file_path, part_size=part_size, progress_callback=self.progress_callback)
        # self._popup.content.popup_label.text = "Image Successfully uploaded to Object Storage"

        source_uri="https://objectstorage.%s.oraclecloud.com/n/%s/b/%s/o/%s" % (region, namespace, bucket_selected, file_name)

        image_source_details = oci.core.models.ImageSourceViaObjectStorageUriDetails(source_image_type=source_image_type, source_type="objectStorageUri", source_uri=source_uri)
        create_image_details = oci.core.models.CreateImageDetails(compartment_id=compartment_selected, display_name=display_name, image_source_details=image_source_details, launch_mode=launch_mode)
        create_image_res = compute_store.create_image(create_image_details=create_image_details)
        image_id=create_image_res.data.id

        image_status = compute_store.get_image(image_id=image_id).data.lifecycle_state
        # self._popup.content.popup_label.text = "Step 2/3: Importing Image from Object Storage"
        while image_status != "AVAILABLE":
            if image_status != "IMPORTING":
                btn = Button(text="Okay", size_hint_y=None, height=40, on_release=lambda btn: self.dismiss_popup())
                self._popup.content.popup_container.add_widget(btn)
                self._popup.content.popup_label.text = "Image Import was not successful"
                return
                exit()
            time.sleep(20)
            image_status = compute_store.get_image(image_id=image_id).data.lifecycle_state

        # self._popup.content.popup_label.text = "Step 3/3: Provisioning VM from Custom Image"

        create_vnic_details = oci.core.models.CreateVnicDetails(subnet_id=subnet_selected)

        launch_instance_details = oci.core.models.LaunchInstanceDetails(availability_domain=ad_selected, compartment_id=compartment_selected, create_vnic_details=create_vnic_details, display_name=display_name, image_id=image_id, shape=shape_selected)

        create_vm_res = compute_store.launch_instance(launch_instance_details=launch_instance_details)
        instance_id = create_vm_res.data.id
        instance_status = compute_store.get_instance(instance_id=instance_id).data.lifecycle_state
        print 'Provisioning instance...'
        while instance_status != "RUNNING":
            if instance_status != "PROVISIONING":
                print 'An error occured while provisioning the server'
                exit()
            time.sleep(20)
            instance_status = compute_store.get_instance(instance_id=instance_id).data.lifecycle_state
            print 'Provisioning instance... \r'

        vnic = compute_store.list_vnic_attachments(compartment_id=compartment_selected, instance_id=instance_id)
        vnic_id = res.data[0].vnic_id

        vcn_store = oci.core.virtual_network_client.VirtualNetworkClient(conf)

        vnic_instance = vcn.get_vnic(vnic_id=vnic_id)

        instance_ip = vnic_instance.data.public_ip

        print 'Instance successfully created'
        print 'Your image is now running in Oracle Cloud Infrastructure'
        print 'Public IP: %s' % instance_ip

        btn = Button(text="Okay", size_hint_y=None, height=40, on_release=lambda btn: self.dismiss_popup())
        self._popup.content.popup_container.add_widget(btn)
        self._popup.content.popup_label.text = "Virtual Machine Successfully Created from Image"

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
        self.dismiss_popup
        #Add VM to list
        App.get_running_app().cancel_vm()


    def dismiss_popup(self):
        self._popup.dismiss()

    def popup_thread(self):
        content = LoadingPopup()
        self._popup = Popup(title="Oracle Cloud Infrastructure VM Migration", content=content,
                            size_hint=(0.8, 0.4))
        self._popup.content.popup_label.text = "Loading..."
        self._popup.open()
        mythread = threading.Thread(target=self.launch_vm())
        mythread.start()

    def show_load(self):
        content = LoadingPopup()
        self._popup = Popup(title="Oracle Cloud Infrastructure VM Migration", content=content,
                            size_hint=(0.8, 0.4))
        self._popup.open()

class ScreenManagement(ScreenManager):
    pass

class AccountListItem(BoxLayout):

    def __init__(self, **kwargs):
        del kwargs['index']
        super(AccountListItem, self).__init__(**kwargs)

    account_index = NumericProperty()
    account_name = StringProperty()
    account_tenancy = StringProperty()
    account_user = StringProperty()
    account_region = StringProperty()
    account_fingerprint = StringProperty()
    account_key = StringProperty()

    def account_details(self):
        App.get_running_app().load_account(self.account_index)

class Accounts(Screen):

    data = ListProperty()

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
        if os.stat(self.data_file).st_size == 0:
            return

        with open(self.data_file) as data_file:
            data = json.load(data_file)
            account_list = []
            for index, x in enumerate(data["accounts"]):
                account = Account(x["name"], x["tenancy_ocid"], x["user_ocid"], x["region"], x["fingerprint"], x["key_location"], x["vms"])
                account_list.append(account)
            self.accounts.data = account_list

    def load_account(self, index):
        self.account.account = self.accounts.data[index]
        if self.account.account.is_active(self.config_file):
            self.account.account_title.text = self.accounts.data[index].name
            self.account.data = self.accounts.data[index].vm_list
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
        self.clear_compartment_dropdown()
        self.clear_bucket_dropdown()
        self.clear_ad_dropdown()
        self.clear_shape_dropdown()
        self.clear_vcn_dropdown()
        self.clear_subnet_dropdown()
        view = VMScreen()
        self.transition.direction = 'right'
        self.root.current = view.name

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

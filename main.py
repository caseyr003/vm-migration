"""
Oracle VM Migration
=====

Application to move local images in VMDK or QCOW2 format to OCI VM

"""
import json
import os
from os.path import join
from threading import Thread

from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.app import App

from migration.account import *
from migration.dropdowns import *
from migration.popups import *
from migration.screens import *


__version__ = '0.1'


class ScreenManagement(ScreenManager):
    pass


class MigrationApp(App):
    def build(self):
        self.title = 'VM Migration Tool'
        self.current_index = 0
        self.transition = SlideTransition(duration=.35)
        self.accounts = Accounts()
        self.account = VMScreen()
        self.image_screen = AddImageScreen()
        self.vm_screen = AddVMScreen()
        self.add_account_screen = AddAccountScreen()
        self.help_screen = HelpScreen()
        root = ScreenManager(transition=self.transition)
        root.add_widget(self.accounts)
        root.add_widget(self.add_account_screen)
        root.add_widget(self.account)
        root.add_widget(self.image_screen)
        root.add_widget(self.vm_screen)
        root.add_widget(self.help_screen)
        self.load_data()
        return root

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadingPopup()
        self._popup = Popup(title="Virtual Machine Migration Tool", content=content,
                            size_hint=(0.8, 0.4), auto_dismiss=False)
        self._popup.open()

    def show_error(self, error):
        btn = Button(text="Okay", size_hint=[1, 0.25], height=40, on_release=lambda btn: self.dismiss_popup())
        self._popup.content.popup_container.add_widget(btn)
        self._popup.content.popup_label.text = error

    def check_file(self):
        file_exists = True
        try:
            file_exists = os.stat(self.data_file).st_size != 0
        except Exception:
            check = open(join(self.user_data_dir, 'data.json'), 'w')
            check.close()
            return not file_exists
        return file_exists

    def load_data(self):
        if self.check_file():
            with open(self.data_file) as data_file:
                data = json.load(data_file)
                account_list = []
                for index, x in enumerate(data["accounts"]):
                    account = Account(x["name"], x["tenancy_ocid"], x["user_ocid"], x["region"],
                                      x["fingerprint"], x["key_location"], x["vms"])
                    account_list.append(account)
                self.accounts.data = account_list

    def get_account(self):
        index = self.current_index
        self.account.account = self.accounts.data[index]
        if self.account.account.is_active(self.config_file):
            self.account.account_title.text = self.accounts.data[index].name
            self.account.data = self.accounts.data[index].vm_list
            self.dismiss_popup()
            self.transition.direction = 'left'
            self.root.current = self.account.name
            self.account.prepare()
        else:
            self.show_error("Error Loading Account")

    def account_added(self):
        self.accounts.prepare()
        self.transition.direction = 'right'
        self.root.current = self.accounts.name

    def load_account(self, index):
        self.show_load()
        self.current_index = index
        Thread(target=self.get_account).start()

    def reload_account(self):
        index = self.current_index
        self.load_data()
        self.account.account = self.accounts.data[index]
        if self.account.account.is_active(self.config_file):
            self.account.account_title.text = self.accounts.data[index].name
            self.account.data = self.accounts.data[index].vm_list
            self.transition.direction = 'right'
            self.root.current = self.account.name
        else:
            print "Account Error"
            return

    def prepare_vm_screen(self):
        self.account.prepare()

    def load_image_options(self):
        self.image_screen.account = self.account.account
        self.image_screen.compartment_list = self.image_screen.account.get_compartments(self.config_file)
        self.image_screen.compartment_dropdown.create_compartment_dropdown(self.image_screen.compartment_list)
        self.transition.direction = 'left'
        self.root.current = self.image_screen.name

    def load_vm_options(self, account, compartment, bucket, image_file_path, image_name, image_type):
        self.show_load()

        if (account == None or compartment == None or bucket == None or image_file_path == '' or
           image_type == '' or image_name == ''):
            self.show_error("Error: Missing Fields")
            return

        self.vm_screen.account = account
        self.vm_screen.selected_compartment = compartment
        self.vm_screen.selected_bucket = bucket
        self.vm_screen.image_file_path = image_file_path
        self.vm_screen.image_type = image_type
        self.vm_screen.image_name = image_name

        Thread(target=self.get_vm_options).start()

    def get_vm_options(self):
        compartment = self.vm_screen.selected_compartment
        self.vm_screen.ad_list = self.vm_screen.account.get_availability_domains(self.config_file, compartment.id)
        self.vm_screen.ad_dropdown.create_availability_domain_dropdown(self.vm_screen.ad_list)
        self.vm_screen.vcn_list = self.vm_screen.account.get_vcns(self.config_file, compartment.id)
        self.vm_screen.vcn_dropdown.create_vcn_dropdown(self.vm_screen.vcn_list)
        self.vm_screen.shape_list = self.vm_screen.account.get_shapes(self.config_file, compartment.id)
        self.vm_screen.shape_dropdown.create_shape_dropdown(self.vm_screen.shape_list)
        self.dismiss_popup()
        self.transition.direction = 'left'
        self.root.current = self.vm_screen.name

    def view_accounts(self):
        self.transition.direction = 'right'
        self.root.current = self.accounts.name

    def get_help(self):
        self.transition.direction = 'left'
        self.root.current = self.help_screen.name

    def cancel_image(self):
        self.clear_compartment_dropdown()
        self.clear_bucket_dropdown()
        self.clear_image_chooser()
        self.image_screen.custom_image_name.text = ''
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
        self.transition.direction = 'right'
        self.root.current = self.accounts.name

    def clear_vm_options(self):
        self.clear_compartment_dropdown()
        self.clear_bucket_dropdown()
        self.clear_ad_dropdown()
        self.clear_shape_dropdown()
        self.clear_vcn_dropdown()
        self.clear_subnet_dropdown()
        self.clear_image_chooser()
        self.image_screen.custom_image_name.text = ''

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
        self.transition.direction = 'left'
        self.root.current = self.image_screen.name

    @property
    def data_file(self):
        return join(self.user_data_dir, 'data.json')

    @property
    def config_file(self):
        return join(self.user_data_dir, 'config')


if __name__ == '__main__':
    MigrationApp().run()

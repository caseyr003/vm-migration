from threading import Thread

from kivy.properties import BooleanProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.app import App


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
        App.get_running_app().show_load()
        can_launch_image = not (self.selected_compartment == None or self.selected_bucket == None or
                                self.image_name == '' or self.image_file_path == '' or self.image_type == '')
        can_launch_vm = not (self.selected_availability_domain == None or self.selected_subnet == None or
                             self.selected_shape == None or self.selected_vcn == None)

        if (self.launch_vm_switch.active and can_launch_image and can_launch_vm):
            Thread(target=self.launch_vm).start()
        elif ((not self.launch_vm_switch.active) and can_launch_image):
            Thread(target=self.launch_image).start()
        else:
            App.get_running_app().dismiss_popup()
            App.get_running_app().show_load()
            App.get_running_app().show_error("Error: Missing Fields")
            return

        App.get_running_app().dismiss_popup()
        App.get_running_app().reload_account()


    def launch_image(self):
        config_file = App.get_running_app().config_file
        bucket_name = self.selected_bucket.name
        file_name = self.image_name
        file_path = self.image_file_path
        display_name = file_name
        image_type = self.image_type
        compartment_id = self.selected_compartment.id
        data_file = App.get_running_app().data_file
        index = App.get_running_app().current_index

        vm_index = self.account.add_vm(data_file, index, file_name, "", "", "Uploading")

        upload = self.account.upload_image(config_file, bucket_name, file_name, file_path)
        if upload[0]:
            namespace = upload[1]
            self.account.update_vm_status(data_file, index, "Importing", False, False, vm_index)
        else:
            print "Error uploading"
            self.account.update_vm_status(data_file, index, "Failed on Upload", False, True, vm_index)
            App.get_running_app().show_load()
            App.get_running_app().show_error("Error Uploading")
            return

        image = self.account.create_image(config_file, namespace, bucket_name, file_name,
                                          display_name, image_type, compartment_id)
        if image[0]:
            print "Custom Image import complete"
            image_id = image[1]
        else:
            print "Error creating image"
            self.account.update_vm_status(data_file, index, "Failed Creating Custom Image", False, True, vm_index)
            App.get_running_app().show_load()
            App.get_running_app().show_error("Error Creating Custom Image")
            return

        self.account.update_vm(data_file, index, "", "", "Custom Image Imported", True, False, vm_index)

    def launch_vm(self):
        config_file = App.get_running_app().config_file
        bucket_name = self.selected_bucket.name
        file_name = self.image_name
        file_path = self.image_file_path
        display_name = file_name
        image_type = self.image_type
        compartment_id = self.selected_compartment.id
        ad_name = self.selected_availability_domain.name
        shape = self.selected_shape.name
        subnet_id = self.selected_subnet.id
        data_file = App.get_running_app().data_file
        index = App.get_running_app().current_index

        vm_index = self.account.add_vm(data_file, index, file_name, "", "", "Uploading")

        upload = self.account.upload_image(config_file, bucket_name, file_name, file_path)
        if upload[0]:
            namespace = upload[1]
            self.account.update_vm_status(data_file, index, "Importing", False, False, vm_index)
        else:
            print "Error uploading"
            self.account.update_vm_status(data_file, index, "Failed on Upload", False, True, vm_index)
            App.get_running_app().show_load()
            App.get_running_app().show_error("Error Uploading")
            return

        image = self.account.create_image(config_file, namespace, bucket_name, file_name,
                                          display_name, image_type, compartment_id)
        if image[0]:
            image_id = image[1]
            self.account.update_vm_status(data_file, index, "Provisioning", False, False, vm_index)
        else:
            print "Error creating image"
            self.account.update_vm_status(data_file, index, "Failed Creating Custom Image", False, True, vm_index)
            App.get_running_app().show_error("Error Creating Custom Image")
            return

        vm = self.account.provision_vm(config_file, subnet_id, ad_name, compartment_id,
                                       display_name, image_id, shape)
        if vm[0]:
            instance_id = vm[1]
            instance_ip = vm[2]
        else:
            print "Error provisioning vm"
            self.account.update_vm_status(data_file, index, "Failed Provisioning Virtual Machine", False, True, vm_index)
            App.get_running_app().show_load()
            App.get_running_app().show_error("Error Provisioning VM")
            return

        self.account.add_vm(data_file, index, display_name, instance_id, instance_ip)
        self.account.update_vm(data_file, index, instance_id, instance_ip, "Running", True, False, vm_index)

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

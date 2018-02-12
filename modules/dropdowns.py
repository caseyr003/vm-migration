from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.properties import ListProperty, StringProperty, \
        NumericProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from account_data import *

class BucketDropdown(BoxLayout):
        bucket_box = ObjectProperty(None)
        bucket_dropdown = DropDown()
        bucket_button = ObjectProperty()

        def __init__(self, *args, **kwargs):
            super(BucketDropdown, self).__init__(*args, **kwargs)
            self.bucket_dropdown = DropDown()

        def create_bucket_dropdown(self, buckets):
            for index, bucket in enumerate(buckets):
                btn = bucket.add_btn(self.bucket_dropdown)
                self.bucket_dropdown.add_widget(btn)
            self.bucket_button.bind(on_release=self.bucket_dropdown.open)
            self.bucket_dropdown.bind(on_select=lambda instance, x: setattr(self.bucket_button, 'text', x.name))
            self.bucket_dropdown.bind(on_select=lambda instance, x: self.parent.parent.parent.get_bucket(x))
            self.bucket_button.disabled = False


class CompartmentDropdown(BoxLayout):
        compartment_box = ObjectProperty(None)
        compartment_dropdown = DropDown()
        compartment_button = ObjectProperty()

        def __init__(self, *args, **kwargs):
            super(CompartmentDropdown, self).__init__(*args, **kwargs)
            self.compartment_dropdown = DropDown()

        def create_compartment_dropdown(self, compartments):
            # self.parent.parent.parent.show_load()
            for index, compartment in enumerate(compartments):
                btn = compartment.add_btn(self.compartment_dropdown)
                self.compartment_dropdown.add_widget(btn)
            self.compartment_button.bind(on_release=self.compartment_dropdown.open)
            self.compartment_dropdown.bind(on_select=lambda instance, x: setattr(self.compartment_button, 'text', x.name))
            self.compartment_dropdown.bind(on_select=lambda instance, x: self.parent.parent.parent.get_compartment(x))
            self.compartment_button.disabled = False
            # self.parent.parent.parent.dismiss_popup()

class AvailabilityDomainDropdown(BoxLayout):
        availability_domain_box = ObjectProperty(None)
        availability_domain_dropdown = DropDown()
        availability_domain_button = ObjectProperty()

        def __init__(self, *args, **kwargs):
            super(AvailabilityDomainDropdown, self).__init__(*args, **kwargs)
            self.availability_domain_dropdown = DropDown()

        def create_availability_domain_dropdown(self, availability_domains):
            for index, availability_domain in enumerate(availability_domains):
                btn = availability_domain.add_btn(self.availability_domain_dropdown)
                self.availability_domain_dropdown.add_widget(btn)
            self.availability_domain_button.bind(on_release=self.availability_domain_dropdown.open)
            self.availability_domain_dropdown.bind(on_select=lambda instance, x: setattr(self.availability_domain_button, 'text', x.name))
            self.availability_domain_dropdown.bind(on_select=lambda instance, x: self.parent.parent.parent.get_availability_domain(x))
            self.availability_domain_button.disabled = False

class VirtualCloudNetworkDropdown(BoxLayout):
        vcn_box = ObjectProperty(None)
        vcn_dropdown = DropDown()
        vcn_button = ObjectProperty()

        def __init__(self, *args, **kwargs):
            super(VirtualCloudNetworkDropdown, self).__init__(*args, **kwargs)
            self.vcn_dropdown = DropDown()

        def create_vcn_dropdown(self, vcns):
            for index, vcn in enumerate(vcns):
                btn = vcn.add_btn(self.vcn_dropdown)
                self.vcn_dropdown.add_widget(btn)
            self.vcn_button.bind(on_release=self.vcn_dropdown.open)
            self.vcn_dropdown.bind(on_select=lambda instance, x: setattr(self.vcn_button, 'text', x.name))
            self.vcn_dropdown.bind(on_select=lambda instance, x: self.parent.parent.parent.get_vcn(x))
            self.vcn_button.disabled = False

class SubnetDropdown(BoxLayout):
        subnet_box = ObjectProperty(None)
        subnet_dropdown = DropDown()
        subnet_button = ObjectProperty()

        def __init__(self, *args, **kwargs):
            super(SubnetDropdown, self).__init__(*args, **kwargs)
            self.subnet_dropdown = DropDown()

        def create_subnet_dropdown(self, subnets):
            for index, subnet in enumerate(subnets):
                btn = subnet.add_btn(self.subnet_dropdown)
                self.subnet_dropdown.add_widget(btn)
            self.subnet_button.bind(on_release=self.subnet_dropdown.open)
            self.subnet_dropdown.bind(on_select=lambda instance, x: setattr(self.subnet_button, 'text', x.name))
            self.subnet_dropdown.bind(on_select=lambda instance, x: self.parent.parent.parent.get_subnet(x))
            self.subnet_button.disabled = False

class ShapeDropdown(BoxLayout):
        shape_box = ObjectProperty(None)
        shape_dropdown = DropDown()
        shape_button = ObjectProperty()

        def __init__(self, *args, **kwargs):
            super(ShapeDropdown, self).__init__(*args, **kwargs)
            self.shape_dropdown = DropDown()

        def create_shape_dropdown(self, shapes):
            for index, shape in enumerate(shapes):
                btn = shape.add_btn(self.shape_dropdown)
                self.shape_dropdown.add_widget(btn)
            self.shape_button.bind(on_release=self.shape_dropdown.open)
            self.shape_dropdown.bind(on_select=lambda instance, x: setattr(self.shape_button, 'text', x.name))
            self.shape_dropdown.bind(on_select=lambda instance, x: self.parent.parent.parent.get_shape(x))
            self.shape_button.disabled = False

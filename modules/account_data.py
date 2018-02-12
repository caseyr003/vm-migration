import json
import os
from kivy.uix.button import Button
import oci

class Account:
    def __init__(self, name, tenancy_ocid, user_ocid, region, fingerprint, key_location, vm_list):
        self.name = name
        self.tenancy_ocid = tenancy_ocid
        self.user_ocid = user_ocid
        self.region = region
        self.fingerprint = fingerprint
        self.key_location = key_location
        self.vm_list = vm_list

    def get_json(self):
        return {
            'name': self.name,
            'tenancy_ocid': self.tenancy_ocid,
            'user_ocid': self.user_ocid,
            'region': self.region,
            'fingerprint': self.fingerprint,
            'key_location': self.key_location,
            'vms': self.vm_list
        }

    def save_account(self, data_file):
        if os.stat(data_file).st_size == 0:
            with open(data_file, 'w') as data_file:
                json.dump({"accounts":[self.get_json()]}, data_file, indent=2)
        else:
            with open(data_file, 'r') as read_data:
                data = json.load(read_data)

            data["accounts"].append(self.get_json())

            with open(data_file, 'w') as write_data:
                json.dump(data, write_data, indent=2)

    def config_account(self, config_file):
        config = open(config_file, 'w')
        config.seek(0)
        config.truncate()
        config.write('[DEFAULT]\n')
        config.write('user=%s\n' % self.user_ocid)
        config.write('fingerprint=%s\n' % self.fingerprint)
        config.write('key_file=%s\n' % self.key_location)
        config.write('tenancy=%s\n' % self.tenancy_ocid)
        config.write('region=%s\n' % self.region)
        config.close()


    def is_active(self, config_file):
        self.config_account(config_file)

        success = False
        try:
            config = oci.config.from_file(file_location=config_file)
            identity = oci.identity.IdentityClient(config)
            user = identity.get_user(config["user"])
            success = True
        except:
            print "An Error Occured"

        return success

    def get_compartments(self, config_file):
        config = oci.config.from_file(file_location=config_file)

        #Store compartments in array to return
        compartment_array = []
        # Get identity store for region and compartment
        identity_store = oci.identity.identity_client.IdentityClient(config)
        # Select compartment for compute
        compartment_res = identity_store.list_compartments(compartment_id=self.tenancy_ocid)
        compartment_list = compartment_res.data
        for x in compartment_list:
            compartment = Compartment(x.id, x.name)
            compartment_array.append(compartment)
        return compartment_array

    def get_buckets(self, config_file, compartment_id):
        config = oci.config.from_file(file_location=config_file)
        bucket_array = []
        obj_store = oci.object_storage.ObjectStorageClient(config)
        namespace = obj_store.get_namespace().data
        try:
            bucket_res = obj_store.list_buckets(namespace_name=namespace, compartment_id=compartment_id)
            bucket_list = bucket_res.data
        except:
            print "probably don't have access to compartment"
            return [[], False]

        for x in bucket_list:
            bucket = Bucket(x.name)
            bucket_array.append(bucket)
        return [bucket_array, True]

    def get_availability_domains(self, config_file, compartment_id):
        config = oci.config.from_file(file_location=config_file)

        #Store compartments in array to return
        ad_array = []
        # Get identity store for region and compartment
        identity_store = oci.identity.identity_client.IdentityClient(config)

        # Select availability domain for compute
        ad_list = identity_store.list_availability_domains(compartment_id=compartment_id).data
        for x in ad_list:
            ad = AvailabilityDomain(x.name)
            ad_array.append(ad)
        return ad_array

    def get_vcns(self, config_file, compartment_id):
        config = oci.config.from_file(file_location=config_file)

        #Store compartments in array to return
        vcn_array = []
        # Get identity store for region and compartment
        vnc_store = oci.core.virtual_network_client.VirtualNetworkClient(config)

        # Select availability domain for compute
        vcn_list = vnc_store.list_vcns(compartment_id=compartment_id).data
        for x in vcn_list:
            vcn = VirtualCloudNetwork(x.id, x.display_name)
            vcn_array.append(vcn)
        return vcn_array

    def get_subnets(self, config_file, compartment_id, vcn_id):
        config = oci.config.from_file(file_location=config_file)

        #Store compartments in array to return
        subnet_array = []
        # Get identity store for region and compartment
        vnc_store = oci.core.virtual_network_client.VirtualNetworkClient(config)

        # Select availability domain for compute
        subnet_list = vnc_store.list_subnets(compartment_id=compartment_id, vcn_id=vcn_id).data
        for x in subnet_list:
            subnet = Subnet(x.id, x.display_name)
            subnet_array.append(subnet)
        return subnet_array

    def get_shapes(self, config_file, compartment_id):
        config = oci.config.from_file(file_location=config_file)

        #Store compartments in array to return
        shape_array = []
        # Get identity store for region and compartment
        compute_store = oci.core.compute_client.ComputeClient(config)

        # Select availability domain for compute
        shape_list = compute_store.list_shapes(compartment_id=compartment_id).data
        for x in shape_list:
            shape = Shape(x.shape)
            shape_array.append(shape)
        return shape_array

class Bucket:
    def __init__(self, name):
        self.name = name

    def add_btn(self, dropdown):
        btn = Button(text=str(self.name), size_hint_y=None, height=40, on_release=lambda btn: dropdown.select(self))
        return btn

class Compartment:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def add_btn(self, dropdown):
        btn = Button(text=str(self.name), size_hint_y=None, height=40, on_release=lambda btn: dropdown.select(self))
        return btn

class AvailabilityDomain:
    def __init__(self, name):
        self.name = name

    def add_btn(self, dropdown):
        btn = Button(text=str(self.name), size_hint_y=None, height=40, on_release=lambda btn: dropdown.select(self))
        return btn

class VirtualCloudNetwork:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def add_btn(self, dropdown):
        btn = Button(text=str(self.name), size_hint_y=None, height=40, on_release=lambda btn: dropdown.select(self))
        return btn

class Subnet:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def add_btn(self, dropdown):
        btn = Button(text=str(self.name), size_hint_y=None, height=40, on_release=lambda btn: dropdown.select(self))
        return btn

class Shape:
    def __init__(self, name):
        self.name = name

    def add_btn(self, dropdown):
        btn = Button(text=str(self.name), size_hint_y=None, height=40, on_release=lambda btn: dropdown.select(self))
        return btn

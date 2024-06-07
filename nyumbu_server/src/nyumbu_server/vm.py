import time
import libvirt
import xml.etree.ElementTree as ET

class VM:

    def __init__(self, domain_xml_str: str):
        self.conn = libvirt.open("qemu:///system")
        self.domain_xml = ET.fromstring(domain_xml_str)
        self.vm_name = self.domain_xml.find("name").text
        self.domain_xml_str = domain_xml_str

    def start(self):
        # https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/virtualization_deployment_and_administration_guide/sect-troubleshooting-common_libvirt_errors_and_troubleshooting
        # libvirtd.service

        # start default network if not active
        network_name = "default"
        net = self.conn.networkLookupByName(network_name)
        if not net.isActive():
            net.create()

        # start vm
        try:
            dom = self.conn.lookupByName(self.vm_name)
            print("has old vm")
            if dom.isActive():
                self.stop()
            else:
                dom.create()
            self.dom = dom
        except Exception as e:
            print("no old vm", e)
            print("creating new vm")
            dom = self.conn.defineXML(self.domain_xml_str)
            dom.create()
            self.dom = dom

        # create vm
        print("done, active now")

    def stop(self):
        try:
            dom = self.conn.lookupByName(self.vm_name)
            if dom != None:
                if dom.isActive():
                    dom.shutdown()
                dom.destroy()
                time.sleep(1)
        # self.dom.undefine()
        except Exception as e:
            print(f"no such vm named: {self.vm_name}")
            pass

    def save_snapshot(self, name, description="", override=False):
        if self.get_snapshot_by_name(name) == None:
            pass
        elif override:
            self.delete_snapshot_by_name(name)
        else:
            return

        snapshot_xml = f"""
        <domainsnapshot>
        <name>{name}</name>
        <description>{description}</description>
        </domainsnapshot>
        """
        self.dom.snapshotCreateXML(snapshot_xml, 0)

    def save_snapshot_and_jump(self, name, description="", override=False):
        self.save_snapshot(name, description, override)
        self.jump_to_snapshort(name)

    def jump_to_snapshort(self, name):
        snap = self.get_snapshot_by_name(name)
        if snap == None:
            raise "snap not exist"
        self.dom.revertToSnapshot(snap)

    def get_snapshot_by_name(self, name):
        try:
            snap = self.dom.snapshotLookupByName(name)
            return snap
        except:
            return None

    def delete_snapshot_by_name(self, name):
        try:
            snap = self.dom.snapshotLookupByName(name)
            snap.delete()
        except:
            pass

    def delete_all_snapshot(self):
        for name in self.dom.snapshotListNames():
            snap = self.dom.snapshotLookupByName(name)
            snap.delete()

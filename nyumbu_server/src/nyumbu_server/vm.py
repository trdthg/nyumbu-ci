import time
import libvirt
import xml.etree.ElementTree as ET
from .util import fixup_snapshotname

class VM:

    def __init__(self, domain_xml_str: str):
        def libvirt_callback(userdata, err):
            pass
        libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)

        self.conn = libvirt.open("qemu:///system")
        self.domain_xml = ET.fromstring(domain_xml_str)
        self.vm_name = self.domain_xml.find("name").text
        self.domain_xml_str = domain_xml_str

        self.init_network()

    def init_network(self):
        # start default network if not active
        network_name = "default"
        net = self.conn.networkLookupByName(network_name)
        if not net.isActive():
            net.create()

    def start(self):
        # https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/virtualization_deployment_and_administration_guide/sect-troubleshooting-common_libvirt_errors_and_troubleshooting
        # libvirtd.service

        # start vm
        try:
            dom = self.conn.lookupByName(self.vm_name)

            if dom != None:
                print("先停止")
                if dom.isActive():
                    print("先重启")
                    dom.reboot(0)
                else:
                    print("不用重启")
            else:
                print("首次定义虚拟机")
                dom = self.conn.defineXML(self.domain_xml_str)

            print("启动虚拟机")
            dom.create()
            self.dom = dom
            print("启动成功", self.dom)
        except Exception as e:
            print("启动失败 " ,e)

    def stop(self):
        try:
            dom = self.dom
            if dom != None:
                if dom.isActive():
                    dom.destroy()
        except Exception as e:
            print(f"停止失败", e)
            pass

    def pause(self):
        try:
            dom = self.dom
            if dom != None:
                if dom.isActive():
                    dom.suspend()
        except Exception as e:
            print(f"暂停失败", e)
            pass

    def resume(self):
        try:
            dom = self.dom
            if dom != None:
                if not dom.isActive():
                    dom.resume()
        except Exception as e:
            print(f"恢复失败", e)
            pass

    def save_snapshot(self, name, description="", override=False):
        name = fixup_snapshotname(name)

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
        name = fixup_snapshotname(name)

        self.save_snapshot(name, description, override)
        self.jump_to_snapshort(name)

    def jump_to_snapshort(self, name):
        name = fixup_snapshotname(name)

        snap = self.get_snapshot_by_name(name)
        if snap == None:
            raise "snap not exist"
        self.dom.revertToSnapshot(snap)

    def get_snapshot_by_name(self, name):
        name = fixup_snapshotname(name)

        try:
            snap = self.dom.snapshotLookupByName(name)
            return snap
        except:
            return None

    def delete_snapshot_by_name(self, name):
        name = fixup_snapshotname(name)

        try:
            snap = self.dom.snapshotLookupByName(name)
            snap.delete()
        except:
            pass

    def delete_all_snapshot(self):
        for name in self.dom.snapshotListNames():
            snap = self.dom.snapshotLookupByName(name)
            snap.delete()

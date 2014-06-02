import os
import shutil
import tempfile
import atexit


class TFTPBoot:
    def __init__(self, nodesMACIPPairs, netmask, serverIP, rootPassword):
        self._netmask = netmask
        self._serverIP = serverIP
        self._root = tempfile.mkdtemp(suffix=".tftpboot")
        self._rootPassword = rootPassword
        atexit.register(self._cleanup)
        self._pxelinuxConfigDir = os.path.join(self._root, "pxelinux.cfg")
        self._installPXELinux()
        self._createConfigurations(nodesMACIPPairs)

    def root(self):
        return self._root

    def _cleanup(self):
        shutil.rmtree(self._root, ignore_errors=True)

    def _installPXELinux(self):
        shutil.copy("/usr/share/syslinux/menu.c32", self._root)
        shutil.copy("/usr/share/syslinux/pxelinux.0", self._root)
        shutil.copy("/usr/share/inaugurator/inaugurator.vmlinuz", self._root)
        shutil.copy("/usr/share/inaugurator/inaugurator.initrd.img", self._root)
        os.mkdir(self._pxelinuxConfigDir)

    def _createConfigurations(self, macs):
        for mac, ip in macs:
            basename = '01-' + mac.replace(':', '-')
            path = os.path.join(self._pxelinuxConfigDir, basename)
            contents = self._configureInaugurator(mac, ip)
            with open(path, "w") as f:
                f.write(contents)

    def _configureInaugurator(self, mac, ip):
        return _TEMPLATE % dict(
            macAddress=mac, ipAddress=ip,
            netmask=self._netmask, osmosisServerIP=self._serverIP,
            rootPassword=self._rootPassword)

_TEMPLATE = r"""
#serial support on port0 (COM1) running baud-rate 115200
SERIAL 0 115200
#VGA output parallel to serial disabled
CONSOLE 0

default menu.c32
prompt 0
timeout 1

menu title RackAttack PXE Boot Menu

label Latest
    menu label Latest
    kernel inaugurator.vmlinuz
    initrd inaugurator.initrd.img
    append --inauguratorUseNICWithMAC=%(macAddress)s --inauguratorOsmosisHostname=%(osmosisServerIP)s --inauguratorOsmosisLabel=theLabel --inauguratorIPAddress=%(ipAddress)s --inauguratorNetmask=%(netmask)s --inauguratorChangeRootPassword=%(rootPassword)s
"""

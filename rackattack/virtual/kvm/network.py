from rackattack.virtual.kvm import libvirtsingleton
import logging

NAME = "rackattacknet"


def ipAddressFromVMIndex(index):
    return _IP_ADDRESS_FORMAT % (10 + index)


def primaryMACAddressFromVMIndex(index):
    assert index < (1 << 16)
    return "52:54:00:00:%02X:%02X" % (int(index / 256), index % 256)


def secondMACAddressFromVMIndex(index):
    assert index < (1 << 16)
    return "52:54:00:01:%02X:%02X" % (int(index / 256), index % 256)


def setUp():
    with libvirtsingleton.it().lock():
        libvirt = libvirtsingleton.it().libvirt()
        try:
            libvirt.networkLookupByName(NAME)
            logging.info("Libvirt network is already set up")
        except:
            _create(libvirt)
            logging.info("Libvirt network created")


_BRIDGE_NAME = "rackattacknetbr"
_IP_ADDRESS_FORMAT = "192.168.124.%d"
_GATEWAY_IP_ADDRESS = _IP_ADDRESS_FORMAT % 1
_XML = """
<network>
  <name>%(name)s</name>
  <forward mode='nat'/>
  <bridge name='%(bridgeName)s' stp='on' delay='0' />
  <ip address='%(gatewayIPAddress)s' netmask='255.255.255.0'>
  </ip>
</network>
""" % dict(
    name=NAME, bridgeName=_BRIDGE_NAME,
    gatewayIPAddress=_GATEWAY_IP_ADDRESS)


def _create(libvirt):
    libvirt.networkCreateXML(_XML)

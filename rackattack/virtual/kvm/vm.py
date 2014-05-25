from rackattack.virtual.kvm import manifest
from rackattack.virtual.kvm import libvirtsingleton
from rackattack.virtual.kvm import config
from rackattack.virtual.kvm import imagecommands
from rackattack.virtual.kvm import network
import os


class VM:
    def __init__(self, index, domain, manifest, imageLabel, imageHint):
        self._index = index
        self._domain = domain
        self._manifest = manifest
        self._imageLabel = imageLabel
        self._imageHint = imageHint

    def index(self):
        return self._index

    def id(self):
        return self._manifest.name()

    def primaryMACAddress(self):
        return self._manifest.primaryMACAddress()

    def secondaryMACAddress(self):
        return self._manifest.secondaryMACAddress()

    def ipAddress(self):
        network.ipAddressFromVMIndex(self._index)

    @classmethod
    def create(cls, index, requirement):
        name = cls._nameFromIndex(index)
        image1 = os.path.join(config.DISK_IMAGES_DIRECTORY, name + "_disk1.qcow2")
        image2 = os.path.join(config.DISK_IMAGES_DIRECTORY, name + "_disk2.qcow2")
        serialLog = os.path.join(config.SERIAL_LOGS_DIRECTORY, name + ".serial.txt")
        hardwareConstraints = requirement['hardwareConstraints']
        imagecommands.create(
            image=image1, sizeGB=hardwareConstraints['minimumDisk1SizeGB'])
        imagecommands.create(
            image=image2, sizeGB=hardwareConstraints['minimumDisk2SizeGB'])
        mani = manifest.Manifest.create(
            name=name,
            memoryMB=int(1024 * hardwareConstraints['minimumRAMGB']),
            vcpus=hardwareConstraints['minimumCPUs'] \
                if hardwareConstraints['minimumCPUs'] is not None else 1,
            disk1Image=image1,
            disk2Image=image2,
            primaryMACAddress=network.primaryMACAddressFromVMIndex(index),
            secondaryMACAddress=network.secondMACAddressFromVMIndex(index),
            networkName=network.NAME,
            serialOutputFilename=serialLog)
        with libvirtsingleton.it().lock():
            domain = libvirtsingleton.it().libvirt().defineXML(mani.xml())
        return cls(
            index=index, domain=domain, manifest=mani,
            imageLabel=requirement['imageLabel'],
            imageHint=requirement['imageHint'])

    @classmethod
    def _nameFromIndex(cls, index):
        return "rackattack-vm%d" % index

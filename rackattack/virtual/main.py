import logging
logging.basicConfig(level=logging.DEBUG)
import time
import argparse
from rackattack.virtual import ipcserver
from rackattack.virtual.kvm import vms
from rackattack.virtual.kvm import cleanup
from rackattack.virtual import allocator
import rackattack.virtual.handlekill
from rackattack.virtual.kvm import config
from rackattack.virtual.kvm import network
from rackattack.common import dnsmasq
from rackattack.common import tftpboot
import atexit

parser = argparse.ArgumentParser()
parser.add_argument("--port", default=1011, type=int)
parser.add_argument("--maximumVMs", type=int)
parser.add_argument("--diskImagesDirectory")
parser.add_argument("--serialLogsDirectory")
args = parser.parse_args()

if args.maximumVMs:
    config.MAXIMUM_VMS = args.maximumVMs
if args.diskImagesDirectory:
    config.DISK_IMAGES_DIRECTORY = args.diskImagesDirectory
if args.serialLogsDirectory:
    config.SERIAL_LOGS_DIRECTORY = args.serialLogsDirectory

cleanup.cleanup()
atexit.register(cleanup.cleanup)
network.setUp()
tfpbootInstance = tftpboot.TFTPBoot(
    nodesMACIPPairs=network.allNodesMACIPPairs(),
    netmask=network.NETMASK,
    serverIP=network.GATEWAY_IP_ADDRESS)
dnsmasq.DNSMasq(
    tftpboot=tfpbootInstance,
    serverIP=network.GATEWAY_IP_ADDRESS,
    netmask=network.NETMASK,
    gateway=network.GATEWAY_IP_ADDRESS,
    nameserver=network.GATEWAY_IP_ADDRESS,
    nodesMACIPPairs=network.allNodesMACIPPairs())
vmsInstance = vms.VMs()
allocatorInstance = allocator.Allocator(vms=vmsInstance)
server = ipcserver.IPCServer(
    tcpPort=args.port,
    vms=vmsInstance,
    allocator=allocatorInstance)
logging.info("Virtual RackAttack up and running")
while True:
    time.sleep(1000 * 1000)

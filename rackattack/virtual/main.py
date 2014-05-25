import logging
logging.basicConfig(level=logging.DEBUG)
import time
import argparse
from rackattack.virtual import ipcserver
from rackattack.virtual.kvm import vms
from rackattack.virtual.kvm import cleanup
from rackattack.virtual import allocator
from rackattack.virtual.kvm import config
from rackattack.virtual.kvm import network

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
network.setUp()
vmsInstance = vms.VMs()
allocatorInstance = allocator.Allocator(vms=vmsInstance)
server = ipcserver.IPCServer(tcpPort=args.port, vms=vmsInstance, allocator=allocatorInstance)
logging.info("Virtual RackAttack up and running")
while True:
    time.sleep(1000 * 1000)

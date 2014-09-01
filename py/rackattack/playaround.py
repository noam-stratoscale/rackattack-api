import os
from rackattack.ssh import connection
from rackattack import clientfactory
from rackattack import api
connection.discardParamikoLogs()
connection.discardSSHDebugMessages()
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--label", required=True)
parser.add_argument("--user", required=True, help="User to report to provider")
parser.add_argument("--nice", type=float, default=1)
args = parser.parse_args()

print "Connecting"
client = clientfactory.factory()
print "Allocating"
allocation = client.allocate(
    requirements={'node': api.Requirement(imageLabel=args.label, imageHint="playaround")},
    allocationInfo=api.AllocationInfo(user=args.user, purpose="playaround", nice=args.nice))
allocation.wait(timeout=8 * 60)
assert allocation.done(), "Allocation failed"
print "Done allocating, Waiting for boot to finish"
try:
    node = allocation.nodes()['node']
    credentials = node.rootSSHCredentials()
    ssh = connection.Connection(**credentials)
    ssh.waitForTCPServer()
    ssh.connect()
    ssh.close()
    print "ROOT SSH Credentials:"
    print credentials
    print "Opening ssh session. Close it to free up allocation"
    os.system(
        "sshpass -p %(password)s ssh -o ServerAliveInterval=5 -o ServerAliveCountMax=1 "
        "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p %(port)d "
        "%(username)s@%(hostname)s" % credentials)
finally:
    allocation.free()

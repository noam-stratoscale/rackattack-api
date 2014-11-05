import unittest
import subprocess
import os
import test
import time
import contextlib
import socket
from rackattack import clientfactory
from rackattack.ssh import connection
from rackattack import api


SIMPLE_USE_CASE = os.path.join(os.path.dirname(test.__file__), "simpleusecase.py")
HINT = 'rootfs-basic'
LABEL = subprocess.check_output([
    "solvent", "printlabel", "--product", "rootfs", "--repositoryBasename",
    "rootfs-basic"]).strip()
TCPSERVER_SENDMESSAGE = os.path.join(os.path.dirname(__file__), "tcpserver_sendmessage.py")
TCPSERVER_READEVERYTHING = os.path.join(os.path.dirname(__file__), "tcpserver_readeverything.py")


class Test(unittest.TestCase):
    def test_singleNodeAllocation(self):
        popen = subprocess.Popen(["python", SIMPLE_USE_CASE], stdin=subprocess.PIPE)
        popen.stdin.write("c\n")
        popen.stdin.close()
        result = popen.wait()
        if result != 0:
            raise Exception("simpleusecase.py failed %d" % result)

    def test_singleNodeAllocation_PDBDoesNotCauseAllocationToDie(self):
        popen = subprocess.Popen(["python", SIMPLE_USE_CASE], stdin=subprocess.PIPE)
        print "Sleeping for 180 seconds, to make sure heartbeat timeout occours, if pdb stops"
        time.sleep(180)
        print "Done Sleeping for 180 seconds, resuming PDB"
        popen.stdin.write("c\n")
        popen.stdin.close()
        result = popen.wait()
        if result != 0:
            raise Exception("simpleusecase.py failed %d" % result)

    def test_LocalForwardingTunnel(self):
        with self._allocateOne() as (node, ssh):
            ssh.ftp.putFile("/tmp/server.py", TCPSERVER_SENDMESSAGE)
            ssh.run.backgroundScript("python /tmp/server.py 7788 hello")
            port = ssh.tunnel.localForward(7788)
            port2 = ssh.tunnel.localForward(7789)
            self.assertIn('hello', self._receiveAll(port))
            self.assertIn('hello', self._receiveAll(port))
            self.assertIn('hello', self._receiveAll(port))
            ssh.ftp.putFile("/tmp/server.py", TCPSERVER_READEVERYTHING)
            ssh.run.backgroundScript("python /tmp/server.py 7789 > /tmp/output")
            self._send(port2, "wassup")
            self.assertIn('wassup', ssh.ftp.getContents("/tmp/output"))
            print "Stopping all tunnels"
            ssh.tunnel.stopAll()
            with self.assertRaises(Exception):
                self._receiveAll(port)
            print "Closing tunnel"
            ssh.tunnel.close()
            print "Sleeping for few seconds, watch for exceptions from other threads"
            time.sleep(3)
            print "Done Sleeping for few seconds"

    @contextlib.contextmanager
    def _allocateOne(self):
        client = clientfactory.factory()
        try:
            requirement = api.Requirement(imageLabel=LABEL, imageHint=HINT)
            info = api.AllocationInfo(user='rackattack-api test', purpose='integration test')
            allocation = client.allocate(dict(it=requirement), info)
            print "Created allocation, waiting for node inauguration"
            try:
                allocation.wait(timeout=7 * 60)
                print "Allocation successfull, waiting for ssh"
                nodes = allocation.nodes()
                assert len(nodes) == 1, nodes
                it = nodes['it']
                print "SSH credentials:", it.rootSSHCredentials()
                ssh = connection.Connection(**it.rootSSHCredentials())
                ssh.waitForTCPServer()
                ssh.connect()
                print "SSH connected"
                yield it, ssh
            finally:
                allocation.free()
        finally:
            client.close()

    def _receiveAll(self, port):
        result = []
        s = socket.socket()
        try:
            s.connect(("localhost", port))
            while True:
                data = s.recv(4096)
                if len(data) == 0:
                    return "".join(result)
                result.append(data)
        finally:
            s.close()

    def _send(self, port, message):
        s = socket.socket()
        try:
            s.connect(("localhost", port))
            s.sendall(message)
        finally:
            s.close()


if __name__ == '__main__':
    unittest.main()

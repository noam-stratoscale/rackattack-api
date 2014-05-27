import logging
import subprocess
import tempfile
import threading
import atexit
import time
import signal
import os


class DNSMasq(threading.Thread):
    @classmethod
    def killPrevious(self):
        logging.info("Killing previous instances of dnsmasq")
        while True:
            try:
                subprocess.check_output(
                    ["killall", "dnsmasq"], close_fds=True, stderr=subprocess.STDOUT)
                time.sleep(0.1)
            except:
                logging.info("Done killing previous instances of dnsmasq")
                return

    def __init__(self, tftpboot, serverIP, nodesMACIPPairs, netmask, gateway=None, nameserver=None):
        self._tftpboot = tftpboot
        self._nodesMACIPPairs = nodesMACIPPairs
        self._netmask = netmask
        self._gateway = gateway
        self._nameserver = nameserver
        self.killPrevious()
        self._logFile = tempfile.NamedTemporaryFile(suffix=".dnsmasq.log")
        self._configFile = self._configurationFile()
        self._stopped = False
        self._popen = subprocess.Popen(
            ['dnsmasq', '--no-daemon', '--listen-address=' + serverIP,
                '--conf-file=' + self._configFile.name],
            stdout=self._logFile, stderr=subprocess.STDOUT, close_fds=True)
        atexit.register(self._exit)
        threading.Thread.__init__(self)
        self.daemon = True
        threading.Thread.start(self)

    def _configurationFile(self):
        conf = tempfile.NamedTemporaryFile(suffix=".dnsmasq.conf")
        hosts = ['dhcp-host=%s,%s,infinite' % (mac.lower(), ip) for mac, ip in self._nodesMACIPPairs]
        gateway = 'dhcp-option=option:router,%s' % self._gateway if self._gateway is not None else ""
        nameserver = 'dhcp-option=6,%s' % self._nameserver if self._nameserver is not None else ""
        ips = [m[1] for m in self._nodesMACIPPairs]
        output = _TEMPLATE % dict(
            hosts="\n".join(hosts), netmask=self._netmask, gateway=gateway, nameserver=nameserver,
            tftpbootRoot=self._tftpboot.root(), firstIPAddress=min(ips), lastIPAddress=max(ips))
        conf.write(output)
        conf.flush()
        return conf

    def run(self):
        self._popen.wait()
        if self._stopped:
            return
        self._stopped = True
        logging.error("DNSMASQ process exited early, shutting down")
        logging.error("DNSMASQ output:\n%(output)s", dict(output=open(self._logFile.name).read()))
        os.system("cp %s /tmp/dnsmasq.error.log" % self._logFile.name)
        os.system("cp %s /tmp/dnsmasq.error.config" % self._configFile.name)
        os.kill(os.getpid(), signal.SIGKILL)

    def _exit(self):
        if self._stopped:
            return
        self._stopped = True
        self._popen.terminate()

_TEMPLATE = \
    'tftp-root=%(tftpbootRoot)s\n' + \
    'enable-tftp\n' + \
    'dhcp-boot=pxelinux.0\n' + \
    'dhcp-option=vendor:PXEClient,6,2b\n' + \
    'dhcp-no-override\n' + \
    '%(gateway)s\n' + \
    '%(nameserver)s\n' + \
    '%(hosts)s\n' + \
    'dhcp-ignore=tag:!known\n' + \
    'pxe-prompt="Press F8 for boot menu", 1\n' + \
    'pxe-service=X86PC, "Boot from network", pxelinux\n' + \
    'pxe-service=X86PC, "Boot from local hard disk", 0\n' + \
    'dhcp-range=%(firstIPAddress)s,%(lastIPAddress)s,%(netmask)s,12h\n'

import subprocess
import os
import shutil
import time
from rackattack import clientfactory


class UserVirtualRackAttack:
    MAXIMUM_VMS = 4

    def __init__(self):
        self._port = 3443
        imageDir = os.path.join(os.getcwd(), "images.fortests")
        shutil.rmtree(imageDir, ignore_errors=True)
        self._popen = subprocess.Popen(
            ["python", "rackattack/virtual/main.py",
                "--port=%d" % self._port,
                "--diskImagesDirectory=" + imageDir,
                "--maximumVMs=%d" % self.MAXIMUM_VMS],
            close_fds=True, stderr=subprocess.STDOUT)
        time.sleep(0.1)

    def done(self):
        if self._popen.poll() is not None:
            raise Exception("Virtual RackAttack server terminated before it's time")
        self._popen.terminate()
        self._popen.wait()

    def createClient(self):
        os.environ['RACKATTACK_PROVIDER'] = 'tcp://localhost:%d' % self._port
        return clientfactory.factory()

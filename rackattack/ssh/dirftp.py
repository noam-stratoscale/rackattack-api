import tempfile
import tarfile
import cStringIO
import os
import random
from rackattack.ssh import ftp


class DirFTP:
    def __init__(self, sshClient):
        self._sshClient = sshClient
        self._ftp = ftp.FTP(sshClient)

    def put(self, path, originPath, compressed=True):
        tarContents = cStringIO.StringIO()
        tar = tarfile.open(mode="w:gz" if compressed else "w", fileobj=tarContents)
        tar.add(originPath, arcname=path)
        tar.close()
        remoteTarPath = tempfile.mktemp()
        self.putFileContents(remoteTarPath, tarContents.getvalue())
        try:
            self.runScript("tar -xf %s -C /" % (remoteTarPath))
        finally:
            self.delete(remoteTarPath)

    def get(self, localPath, originPath, compressed=True):
        remoteTarPath = tempfile.mktemp()
        self.runScript("cd %s\n tar --ignore-failed-read -c%sf %s *" % (
            originPath, "z" if compressed else "", remoteTarPath))
        tarContent = self.getFileContents(remoteTarPath)
        self.runScript("rm -f %s" % remoteTarPath)
        tar = tarfile.open(mode="r:gz" if compressed else "r", fileobj=cStringIO.StringIO(tarContent))
        if not os.path.isdir(localPath):
            os.makedirs(localPath)
        tar.extractall(path=localPath)

    def getMightChange(self, localPath, originPath, compressed=True):
        tempPath = '/tmp/dir_copy_%d' % (random.random() * 1e9)
        self.runScript('cp -r %s %s' % (originPath, tempPath))
        self.getDir(localPath, tempPath, compressed)
        self.runScript('rm -rf %s' % tempPath)

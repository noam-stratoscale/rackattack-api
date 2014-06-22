import cStringIO
from rackattack.ssh import reportprogress


class FTP:
    def __init__(self, sshClient):
        self._sshClient = sshClient

    def putFile(self, path, originPath, logProgressEveryBytes=None):
        sftp = self._sshClient.open_sftp()
        callback = None
        if logProgressEveryBytes is not None:
            report = reportprogress.ReportProgress(upload=True, logEveryBytes=logProgressEveryBytes)
            callback = report.log
        try:
            sftp.put(originPath, path, callback=callback)
        finally:
            sftp.close()

    def putContents(self, path, contents, logProgressEveryBytes=None):
        sftp = self._sshClient.open_sftp()
        BLOCK_SIZE = 128 * 1024
        callback = None
        if logProgressEveryBytes is not None:
            report = reportprogress.ReportProgress(upload=True, logEveryBytes=logProgressEveryBytes)
            callback = report.log
        try:
            sftp.chdir('.')
            fileOperation = sftp.file(path, mode="wb")
            try:
                for i in xrange(0, len(contents), BLOCK_SIZE):
                    if callback is not None:
                        callback(i, len(contents))
                    fileOperation.write(contents[i: i + BLOCK_SIZE])
            finally:
                fileOperation.close()
        finally:
            sftp.close()

    def getFile(self, path, destinationPath, logProgressEveryBytes=None):
        callback = None
        if logProgressEveryBytes is not None:
            report = reportprogress.ReportProgress(upload=False, logEveryBytes=logProgressEveryBytes)
            callback = report.log
        sftp = self._sshClient.open_sftp()
        try:
            sftp.get(path, destinationPath, callback=callback)
        finally:
            sftp.close()

    def getContents(self, path, logProgressEveryBytes=None):
        callback = None
        if logProgressEveryBytes is not None:
            report = reportprogress.ReportProgress(upload=False, logEveryBytes=logProgressEveryBytes)
            callback = report.log
        BLOCK_SIZE = 128 * 1024
        result = cStringIO.StringIO()
        transferredBytes = 0
        sftp = self._sshClient.open_sftp()
        try:
            f = sftp.file(path, mode="r")
            try:
                while True:
                    segment = f.read(BLOCK_SIZE)
                    if segment == "":
                        return result.getvalue()
                    result.write(segment)
                    transferredBytes += len(segment)
                    if callback is not None:
                        callback(transferredBytes, None)
            finally:
                f.close()
        finally:
            sftp.close()

    def delete(self, path):
        sftp = self._sshClient.open_sftp()
        try:
            sftp.unlink(path)
        finally:
            sftp.close()

import logging


class ReportProgress:
    def __init__(self, upload, logEveryBytes):
        self._upload = upload
        self._logEveryBytes = logEveryBytes
        self._lastLog = 0

    def log(self, bytesTransferred, total):
        if bytesTransferred / self._logEveryBytes <= self._lastLog:
            return
        self._lastLog = bytesTransferred / self._logEveryBytes
        data = dict(
            megabytes=bytesTransferred / 1024 / 1024,
            totalMegabytes=(total / 1024 / 1024 if total is not None else "?"))
        if self._upload:
            logging.info("Upload: %(megabytes)dMB/%(totalMegabytes)sMB", data)
        else:
            logging.info("Download: %(megabytes)dMB/%(totalMegabytes)sMB", data)

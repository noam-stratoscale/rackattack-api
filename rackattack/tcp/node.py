from rackattack import api


class Node(api.Node):
    def __init__(self, ipcClient, name, allocated):
        assert 'id' in allocated
        assert 'primaryMACAddress' in allocated
        assert 'secondaryMACAddress' in allocated
        assert 'ipAddress' in allocated
        self._ipcClient = ipcClient
        self._name = name
        self._allocated = allocated

    def rootSSHCredentials(self):
        return self._ipcClient.call("rootSSHCredentials", id=self._allocated['id'])

    def unallocate(self):
        self._ipcClient.call("unallocate", id=self._allocated['id'])
        del self._ipcClient
        del self._name
        del self._allocated

    def name(self):
        return self._name

    def primaryMACAddress(self):
        return self._allocated['primaryMACAddress']

    def secondaryMACAddress(self):
        return self._allocated['secondaryMACAddress']

    def ipAddress(self):
        return self._allocated['ipAddress']

    def setPXEParameters(self, answerDHCP=True, assimilatorParameters=None):
        return self._ipcClient.call(
            'setPXEParameters', id=self._allocated['id'], answerDHCP=answerDHCP,
            assimilatorParameters=assimilatorParameters)

    def initialStart(self):
        return self._ipcClient.call('initialStart', id=self._allocated['id'], ipcTimeoutMS=10 * 60 * 1000)

    def coldRestart(self):
        return self._ipcClient.call('coldRestart', id=self._allocated['id'])

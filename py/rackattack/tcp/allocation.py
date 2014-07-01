from rackattack import api
from rackattack.tcp import node
import threading
import logging


class Allocation(api.Allocation):
    def __init__(self, id, requirements, ipcClient, subscribe, heartbeat):
        self._id = id
        self._requirements = requirements
        self._ipcClient = ipcClient
        self._heartbeat = heartbeat
        self._subscribe = subscribe
        self._dead = False
        self._waitEvent = threading.Event()
        self._subscribe.register(self._eventBroadcasted)
        self._heartbeat.register(id)
        if self.dead() or self.done():
            self._waitEvent.set()
        logging.info("allocation created")

    def _idForNodeIPC(self):
        assert not self._dead
        return self._id

    def done(self):
        assert not self._dead
        return self._ipcClient.call('allocation__done', id=self._id)

    def dead(self):
        result = self._ipcClient.call('allocation__dead', id=self._id)
        if result:
            self._dead = True
        return result

    def wait(self, timeout=None):
        self._waitEvent.wait(timeout=timeout)
        if not self._waitEvent.isSet():
            raise Exception("Timeout waiting for allocation")
        death = self.dead()
        if death is not None:
            raise Exception(death)

    def nodes(self):
        assert not self._dead
        assert self.done()
        allocatedMap = self._ipcClient.call('allocation__nodes', id=self._id)
        result = {}
        for name, info in allocatedMap.iteritems():
            nodeInstance = node.Node(
                ipcClient=self._ipcClient, allocation=self, name=name, info=info)
            result[name] = nodeInstance
        return result

    def free(self):
        logging.info("freeing allocation")
        self._ipcClient.call('allocation__free', id=self._id)
        self._dead = True
        self._heartbeat.unregister(self._id)

    def setForceReleaseCallback(self, callback):
        raise NotImplementedError("here")

    def _eventBroadcasted(self, event):
        if event.get('event', None) == "allocation__changedState" and \
                event.get('allocationID', None) == self._id:
            self._waitEvent.set()
        if event.get('event', None) == "allocation__providerMessage" and \
                event.get('allocationID', None) == self._id:
            logging.info("Rackattack provider says: %(message)s", dict(message=event['message']))

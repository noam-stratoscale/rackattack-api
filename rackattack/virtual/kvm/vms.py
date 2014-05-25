from rackattack.virtual.kvm import vm


class VMs:
    def __init__(self):
        self._index = 0
        self._vms = {}

    def create(self, requirement):
        self._index += 1
        theVM = vm.VM.create(index=self._index, requirement=requirement)
        self._vms[self._index] = theVM
        return theVM

    def inUse(self):
#todo: not implmeneted"
        return []

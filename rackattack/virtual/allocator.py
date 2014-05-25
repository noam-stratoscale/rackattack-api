from rackattack import api
from rackattack.virtual.kvm import config


class Allocator:
    def __init__(self, vms):
        self._vms = vms

    def allocate(self, requirements, allocationInfo):
        self._notWayTooManyVMs(requirements)
        self._notTooManyVMsInUse(requirements)
        allocated = {}
        try:
            for name, requirement in requirements.iteritems():
                vm = self._tryReuse(requirement)
                if vm is not None:
                    allocated[name] = vm
            for name, requirement in requirements.iteritems():
                if name in allocated:
                    continue
                vm = self._tryReassign(requirement)
                if vm is not None:
                    allocated[name] = vm
            for name, requirement in requirements.iteritems():
                if name in allocated:
                    continue
                vm = self._create(requirement)
                allocated[name] = vm
        except:
            for name, vm in allocated:
                self._vms.noLongerInUse(vm)
            raise
        assert allocated.keys() == requirements.keys()
        return allocated

    def _notWayTooManyVMs(self, requirements):
        if len(requirements) > config.MAXIMUM_VMS:
            raise api.NotEnoughResourcesForAllocation(
                "Allocation request is more than maximum defined VMs for this "
                "virtual rackattack")

    def _notTooManyVMsInUse(self, requirements):
        if len(requirements) > config.MAXIMUM_VMS - len(self._vms.inUse()):
            raise api.NotEnoughResourcesForAllocation(
                "%d vms are in use, and maximum is %d. Unable to allocate %d vms" %
                (len(self._vms.inUse()), config.MAXIMUM_VMS, len(requirements)))

    def _tryReuse(self, requirement):
# todo: implement
        return None

    def _tryReassign(self, requirement):
# todo: implement
        return None

    def _create(self, requirement):
        return self._vms.create(requirement)

class NotEnoughResourcesForAllocation(Exception):
    pass


class Client:
    """
    To create a client:
    from rackattack import clientfactory
    client = clientfactory.factory()

    Open a virtual or physical provisioning client depending on the
    variables defined in the environment. Look inside clientfactory
    for more details
    """
    def allocate(self, requirements, allocationInfo, forceReleaseCallback):
        """
        This method receives a dict from names of nodes, to their requirements,
        and returns a matching map with a Node instance for each node name, or
        throws NotEnoughResourcesForAllocation.
        """
        assert False, "Deriving class must implement"


class Requirement:
    def __init__(self, imageLabel, imageHint=None, hardwareConstraints=None):
        """
        Describes what is expected of the allocated node.
        imageLabel is the name of the label to osmos into the node, or None
        to skip osmosis.
        imageHint is a string that allows the allocator to attempt to
        find a close matching image to shorten the image osmosis process.
        """
        self.imageLabel = imageLabel
        self.imageHint = imageHint
        self.hardwareConstraints = dict(
            minimumCPUs=1, minimumRAMGB=2,
            minimumDisk1SizeGB=16, minimumDisk2SizeGB=16)
        if hardwareConstraints is not None:
            self.hardwareConstraints.update(hardwareConstraints)


class AllocationInfo:
    def __init__(self, user, purpose, nice=0, comment=""):
        """
        This object represents what is this allocation for, by whom.
        This is important only for scheduling of shared resources

        user can be a name, or 'continuous integration', or 'QA'

        purpose can be:
        - 'build'
        - 'bare metal host for rack test'
        - 'vm runner for virtual rack test' (==slave)
        note: the last option is used to provision a CI slave, which
        means a virtual rack provider will be running on it.

        nice value: if you are writing a gready system, for example,
        a system for using as many free nodes as possible to run as
        many concurrent tests as possible, make sure to use increment
        this value for each additional allocation.
        """
        self.user = user
        self.purpose = purpose
        self.nice = nice
        self.comment = comment


class Node:
    def rootSSHCredentials(self):
        """
        returns a dictionary with: hostname, username == root, either password or key,
        and port == 22. Useful to pass as **kwargs to SSH class
        """
        assert False, "Deriving class must implement"

    def unallocate(self):
        """
        Physical provisioning should also have policy to garbage collent nodes
        from crashed tests. After call this method, this object might not be
        used again.
        """
        assert False, "Deriving class must implement"

    def name(self):
        assert False, "Deriving class must implement"

    def primaryMACAddress(self):
        "Returns the MAC address out of which the node will DHCP from (e.g., eth0)"
        assert False, "Deriving class must implement"

    def secondaryMACAddress(self):
        "Returns the MAC address of the second NIC (e.g., eth1)"
        assert False, "Deriving class must implement"

    def ipAddress(self):
        "IP address assigned at DHCP to the primary NIC"
        assert False, "Deriving class must implement"

    def setPXEParameters(self, answerDHCP=True, assimilatorParameters=None):
        assert False, "Deriving class must implement"

    def initialStart(self):
        """
        Initial start: reboot/kexec a physical node or start the VM
        should be called exactly once after allocation, possibly after
        calling setPXEParameters
        """
        assert False, "Deriving class must implement"

    def coldRestart(self):
        """
        cold reboot the host, for testing purposes. This "pulls the switch", does not
        allow orderly shutdown. Note: physical servers sometimes take as much as 5 minutes
        to reboot, due long bios wakeup times.
        """
        assert False, "Deriving class must implement"

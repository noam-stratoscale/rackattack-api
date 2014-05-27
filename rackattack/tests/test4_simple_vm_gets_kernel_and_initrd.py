import unittest
from rackattack.tests import uservirtualrackattack
import rackattack
from rackattack import api


class Test(unittest.TestCase):
    def setUp(self):
        self.assertTrue('/usr/' not in rackattack.__file__)
        self.server = uservirtualrackattack.UserVirtualRackAttack()

    def tearDown(self):
        self.server.done()

    def test_it(self):
        self.client = self.server.createClient()
        node = self.allocate()
        try:
            node.initialStart()
        finally:
            node.unallocate()

    def allocate(self):
        result = self.client.allocate(
            requirements={'node1': api.Requirement(
                imageLabel="rootfs-basic", imageHint="basic")},
            allocationInfo=api.AllocationInfo(
                user="whitebox", purpose="whitebox", nice=0),
            forceReleaseCallback=self.forceReleaseMustNotBeCalled)
        self.assertEquals(len(result), 1)
        return result['node1']

    def forceReleaseMustNotBeCalled(self):
        self.assertTrue(False, "Force release must not be called")

if __name__ == '__main__':
    unittest.main()

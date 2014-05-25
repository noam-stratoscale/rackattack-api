import unittest
from rackattack.tests import testlib
import rackattack
from rackattack import api


class Test(unittest.TestCase):
    def setUp(self):
        self.assertTrue('/usr/' not in rackattack.__file__)
        self.server = testlib.UserVirtualRackAttack()

    def tearDown(self):
        self.server.done()

    def test_it(self):
        self.client = self.server.createClient()
        with self.assertRaises(api.NotEnoughResourcesForAllocation):
            self.allocate()

    def allocate(self):
        self.assertEquals(self.server.MAXIMUM_VMS, 4)
        self.client.allocate(
            requirements={'node%d' % i: api.Requirement(
                imageLabel="rootfs-basic", imageHint="basic")
                for i in xrange(1, self.server.MAXIMUM_VMS + 2)},
            allocationInfo=api.AllocationInfo(
                user="whitebox",
                purpose="whitebox",
                nice=0),
            forceReleaseCallback=self.forceReleaseMustNotBeCalled)

    def forceReleaseMustNotBeCalled(self):
        self.assertTrue(False, "Force release must not be called")

if __name__ == '__main__':
    unittest.main()

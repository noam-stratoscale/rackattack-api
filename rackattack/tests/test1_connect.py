import unittest
from rackattack.tests import testlib
import rackattack


class Test(unittest.TestCase):
    def setUp(self):
        self.assertTrue('/usr/' not in rackattack.__file__)
        self.server = testlib.UserVirtualRackAttack()

    def tearDown(self):
        self.server.done()

    def test_emptyConnection(self):
        client = self.server.createClient()

if __name__ == '__main__':
    unittest.main()

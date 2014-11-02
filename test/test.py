import unittest
import subprocess
import os
import test
import time


SIMPLE_USE_CASE = os.path.join(os.path.dirname(test.__file__), "simpleusecase.py")


class Test(unittest.TestCase):
    def test_singleNodeAllocation(self):
        popen = subprocess.Popen(["python", SIMPLE_USE_CASE], stdin=subprocess.PIPE)
        popen.stdin.write("c\n")
        popen.stdin.close()
        result = popen.wait()
        if result != 0:
            raise Exception("simpleusecase.py failed %d" % result)

    def test_singleNodeAllocation_PDBDoesNotCauseAllocationToDie(self):
        popen = subprocess.Popen(["python", SIMPLE_USE_CASE], stdin=subprocess.PIPE)
        print "Sleeping for 180 seconds, to make sure heartbeat timeout occours, if pdb stops"
        time.sleep(180)
        print "Done Sleeping for 180 seconds, resuming PDB"
        popen.stdin.write("c\n")
        popen.stdin.close()
        result = popen.wait()
        if result != 0:
            raise Exception("simpleusecase.py failed %d" % result)


if __name__ == '__main__':
    unittest.main()

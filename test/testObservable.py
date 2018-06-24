import unittest
import os,sys,inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from observer import Observer

class TestObserver(unittest.TestCase):

    def testAbstractCommandInstanciation(self):
        with self.assertRaises(TypeError):
            c = Observer()

if __name__ == '__main__':
    unittest.main()
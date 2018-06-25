import inspect
import os
import sys
import unittest
import pickle

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0,currentdir) # this instruction is necessary for successful importation of utilityfortest module when
                              # the test is executed standalone

from apikey.apikeyfilegenerator import ApiKeyFileGenerator

class TestApiKeyFileGenerator(unittest.TestCase):

    def testCreateKeyFile(self):
        '''
        This test demonsttates how to test a command line script using artparse.
        :return:
        '''
        ap = ApiKeyFileGenerator()
        ap.createKeyFile(['-a', 'key', '-s', 'secret key', '-f', 'testfile', '-pw', 'monpw'])

        with open(ApiKeyFileGenerator.FILE_PATH + 'testfile.bin', 'rb') as handle:
            encryptedKeyList = pickle.load(handle)

        self.assertEqual(['w5jDlMOn', 'w6DDlMORw6LDnMOhwo_DmcOVw7A='], encryptedKeyList)
        self.assertEqual('key', ap.decode('monpw', encryptedKeyList[0]))
        self.assertEqual('secret key', ap.decode('monpw', encryptedKeyList[1]))


    def testCreateKeyFileNoArgs(self):
        ap = ApiKeyFileGenerator()
        with self.assertRaises(SystemExit):
            ap.createKeyFile([])


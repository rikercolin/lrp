'''
LRP Config/Main File
Alter test settings here
'''

import keyfile
import tester

debug = True
category = ''
source = ''
kfilename = ''

def main():
    keyfile.build(category, source, kfilename)
    kfile = keyfile.read(kfilename)
    kfile.data_folder_integratity()
    outcome = tester.test(kfile.documents, debug)
    print(outcome)


main()

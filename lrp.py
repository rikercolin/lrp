'''
Read Offline & Online Data
Save Online data into Offline
'''

import re
import os
import datetime
from enum import Enum

import keyfile
import tester

verbose = True
category = 'address'
source = ''

def main():
    keyfile.build('address','sources')
    kfile = keyfile.read("address_2022-06-28.json")
    kfile.data_folder_integratity()
    outcome = tester.test(kfile.documents)
    print(outcome)

main()

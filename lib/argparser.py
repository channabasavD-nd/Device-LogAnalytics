import os
import argparse
import sys

import pandas as pd
#from lib.loggerutil import *


# NOTE For command line interface 

def arguments():  
    parser = argparse.ArgumentParser(description="Download logs for a device for a particular date")
    parser.add_argument('--deviceid', type=str, required=True, help="device ID")
    parser.add_argument('--env', type=str, required=True, help="staging or production")
    parser.add_argument('--date', type=str, required=True, help="date in YYYY-MM-DD")
    parser.add_argument('--device_type', type=str, help="device_type DTS or Normal")
    #parser.add_argument('--action', type=str, default='all', help="download/extract/all")
    #parser.add_argument('--format', type=str, default='new', help="old/new")
    args = parser.parse_args()


    details = {}
    try:
        args = parser.parse_args()
        details['deviceid'] = args.deviceid
        details['env'] = args.env
        details['date'] = args.date
        details['deviceType'] = args.device_type



    except Exception as e:
        print(e)
        e = sys.exc_info()[0]
    return details
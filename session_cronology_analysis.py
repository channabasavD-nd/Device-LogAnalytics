import re
import configparser
from lib import mongodb
from lib import argparser
from datetime import datetime
from pymongo import MongoClient
from utils import download_logs
import streamlit as st


config = configparser.ConfigParser()
# config.read('streamlit/variables.ini') # while using cli for downloads 
config.read('variables.ini')


class Session_details(object):
    def __init__(self, outdir, details):
        self.outdir = outdir
        self.session_ids = {}
        self.details = details
        self.tracebacks = {
             'device_ID' : details['deviceid'],
             'date' : details['date'],
             'ndcentral': {},
             'inwardAnalyticsClient': {},
             'outwardAnalyticsClient': {},
             'inertialAnalyticsClient': {},
             'inferenceInertial': {},
             'analyticsService': {}
             }

    def get_sessioIDs(self):
        with open(f"{self.outdir}/ndcentral.log", "r", encoding="utf-8", errors="ignore") as file:
            log_content = file.read().splitlines()

        for line in log_content:
                try:
                    if self.details['deviceType'] == 'DTS':
                        session_id_match = re.search(config.get('sessionInfo','sessionID_DTS'), line)
                    else:
                        session_id_match = re.search(config.get('sessionInfo','sessionID'), line)
                    if session_id_match:
                        session_id = session_id_match.group(2)
                        if self.details['deviceType'] == 'DTS':
                            timestamp = datetime.strptime(session_id_match.group(1), "%m/%d/%Y %H:%M:%S.%f")
                        else:
                            timestamp = datetime.utcfromtimestamp(int(session_id_match.group(1))/1000)
                        self.session_ids[session_id]={
                                                    "device_ID": self.details['deviceid'],
                                                    "session_ID": session_id,
                                                    "start_time": timestamp,
                                                    "end_time": None,
                                                    "ota_version": None,
                                                    "date": self.details['date'],
                                                    "inwardAnalyticsClient":{
                                                                            "start_time": None,
                                                                            "obs_data_written_status": 0,
                                                                            "end_time": None,
                                                                            "events_detected": -1
                                                                            }, 
                                                    'outwardAnalyticsClient':{
                                                                            "start_time": None,
                                                                            "obs_data_written_status": 0,
                                                                            "end_time": None,
                                                                            "events_detected": -1
                                                                            }, 
                                                    'inertialAnalyticsClient':{
                                                                            "start_time": None,
                                                                            "obs_data_written_status": 0,
                                                                            "end_time": None,
                                                                            "events_detected": -1
                                                                            }, 
                                                    'inferenceInertial':{
                                                                        "NRT_processing_status": 0,
                                                                        "summary_file_written_status": 0
                                                                        }, 
                                                    "analyticsService":{
                                                                        "Inward_session_drop": 0,
                                                                        "reason_for_inward_session_drop": 'NA',
                                                                        "Outward session drop": 0,
                                                                        "reason_for_outward_session_drop": 'NA'
                                                                        }, 
                                                    'inference':{
                                                                "traceback_count":0,
                                                                "outward_NRT":{
                                                                            "outward_NRT_processing_status": -1,
                                                                            "failure_reason_o": -1,
                                                                            "processed_time": -1,
                                                                            "summary_file_written_status": -1,
                                                                            "traceback": 'NA'
                                                                            }, 
                                                                "inward_NRT":{
                                                                            "inward_NRT_processing_status": -1,
                                                                            "failure_reason_o": -1,
                                                                            "processed_time": -1,
                                                                            "summary_file_written_status": -1,
                                                                            "traceback": 'NA'
                                                                            }
                                                                } 
                                                    }
                    if "traceback" in line.lower():
                        traceback_index = log_content.index(line)
                        if not log_content[traceback_index+1][:2].isdigit():
                            traceback = ''
                            while traceback_index<len(log_content) and not log_content[traceback_index][:2].isdigit():
                                traceback+='\n'+log_content[traceback_index]
                                traceback_index+=1
                        else:
                                traceback = 'Traceback ' + line.split('Traceback')[-1]
                        if traceback in self.tracebacks['ndcentral']:
                            self.tracebacks['ndcentral'][traceback]+=1
                        else:
                            self.tracebacks['ndcentral'][traceback] = 1
                        
                except Exception as e:
                    print('\nException occured in get_sessioIDs :',e,'\n')
                    continue
                
        print('sessionIDs initialized')
        st.write('sessionIDs initialized')

    def inwardAnalyticsClient_stats(self):
        with open(f"{self.outdir}/inwardAnalyticsClient.log", "r", encoding="utf-8", errors="ignore") as file:
            log_content = file.read().splitlines()

        for line in log_content:
            try:
                startTime_match = re.search(config.get('inwardClient', 'startTime'), line)
                endTime_match = re.search(config.get('inwardClient', 'endTime'), line)
                events_match = re.search(config.get('inwardClient', 'eventsDetected'), line)
                if startTime_match :
                    session_id = startTime_match.group(2)
                    updated_timestamp = int(startTime_match.group(1))
                    self.session_ids[session_id]['inwardAnalyticsClient']['start_time'] = datetime.utcfromtimestamp(updated_timestamp/1000)
                elif endTime_match:
                    session_id = endTime_match.group(2)
                    timestamp_str = endTime_match.group(1)
                    self.session_ids[session_id]['inwardAnalyticsClient']['end_time'] = datetime.strptime(timestamp_str,"%Y-%m-%d %H:%M:%S,%f" )
                    self.session_ids[session_id]['inwardAnalyticsClient']['obs_data_written_status'] = 1
                elif events_match:
                    session_id = events_match.group(2)
                    total_events_detected = int(events_match.group(1)) 
                    self.session_ids[session_id]['inwardAnalyticsClient']['events_detected'] = total_events_detected

                if "traceback" in line.lower():
                        traceback_index = log_content.index(line)
                        if not log_content[traceback_index+1][:2].isdigit():
                            traceback = ''
                            while traceback_index<len(log_content) and not log_content[traceback_index][:2].isdigit():
                                traceback+='\n'+log_content[traceback_index]
                                traceback_index+=1
                        else:
                                traceback = 'Traceback ' + line.split('Traceback')[-1]
                        # self.tracebacks['inwardAnalyticsClient'].append(traceback)
                        if traceback in self.tracebacks['inwardAnalyticsClient']:
                            self.tracebacks['inwardAnalyticsClient'][traceback]+=1
                        else:
                            self.tracebacks['inwardAnalyticsClient'][traceback] = 1
            except Exception as e:
                print('\nException occured in inwardAnalyticsClient:',e,'\n')
                continue
        print("updated inwardAnalyticsClient")
        st.write("updated inwardAnalyticsClient data")


    def outwardAnalyticsClient_stats(self):
            with open(f"{self.outdir}/outwardAnalyticsClient.log", "r", encoding="utf-8", errors="ignore") as file:
                log_content = file.read().splitlines()

            for line in log_content:
                try:
                    startTime_match = re.search(config.get('outwardClient', 'startTime'), line)
                    endTime_match = re.search(config.get('outwardClient', 'endTime'), line)
                    # events_match = re.search(inwardAnalyticsClient_events_re, line)
                    if startTime_match :
                        session_id = startTime_match.group(2)
                        updated_timestamp = startTime_match.group(1)
                        self.session_ids[session_id]['outwardAnalyticsClient']['start_time'] = datetime.strptime(updated_timestamp,"%Y-%m-%d %H:%M:%S,%f" )
                    elif endTime_match:
                        session_id = endTime_match.group(2)
                        timestamp_str = endTime_match.group(1)
                        self.session_ids[session_id]['outwardAnalyticsClient']['end_time'] = datetime.strptime(timestamp_str,"%Y-%m-%d %H:%M:%S,%f" )
                        self.session_ids[session_id]['outwardAnalyticsClient']['obs_data_written_status'] = 1

                    if "traceback" in line.lower():
                        traceback_index = log_content.index(line)
                        if not log_content[traceback_index+1][:2].isdigit():
                            traceback = ''
                            while traceback_index<len(log_content) and not log_content[traceback_index][:2].isdigit():
                                traceback+='\n'+log_content[traceback_index]
                                traceback_index+=1
                        else:
                                traceback = 'Traceback ' + line.split('Traceback')[-1]
                        # self.tracebacks['outwardAnalyticsClient'].append(traceback)
                        if traceback in self.tracebacks['outwardAnalyticsClient']:
                            self.tracebacks['outwardAnalyticsClient'][traceback]+=1
                        else:
                            self.tracebacks['outwardAnalyticsClient'][traceback] = 1

                except Exception as e:
                    print('\nException occured in outwardAnalyticsClient :',e,'\n')
                    continue
            print("updated outwardAnalyticsClient")
            st.write("updated outwardAnalyticsClient data")

    def inertialAnalyticsClient_stats(self):
            with open(f"{self.outdir}/inertialAnalyticsClient.log", "r", encoding="utf-8", errors="ignore") as file:
                log_content = file.read().splitlines()

            for line in log_content:
                try:
                    startTime_match = re.search(config.get('inertialClient', 'startTime'), line)
                    endTime_match = re.search(config.get('inertialClient', 'endTime'), line)
                    if startTime_match :
                        session_id = startTime_match.group(2)
                        updated_timestamp = startTime_match.group(1)
                        self.session_ids[session_id]['inertialAnalyticsClient']['start_time'] = datetime.strptime(updated_timestamp,"%Y-%m-%d %H:%M:%S,%f" )
                    elif endTime_match:
                        session_id = endTime_match.group(2)
                        timestamp_str = endTime_match.group(1)
                        self.session_ids[session_id]['inertialAnalyticsClient']['end_time'] = datetime.strptime(timestamp_str,"%Y-%m-%d %H:%M:%S,%f" )
                        self.session_ids[session_id]['inertialAnalyticsClient']['obs_data_written_status'] = 1
                    
                    if "traceback" in line.lower():
                        traceback_index = log_content.index(line)
                        if not log_content[traceback_index+1][:2].isdigit():
                            traceback = ''
                            while traceback_index<len(log_content) and not log_content[traceback_index][:2].isdigit():
                                traceback+='\n'+log_content[traceback_index]
                                traceback_index+=1
                        else:
                                traceback = 'Traceback ' + line.split('Traceback')[-1]
                        # self.tracebacks['inertialAnalyticsClient'].append(traceback)
                        if traceback in self.tracebacks['inertialAnalyticsClient']:
                            self.tracebacks['inertialAnalyticsClient'][traceback]+=1
                        else:
                            self.tracebacks['inertialAnalyticsClient'][traceback] = 1
                except Exception as e:
                    print('\nException occured in inertialAnalyticsClient:',e,'\n')
                    continue
            print("updated inertialAnalyticsClient")
            st.write("updated inertialAnalyticsClient data")
    
    def inferenceInertial_stats(self):
            with open(f"{self.outdir}/inference_inertial.log", "r", encoding="utf-8", errors="ignore") as file:
                log_content = file.read().splitlines()

            for line in log_content:
                try:
                    summaryFile_match = re.search(config.get('inferenceInertial', 'summaryFile'), line)
                    processing_match = re.search(config.get('inferenceInertial', 'processing'), line)
                    if processing_match:
                        # print('in_inf_iner')
                        session_id = processing_match.group(1)
                        self.session_ids[session_id]['inferenceInertial']["NRT_processing_status"] += 1
                    elif summaryFile_match:
                        session_id = summaryFile_match.group(1)
                        self.session_ids[session_id]['inferenceInertial']["summary_file_written_status"] = 1
                    if "traceback" in line.lower():
                        traceback_index = log_content.index(line)
                        if not log_content[traceback_index+1][:2].isdigit():
                            traceback = ''
                            while traceback_index<len(log_content) and not log_content[traceback_index][:2].isdigit():
                                traceback+='\n'+log_content[traceback_index]
                                traceback_index+=1
                        else:
                                traceback = 'Traceback ' + line.split('Traceback')[-1]
                        # self.tracebacks['inferenceInertial'].append(traceback)
                        if traceback in self.tracebacks['inferenceInertial']:
                            self.tracebacks['inferenceInertial'][traceback]+=1
                        else:
                            self.tracebacks['inferenceInertial'][traceback] = 1
                except Exception as e:
                    print('\nException occured in inferenceInertial:',e,'\n')
                    continue
            print("updated inferenceInertial")
            st.write("updated inferenceInertial data")
                
    def analyticsService_stats(self):
        with open(f"{self.outdir}/analytics.log", "r", encoding="utf-8", errors="ignore") as file:
            log_content = file.read().splitlines()

        for line in log_content:
            try:
                Inward_drop_match = re.search(config.get('analyticsService', 'InwardDroppedSession'), line) or re.search(config.get('analyticsService', 'InwardDroppedSession_slowdown'), line)
                Outward_drop_match = re.search(config.get('analyticsService', 'OutwardDroppedSession'), line) or re.search(config.get('analyticsService', 'OutwardDroppedSession_slowdown'), line)
                if Inward_drop_match :
                    session_id = Inward_drop_match.group(1)
                    Failure_cause = Inward_drop_match.group(2)
                    self.session_ids[session_id]['analyticsService']['reason_for_inward_session_drop'] = Failure_cause
                    self.session_ids[session_id]['analyticsService']['Inward_session_drop'] = 1
                elif Outward_drop_match:
                    session_id = Outward_drop_match.group(1)
                    Failure_cause = (Outward_drop_match.group(2))
                    self.session_ids[session_id]['analyticsService']['reason_for_outward_session_drop'] = Failure_cause
                    self.session_ids[session_id]['analyticsService']['Outward session drop'] = 1
                if "traceback" in line.lower():
                        traceback_index = log_content.index(line)
                        if not log_content[traceback_index+1][:2].isdigit():
                            traceback = ''
                            while traceback_index<len(log_content) and not log_content[traceback_index][:2].isdigit():
                                traceback+='\n'+log_content[traceback_index]
                                traceback_index+=1
                        else:
                                traceback = 'Traceback ' + line.split('Traceback')[-1]
                        # self.tracebacks['analyticsService'].append(traceback)
                        if traceback in self.tracebacks['analyticsService']:
                            self.tracebacks['analyticsService'][traceback]+=1
                        else:
                            self.tracebacks['analyticsService'][traceback] = 1
            except Exception as e:
                print('\nException occured in analyticsService:',e,'\n')
                continue
        print("updated Analytics")
        st.write("updated Analytics data")

    def inference_stats(self):
            with open(f"{self.outdir}/inference.log", "r", encoding="utf-8", errors="ignore") as file:
                log_content = file.read().splitlines()
            cur_session = None
            for line in log_content:
                try:
                    currentSession_match = re.search(config.get('sessionInfo', 'currentSession'), line)
                    Session_end_match = re.search(config.get('sessionInfo', 'session_endTime'), line)
                    Summary_match = re.search(config.get('inference', 'Summary'), line)
                    Processing_match = re.search(config.get('inference', 'Processing'), line)
                    NRT_failure_match = re.search(config.get('inference', 'NRT_failure'), line)
                    # print(cur_session)
                    if 'Traceback (most recent call last):' in line:
                        self.session_ids[cur_session]['inference']['traceback_count']+=1

                    if currentSession_match:
                        cur_session = currentSession_match.group(1)
                    elif NRT_failure_match:
                        service = NRT_failure_match.group(1)
                        traceback_index = log_content.index(line)+1
                        if not log_content[traceback_index][:2].isdigit():
                            traceback = ''
                            while traceback_index<len(log_content) and not log_content[traceback_index][:2].isdigit():
                                traceback+='\n'+log_content[traceback_index]
                                traceback_index+=1
                        else:
                            if "Traceback" in line:
                                traceback = 'Traceback ' + line.split('Traceback')[-1]

                        self.session_ids[cur_session]['inference'][f'{service}_NRT']['traceback'] = traceback
                    elif Session_end_match:
                        session_id = Session_end_match.group(2)
                        Timestamp = Session_end_match.group(1)
                        self.session_ids[session_id]['end_time'] = datetime.strptime(Timestamp,"%Y-%m-%d %H:%M:%S,%f" )   
                    elif Summary_match:
                        service = Summary_match.group(1)
                        session_id = Summary_match.group(2)
                        self.session_ids[session_id]['inference'][f'{service}_NRT']["summary_file_written_status"] = 1
                    elif Processing_match:
                        service = Processing_match.group(1) 
                        session_id = Processing_match.group(2)  
                        p_status = int(Processing_match.group(3))
                        p_time = Processing_match.group(4)
                        if p_status:
                            self.session_ids[session_id]['inference'][f'{service}_NRT'][f"{service}_NRT_processing_status"] = False
                            self.session_ids[session_id]['inference'][f'{service}_NRT']["processed_time"] = p_time
                        else:
                            self.session_ids[session_id]['inference'][f'{service}_NRT'][f"{service}_NRT_processing_status"] = True
                            self.session_ids[session_id]['inference'][f'{service}_NRT']["processed_time"] = p_time
                except Exception as e:
                    print('\nException occured in inferenceService:',e,'\n')
                    continue
            print("updated inference")
            st.write("updated inference data")

    def get_ota(self):
            with open(f"{self.outdir}/inference.log", "r", encoding="utf-8", errors="ignore") as file:
                log_content = file.readlines() 

                for i, line in enumerate(log_content):
                    try:
                        Session_id_match = re.search(config.get('sessionInfo', 'sessionIDSyncRef'), line)               
                        if Session_id_match:
                            session_id = Session_id_match.group(1)
                            next_20_lines = log_content[i + 1:i + 21]  
                            for sub_line in next_20_lines:
                                ota_match = re.search(config.get('sessionInfo', 'ota'), sub_line.strip())
                                if ota_match:
                                    ota = ota_match.group(1)
                                    self.session_ids[session_id]["ota_version"] = ota
                    except Exception as e:
                        print('\nException occured while fetching ota:',e,'\n')
                        continue      
                print("updated ota")
                st.write("updated ota version")

if __name__ == "__main__":

    details = argparser.arguments()
    # print (args.action)
    '''download logs '''
    # outdir = download_logs.download(details)
    # print(outdir)
    
    '''extract logs'''
    # e_status  = download_logs.extract_and_combine_logs(outdir)

    outdir = '3633090953/2024-03-15'
    session_obj = Session_details(outdir, details)
    for attribute_name, attribute_value in vars(Session_details).items():
        if callable(attribute_value) and attribute_name != "__init__":
                attribute_value(session_obj)

    mongodb.populate_db(session_obj.session_ids)
    mongodb.update_tracebacks(session_obj.tracebacks)



  



# previous 10 days data
#implement logger  





import sys
import streamlit as st
from pymongo import MongoClient 
from bson.objectid import ObjectId
from datetime import datetime, timedelta 

mongo_connectionStr = 'mongodb://10.200.10.181:27017/'
Mongo_db = 'Device_log_monitoring'
Mongo_tracebacks = 'Device_log_tracebacks'

client = MongoClient(mongo_connectionStr)  
db = client[Mongo_db]  

def mongodb_locked():
    collection = db['lock']
    document = collection.find_one({"_id": ObjectId("660ce78daf3d12e00e4d5e9d")})
    return int(document['upload_lock'])

def mongodb_setLock(lock):
    collection = db['lock']
    update_res = collection.update_one({"_id": ObjectId("660ce78daf3d12e00e4d5e9d")},{"$set": {"upload_lock": lock}})

def get_availableDates():
    collection = db[f"{st.session_state['ota_version']}_{st.session_state['deviceID']}"]
    unique_values = collection.distinct('date')
    return unique_values

def data_exists(details):
    collection_names = db.list_collection_names()
    # requested_collections[]
    flag = 0
    for collection_name in collection_names:
        if details['deviceid'] in collection_name:
            collection = db[collection_name]
            document = collection.find_one({'date': details['date']})
            if document:
                flag=1
                break
    return flag

def getAllCollections():
    collection_names = db.list_collection_names()
    device_ids = {}
    for name in collection_names:
        if name == 'lock':
            continue
        ota_version,device_id = name.split('_')
        if device_id in device_ids:
            device_ids[device_id].append(ota_version)
        else:
            device_ids[device_id] = [ota_version]
    return device_ids

def get_tracebacks():
    traceback_db = client[Mongo_tracebacks]
    # collection = traceback_db[st.session_state['deviceID']+'_'+st.session_state['date'].strftime('%Y-%m-%d')]
    collection = traceback_db[st.session_state['deviceID']+'_'+st.session_state['date']]
    document = collection.find_one({'device_ID': st.session_state['deviceID']})
    if not document:
        st.session_state
    return document

def get_data():  

    collection = db[f"{st.session_state['ota_version']}_{st.session_state['deviceID']}"]  
    # date_obj = datetime.combine(st.session_state['date'], datetime.min.time()) 
    # end_date = date_obj + timedelta(days=1)
    # query = {"device_ID": st.session_state['deviceID'], "ota_version": st.session_state['ota_version'], "start_time": {"$gte": date_obj, "$lt": end_date}}
    # query = {"device_ID": st.session_state['deviceID'], "ota_version": st.session_state['ota_version'], 'date': st.session_state['date'].strftime('%Y-%m-%d')}
    query = {"device_ID": st.session_state['deviceID'], "ota_version": st.session_state['ota_version'], 'date': st.session_state['date']}
    documents = collection.find(query)  
    document_count = collection.count_documents(query) 
    if document_count == 0:
        st.error("Requested data is not available")
        st.stop()
    return documents
 
def get_pieChart_data(documents):
    # print(documents)

    pieData = {
                'inwardClient':{
                                'obs_written':0, 
                                'events_detected':0,
                                'events_notProcessed':0
                               },
                'inwardAnalytics':{
                                  }, 
                'inwardNRT':{
                            'processing_status':0, 
                            'processing_time':0, 
                            'total_tracebacks':0, 
                            'summaryFile_status':0
                            }, 
                'outwardClient':{
                                'obs_written':0, 
                                'events_detected':0,
                                'events_notProcessed':0
                               },
                'outwardAnalytics':{
                                   }, 
                'outwardNRT':{
                            'processing_status':0, 
                            'processing_time':0,  
                            'summaryFile_status':0
                            }
              }
    total_documents = 0
    report = {'Missing_obsData_inwardClient':[], 
              'unprocessed_events_inwardClient':[], 
              'Missing_obsData_outwardClient':[],
              'unprocessed_events_outwardClient':[],
              "inward_sessionDrop":{}, #make sub columns 
              "outward_sessionDrop":{}, 
              "inwardNRT_unprocessed":[], 
              'Missing_sumaryFile_inwardNRT':[], 
              'traceback_inwardNRT':[], #[sessionID,traceback]
              "outwardNRT_unprocessed":[], 
              'Missing_sumaryFile_outwardNRT':[], 
              'traceback_outwardNRT':[] 
              }
    
    for document in documents:
        #Inward
        if document['inwardAnalyticsClient']['obs_data_written_status']:
            pieData['inwardClient']['obs_written']+=1
        else:
            report['Missing_obsData_inwardClient'].append(document['session_ID'])

        if document['inwardAnalyticsClient']['events_detected'] > -1:
            pieData['inwardClient']['events_detected']+=document['inwardAnalyticsClient']['events_detected']
        else:
            pieData['inwardClient']['events_notProcessed']+=1
            report['unprocessed_events_inwardClient'].append(document['session_ID'])
        
        if document['analyticsService']['Inward_session_drop']:
            failure_reason = document['analyticsService']['reason_for_inward_session_drop']
            if  failure_reason in pieData['inwardAnalytics'].keys():
                pieData['inwardAnalytics'][failure_reason]+=1
            else:
                pieData['inwardAnalytics'][failure_reason] = 1

            if  failure_reason in report['inward_sessionDrop']:
                report['inward_sessionDrop'][failure_reason].append(document['session_ID'])
            else:
                report['inward_sessionDrop'][failure_reason] = [document['session_ID']]
        
        pieData['inwardNRT']['total_tracebacks']+= document['inference']['traceback_count']
        pieData['inwardNRT']['processing_time']+= float(document['inference']['inward_NRT']['processed_time'])

        if document['inference']['inward_NRT']['inward_NRT_processing_status']:
            pieData['inwardNRT']['processing_status']+=1
        else:
            report['inwardNRT_unprocessed'].append(document['session_ID'])

        if document['inference']['inward_NRT']['summary_file_written_status']:
            pieData['inwardNRT']['summaryFile_status']+=1
        else:
            report['Missing_sumaryFile_inwardNRT'].append(document['session_ID'])
        
        if document['inference']['inward_NRT']['traceback'] != 'NA':
            report['traceback_inwardNRT'].append(document['inference']['inward_NRT']['traceback']+'\n'+document['session_ID'])

        #Outward
        if document['outwardAnalyticsClient']['obs_data_written_status']:
            pieData['outwardClient']['obs_written']+=1
        else:
            report['Missing_obsData_outwardClient'].append(document['session_ID'])

        if document['outwardAnalyticsClient']['events_detected'] > -1:
            pieData['outwardClient']['events_detected']+=document['outwardAnalyticsClient']['events_detected']
        else:
            pieData['outwardClient']['events_notProcessed']+=1
            report['unprocessed_events_outwardClient'].append(document['session_ID'])
        
        if document['analyticsService']['Outward session drop']:
            failure_reason = document['analyticsService']['reason_for_outward_session_drop']
            if  failure_reason in pieData['outwardAnalytics'].keys():
                pieData['outwardAnalytics'][failure_reason]+=1
            else:
                pieData['outwardAnalytics'][failure_reason] = 1
            
            if  failure_reason in report['outward_sessionDrop']:
                report['outward_sessionDrop'][failure_reason].append(document['session_ID'])
            else:
                report['outward_sessionDrop'][failure_reason] = [document['session_ID']]
        
        pieData['outwardNRT']['processing_time']+= float(document['inference']['outward_NRT']['processed_time'])

        if document['inference']['outward_NRT']['outward_NRT_processing_status']:
            pieData['outwardNRT']['processing_status']+=1
        else:
            report['outwardNRT_unprocessed'].append(document['session_ID'])

        if document['inference']['outward_NRT']['summary_file_written_status']:
            pieData['outwardNRT']['summaryFile_status']+=1
        else:
            report['Missing_sumaryFile_outwardNRT'].append(document['session_ID'])
        
        if document['inference']['outward_NRT']['traceback'] != 'NA':
            report['traceback_outwardNRT'].append(document['inference']['outward_NRT']['traceback']+'\n'+document['session_ID'])

        total_documents +=1
    
    return pieData, total_documents, report

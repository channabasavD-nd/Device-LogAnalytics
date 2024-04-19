from pymongo import MongoClient
import streamlit as st


mongo_connectionStr = 'mongodb://10.200.10.181:27017/'
Mongo_db = 'Device_log_monitoring'
Mongo_tracebacks = 'Device_log_tracebacks'

# def populate_db(session_stats):

# # #     # NOTE: Sessions with ota_version as None are getting ignored
# # #     # insert_one is too slow , find a way to use instert many

#     try :
#         client = MongoClient(mongo_connectionStr)
#         db = client[Mongo_db] 
#         for session_id in session_stats.keys():
#             if session_stats['_trip00c5_part004132_12.9829_77.7512_0.0_1710459210638_y']['ota_version']:
#                 collection = db[session_stats['_trip00c5_part004132_12.9829_77.7512_0.0_1710459210638_y']['ota_version']+"_"+session_stats['_trip00c5_part004132_12.9829_77.7512_0.0_1710459210638_y']['device_ID']] 
#                 collection.create_index([('_id', 1), ('start_time', 1)], unique=True)
#                 collection.insert_one(session_stats['_trip00c5_part004132_12.9829_77.7512_0.0_1710459210638_y'])
#         # print('Data successfully updated to mongodb')
#         st.write('Data successfully updated to mongodb')
#     except Exception as e:
#         print("Exception in mongoDB :",e)
         



def populate_db(session_stats):

    # NOTE: Sessions with ota_version as None are getting ignored
    # insert_one is too slow , find a way to use instert many

    try :
        client = MongoClient(mongo_connectionStr)
        db = client[Mongo_db]      
        documents = {}
        for session_id in session_stats.keys():
            if session_stats[session_id]['ota_version']:
                collection_name = session_stats[session_id]['ota_version'] + "_" + session_stats[session_id]['device_ID']
                if collection_name in documents:
                        documents[collection_name].append(session_stats[session_id])
                else:
                        documents[collection_name] = [session_stats[session_id]]
        for collection_name in documents.keys():
                collection = db[collection_name]
                collection.create_index([('_id', 1), ('date', 1), ('start_time', 1)], unique=True)
                res = collection.insert_many(documents[collection_name])
        st.write('Data successfully updated to mongodb')
    
    except Exception as e:
        st.error(f"Exception in mongoDB : {e}")
        print("Exception in mongoDB :",e)


def update_tracebacks(tracebacks):

    client = MongoClient(mongo_connectionStr)
    db = client[Mongo_tracebacks] 
    current_collection = tracebacks['device_ID']+'_'+tracebacks['date']
    if len(tracebacks['ndcentral'])+len(tracebacks['inwardAnalyticsClient'])+len(tracebacks['outwardAnalyticsClient'])+len(tracebacks['inertialAnalyticsClient'])+len(tracebacks['inferenceInertial'])+len(tracebacks['analyticsService'])+len(tracebacks['analyticsService'])+len(tracebacks['inference'])+len(tracebacks['audio'])+len(tracebacks['health'])+len(tracebacks['overspeedClient'])+len(tracebacks['reboot'])+len(tracebacks['scheduler']) > 0 :
        try:
            collection_names = db.list_collection_names()
            flag = 0
            for collection_name in collection_names:
                if collection_name == current_collection:
                    st.write('Tracebacks data already exixt')
                    flag = 1
                    break
            
            if not flag:
                collection = db[current_collection]
                collection.insert_one(tracebacks)
                st.write('Tracebacks data updated')

        except Exception as e:
            print("Exception in mongoDB :",e)
            st.error(e)
    else:
         st.info("No tracebacks found")



        

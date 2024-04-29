import sys
import streamlit as st

from db import data_exists, mongodb_locked, mongodb_setLock
sys.path.append('..')
from lib import mongodb
from utils import download_logs
import subprocess
from session_cronology_analysis import Session_details



st.markdown("<h1 style='text-align: center; color: white;'>Extract Log Analytics</h1>", unsafe_allow_html=True)

deviceID = st.text_input('Enter Device ID')
env = st.selectbox("Select Environment", ['Staging','Production']).lower()
date = st.date_input('Enter Date')  
device_type = st.selectbox("Select Device Type", ['Normal', 'DTS'])
date = date.strftime('%Y-%m-%d')

details = {}
details['deviceid'] = deviceID
st.session_state['upload_deviceID'] = deviceID
details['env'] = env
details['date'] = date
st.session_state['upload_date'] = date
details['deviceType'] = device_type
if st.button('Extract'):
    if not deviceID:
        st.info('deviceID field cannot be empty')
        st.stop()
    if mongodb_locked():
        st.warning("Another user is already uploading data. Please wait until the upload is complete.")
    else:
        exists = data_exists(details) 
        if not exists:
            success = False
            with st.status("Updating Data...", expanded=True) as status:
                try:
                    mongodb_setLock(lock = 1)
                
                    outdir = download_logs.download(details)
                    st.write('downloaded logs')
    
                    e_status  = download_logs.extract_and_combine_logs(outdir)
                    st.write('extracted logs')
    
                    # outdir = '103322300022/2024-04-22'
                    session_obj = Session_details(outdir, details)
                    for attribute_name, attribute_value in vars(Session_details).items():
                        if callable(attribute_value) and attribute_name != "__init__":
                                attribute_value(session_obj)
                    # st.write(session_obj.session_ids)
                    mongodb.populate_db(session_obj.session_ids)
                    mongodb.update_tracebacks(session_obj.tracebacks)
                    success = True
                    status.update(label="Successfully updated!", state="complete", expanded=False)
                except Exception as e:
                    st.error(e)
                    st.error('Try again with valid details')
                    status.update(label="Update Failed!", state="error", expanded=True)
                    st.stop()
                finally:
                    mongodb_setLock(lock = 0)
            if success:
                st.success("Data successfully updated")     
        else:
            st.info('Data already exists')
        
    

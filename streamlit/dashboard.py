import io
import numpy as np
import pandas as pd  
import streamlit as st  
import matplotlib.pyplot as plt
from db import get_pieChart_data


def pie_chart(label, data, explode):
    
    colors = ['#F3BD00','#0076A5', '#00B183', 'grey', 'red']
    wp = {'linewidth': 1, 'edgecolor': "black"}

    def func(pct):
        return "{:.1f}%".format(pct)

    fig, ax = plt.subplots(figsize=(6, 4))
    wedges, texts, autotexts = ax.pie(data,
                                    autopct=lambda pct: func(pct),
                                    explode=explode,
                                    labels=label,
                                    colors=colors,
                                    startangle=90,
                                    wedgeprops=wp,
                                    textprops=dict(color="black"))
    for i in range(len(label)):
        label[i] = label[i] + ' - ' + str(data[i])
    ax.legend(wedges, label,
            title="Labels",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1))
    for autotext, size in zip(autotexts, data):
        autotext.set_fontsize(max(6, int(10 * size / sum(data))))

    return fig

  
def display_dashboard(documents):  

    pieData,total_documents,report = get_pieChart_data(documents)
    print(pieData,total_documents)

    with st.expander("## Analytics Service"):
        col1, col2 = st.columns(2)
        with col1:
            inwardAnalytics_label = ['Processed']
            inwardAnalytics_data = [total_documents-sum(pieData['inwardAnalytics'].values())]
            for key in pieData['inwardAnalytics'].keys():
                if 'low power' in key :
                    inwardAnalytics_label.append('low power')
                    inwardAnalytics_data.append(pieData['inwardAnalytics'][key])
                elif "slowdown" in key:
                    inwardAnalytics_label.append('slow down')
                    inwardAnalytics_data.append(pieData['inwardAnalytics'][key])
                else:
                    inwardAnalytics_label.append(key)
                    inwardAnalytics_data.append(pieData['inwardAnalytics'][key])
            explode = [0.1]+[0]*(len(inwardAnalytics_data)-1)
            fig = pie_chart(inwardAnalytics_label, inwardAnalytics_data, explode)
            st.markdown("<h3 style='text-align: center; color: white;'>Inward analytics service</h3>", unsafe_allow_html=True)
            st.pyplot(fig)

        with col2:
            outwardAnalytics_label = ['Processed']
            outwardAnalytics_data = [total_documents-sum(pieData['outwardAnalytics'].values())]
            for key in pieData['outwardAnalytics'].keys():
                if 'low power' in key :
                    outwardAnalytics_label.append('low power')
                    outwardAnalytics_data.append(pieData['outwardAnalytics'][key])
                elif "slowdown" in key:
                    outwardAnalytics_label.append('slow down')
                    outwardAnalytics_data.append(pieData['outwardAnalytics'][key])
                else:
                    outwardAnalytics_label.append(key)
                    outwardAnalytics_data.append(pieData['outwardAnalytics'][key])
            explode = [0.1]+[0]*(len(outwardAnalytics_data)-1)
            fig = pie_chart(outwardAnalytics_label, outwardAnalytics_data, explode)
            st.markdown("<h3 style='text-align: center; color: white;'>Outward analytics service</h3>", unsafe_allow_html=True)
            st.pyplot(fig)

    with st.expander("## Analytics Client"):

        col1, col2 = st.columns(2)
        # Add content to the first column
        with col1:
            inwardClient_label = ['Obs data written', 'Obs data missing']
            inwardClient_data = [pieData['inwardClient']['obs_written'], total_documents-pieData['inwardClient']['obs_written']]
            explode = [0.1,0]         
            fig = pie_chart(inwardClient_label, inwardClient_data, explode)
            st.markdown("<h3 style='text-align: center; color: white;'>Inward analytics client</h3>", unsafe_allow_html=True)
            st.pyplot(fig)
            # st.markdown(f"<h5 style='text-align: left; color: white;'>Events detected : {pieData['inwardClient']['events_detected']}</h3>", unsafe_allow_html=True)
            # st.markdown(f"<h5 style='text-align: left; color: white;'>Events missing : {pieData['inwardClient']['events_notProcessed']}</h3>", unsafe_allow_html=True)

        with col2:
            outwardClient_label = ['Obs data written', 'Obs data missing']
            outwardClient_data = [pieData['outwardClient']['obs_written'], total_documents-pieData['outwardClient']['obs_written']]
            explode = [0.1,0]
            fig = pie_chart(outwardClient_label, outwardClient_data, explode)
            st.markdown("<h3 style='text-align: center; color: white;'>Outward analytics client</h3>", unsafe_allow_html=True)
            st.pyplot(fig)
            # st.markdown(f"<h5 style='text-align: left; color: white;'>Events detected : {pieData['outwardClient']['events_detected']}</h3>", unsafe_allow_html=True)
            # st.markdown(f"<h5 style='text-align: left; color: white;'>Events missing : {pieData['outwardClient']['events_notProcessed']}</h3>", unsafe_allow_html=True)

    with st.expander("## Inference"):

        col1, col2 = st.columns(2)
        with col1:
            inwardNRT_label = ['Successfully processed', 'Processing failed']
            inwardNRT_data = [pieData['inwardNRT']['processing_status'], total_documents-pieData['inwardNRT']['processing_status']]
            explode = [0.1,0]
            fig = pie_chart(inwardNRT_label, inwardNRT_data, explode)
            st.markdown("<h3 style='text-align: center; color: white;'>Inward NRT</h3>", unsafe_allow_html=True)
            st.pyplot(fig)
            st.markdown(f"<h5 style='text-align: left; color: white;'>Average processing time : {pieData['inwardNRT']['processing_time']/total_documents}</h5>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: left; color: white;'>Missing summary files : {total_documents-pieData['inwardNRT']['summaryFile_status']}</h5>", unsafe_allow_html=True)
        with col2:
            outwardNRT_label = ['Successfully processed', 'Processing failed']
            outwardNRT_data = [pieData['outwardNRT']['processing_status'], total_documents-pieData['outwardNRT']['processing_status']]
            explode = [0.1,0]
            fig = pie_chart(outwardNRT_label, outwardNRT_data, explode)
            st.markdown("<h3 style='text-align: center; color: white;'>Outward NRT</h3>", unsafe_allow_html=True)
            st.pyplot(fig)
            st.markdown(f"<h5 style='text-align: left; color: white;'>Average processing time : {pieData['outwardNRT']['processing_time']/total_documents}</h5>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: left; color: white;'>Missing summary files : {total_documents-pieData['outwardNRT']['summaryFile_status']}</h5>", unsafe_allow_html=True)
        st.markdown(f"<h5 style='text-align: left; color: white;'></h5>", unsafe_allow_html=True)
        st.markdown(f"<h5 style='text-align: left; color: white;'>Total tracebacks : {pieData['inwardNRT']['total_tracebacks']}</h5>", unsafe_allow_html=True)

    return report


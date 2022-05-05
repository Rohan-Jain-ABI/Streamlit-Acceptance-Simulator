# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 18:40:17 2022

@author: 40102892
"""

import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import json
import os
import ssl

#Feature Importance according to each model
bfq_rule_dict = {
    'Show Line Item level rank in Lot'                 : 4.09,
    'Can participants place bids during preview period': 3.40,
    'Can participants see ranks?'                      : 4.88,
    'Bidding period'                                   : 2.03,
    'Specify how lot bidding will begin and end'       : 1.29,
    'Bid rank that triggers overtime'                  : 1.85,
    'Enable traffic light bidding'                     : 1.46,
    'Start overtime if bid submitted within (minutes)' : 1.72,
    'Overtime period (minutes)'                        : 2.06,
    'Running time for the first lot'                   : 1.49,
    'Improve bid amount by'                            : 0.63,
    'Allow bidding overtime'                           : 0.01
}
bfq_rules = ['Show Line Item level rank in Lot','Can participants place bids during preview period','Can participants see ranks?','Bidding period',
'Specify how lot bidding will begin and end','Bid rank that triggers overtime','Enable traffic light bidding',
'Start overtime if bid submitted within (minutes)','Overtime period (minutes)',
'Running time for the first lot','Improve bid amount by','Allow bidding overtime']

nonbfq_rule_dict = {
    'Show Line Item level rank in Lot'                 : 4.61,
    'Can participants place bids during preview period': 3.05,
    'Can participants see ranks?'                      : 3.52,
    'Bidding period'                                   : 3.05,
    'Specify how lot bidding will begin and end'       : 2.23,
    'Bid rank that triggers overtime'                  : 2.69,
    'Enable traffic light bidding'                     : 1.46,
    'Start overtime if bid submitted within (minutes)' : 1.35,
    'Overtime period (minutes)'                        : 1.24,
    'Running time for the first lot'                   : 1.46,
    'Improve bid amount by'                            : 0.86,
    'Allow bidding overtime'                           : 0.11    
}
nonbfq_rules = ['Show Line Item level rank in Lot','Can participants place bids during preview period','Can participants see ranks?','Bidding period',
'Specify how lot bidding will begin and end','Bid rank that triggers overtime','Enable traffic light bidding',
'Start overtime if bid submitted within (minutes)','Overtime period (minutes)',
'Running time for the first lot','Improve bid amount by','Allow bidding overtime']

def scoring(combine,rules,rule_dict):
    combine['score'] = ['-']*combine.shape[0]
    max_score = 0
    my_score = 0
    overtime_rules = ['Bid rank that triggers overtime','Start overtime if bid submitted within (minutes)','Overtime period (minutes)']
    for x in range(combine.shape[0]):
        if combine.loc[x,'ID'] in rules:
            
            #Overtime Condition
            if (combine.loc[10,'Value_x'] == 'No') and (combine.loc[x,'ID'] in overtime_rules):
                continue
            
            #Parallel Condition
            if (combine.loc[4,'Value_x'] == 'Parallel') and (combine.loc[x,'ID'] == 'Running time for the first lot'):
                continue
            
            #Serial Condition
            if (combine.loc[4,'Value_x'] == 'Serial') and (combine.loc[x,'ID'] == 'Bidding period'):
                continue
            
            if (combine.loc[x,'Check']):
                combine.loc[x,'score'] = rule_dict[combine.loc[x,'ID']]
                my_score += rule_dict[combine.loc[x,'ID']]
            else:
                combine.loc[x,'score'] = 0
            max_score += rule_dict[combine.loc[x,'ID']]
    
    return my_score/max_score
    
    
                
            


currencies = ['CNY', 'CLP', 'CAD', 'BRL', 'GBP', 'AUD', 'GHC', 'COP', 'CHF', 'ARS', 'ETB', 'DZD', 'HKD', 'INR', 'BWP', 'CRC', 'HNL', 'CZK', 'DKK', 'BOB', 'HUF', 'AOA', 'EUR', 'DOP', 'GTQ', 'AED', 'NAD', 'KRW', 'SDP', 'RUB', 'JPY', 'MWK', 'LSL', 'MUR', 'MXN', 'MYR', 'UAH', 'NZD', 'PEN', 'KES', 'MAD', 'TZS', 'SZL', 'NGN', 'RWF', 'RON', 'PLN', 'TRY', 'PYG', 'MZN', 'SGD', 'USD', 'UGX', 'ZAR', 'VND', 'ZMW', 'ZMK', 'VEF', 'ZWD', 'UYU', 'NOK', 'SEK', 'ILS']
zone = st.selectbox('Zone',['AFR','APAC','EUR','MAZ','NAZ','SAZ'])
inv_suppl = st.number_input('Invited Suppliers',min_value = 0)
sup_nobid = st.number_input('Sellers Without Initial Bid',min_value = 0)
items = st.number_input('Total Items',min_value = 0)
commodity = st.selectbox('Commodity',['CAPEX','SIMPLE PACKAGES','COMMERCIAL','LOGISTICS','RAU','PACKAGING'])
currency = st.selectbox('Currency',currencies)

bfq = st.number_input('Best First Quote',min_value = 0)
bfq2 = st.number_input('Second Best First Quote',min_value = 0)
baseline = st.number_input('Baseline Spend',min_value = 0)

if (not bfq):
    bfq = -1

if (not bfq2):
    bfq2 = -1

upload = st.file_uploader("Upload Auction Edge Export Excel")
if upload is not None:
    try:
        ar = pd.read_excel(upload)
    except:
        st.warning("Upload excel file only")
        
#datet = '2021-07-21'        

if st.button('Check Acceptance'):
    data = {
    "Zone"                        : zone,
    "Invited Suppliers"           : inv_suppl ,
    "Sellers Without Initial Bid" : sup_nobid,
    "Total Items"                 : items,
    "Commodity"                   : commodity,
    "Currency"                    : currency,
    "Best First Quote"            : bfq,
    "Second Best First Quote"     : bfq2,
    "Baseline Spend"              : baseline,
    "Start time"                  : '2021-07-21'
    }


    body = str.encode(json.dumps(data))
    url = 'http://1fef65a9-6f8c-445c-b953-c468bac71793.westeurope.azurecontainer.io/score'
    api_key = 'Eevt90bBE4HN8Wqc0jmjuDWT0cTo1GRr' # Replace this with the API key for the web service
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}
    
    req = urllib.request.Request(url, body, headers)
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        ae = pd.DataFrame(eval(result))  
        
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        print(error.info())
        print(json.loads(error.read().decode("utf8", 'ignore')))
    
    combined = ar.merge(ae, on = 'ID')
    combined.loc[5,'Value_x'] = int(combined.loc[5,'Value_x'][:-8])
    combined.loc[6,'Value_x'] = int(combined.loc[6,'Value_x'][:-8])
    combined['Check'] = (combined['Value_x'] == combined['Value_y'])
    if bfq == -1:
        acc_score = scoring(combined,nonbfq_rules,nonbfq_rule_dict)
    else:
        acc_score = scoring(combined,bfq_rules,bfq_rule_dict)
    
    if acc_score < 0.3:
        st.write("Rejected : %1.2f"%(acc_score*100))
    elif 0.3 <= acc_score < 0.7:
        st.write('Partial : %1.2f'%(acc_score*100))
    else:
        st.write('Accepted : %1.2f'%(acc_score*100))
    
    combined.columns = ['Rules','User Rules','Recommended Rules','Do Rules Match','Score of Rule']
    st.table(combined.astype(str))
    
    
    
    
    

    

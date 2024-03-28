from os import name
import requests
import xml.etree.ElementTree as ET
from io import StringIO
import pandas as pd
import bs4
from lxml import html
from urllib.parse import urlencode, quote_plus, unquote

import state_of_seoul as ss

start_month = '201512'
end_month = '201601'

flag_month = start_month

row_list = [] 
name_list = [] 
value_list = [] 

for state in ss.selected_state:
    start_month = flag_month
    while int(start_month) <= int(end_month):
        url = 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev'
        params ={'serviceKey' : 'jesfgVDV9IppB3dFObXgUWZ1/4dWH6HbLSG3B8vUvqkbf4cgIx3qVfVLTb18ufbt0L4XAiIymIztsfrWak9Cpw==', 'pageNo' : '1', 'numOfRows' : '1000', 'LAWD_CD' : state, 'DEAL_YMD' : start_month}

        response = requests.get(url, params=params)
        contents = response.text

        tree = ET.parse(StringIO(contents))
        root = tree.getroot()

        xml_obj = bs4.BeautifulSoup(contents,'lxml-xml')
        rows = xml_obj.findAll('item')

        for i in range(0, len(rows)):
            columns = rows[i].find_all()
            for j in range(0,len(columns)):
                if i == 0 and state == ss.selected_state[0] and int(start_month) == int(flag_month):
                    name_list.append(columns[j].name)
                value_list.append(columns[j].text)
            row_list.append(value_list)
            value_list=[]

        year = int(start_month[:4])
        month = int(start_month[4:])

        if month >= 12:
            year += 1
            month = 1
        else:
            month += 1

        start_month = f"{year}{str(month).zfill(2)}"

real_estate_df = pd.DataFrame(row_list, columns=name_list)
print(real_estate_df)
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 10:12:05 2024

@author: wjtrk
"""



import requests
import pandas as pd
import numpy as np
import os
import xmltodict
from sqlalchemy import create_engine
import re
import time


base_direntory = os.getcwd()

## API 키 불러오기
file_path =  base_direntory+ "\\config.txt"

API_KEY=""
with open(file_path, 'r', encoding='utf-8') as file:
    API_KEY = file.read()

##법정동 코드리스트 만들기
file_path = base_direntory + "\\법정동코드 전체자료(서울)\\법정동코드 전체자료.csv"

df_code = pd.read_csv(file_path, encoding='cp949')
df_code = df_code['법정동코드\t법정동명\t폐지여부'].str.split('\t', expand=True)
    # 분리된 데이터프레임에 칼럼명 지정
df_code.columns = ['법정동코드', '법정동명', '폐지여부']

new_code = df_code['법정동코드'].str[:5]
new_si = df_code['법정동명'].str.split(' ', expand=True)[0]
new_gu = df_code['법정동명'].str.split(' ', expand=True)[1]

df_code = pd.DataFrame({'법정동코드':new_code, '시':new_si, '구':new_gu})
    #구가 None인 경우 제거, 시는 서울특별시만 추출, 중복 제거
df_code = df_code[(df_code['구'].notna()) & (df_code['시'] == '서울특별시')].drop_duplicates().reset_index(drop=True)

    # 결과를 dic으로 변환
code_dict = df_code.set_index('법정동코드')['구'].to_dict()

print(code_dict)

count = 0

def get_tradedata(month, code_dict, API_KEY, count):
    url = 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev'
        
    print(month)
    for i in range(0, len(code_dict)):
        count+= 1
    # 요청 파라미터
        params = {
            'serviceKey': API_KEY,
            'LAWD_CD': list(code_dict)[i],  # 지역코드, 예: 서울특별시 종로구
            'DEAL_YMD': month,  # 거래년월, 예: 2024년 1월
        }
        response = requests.get(url, params=params)
        
        
        res_json = xmltodict.parse(response.text)
        
        items = res_json['response']['body']['items']
        data = items['item']
        df = pd.DataFrame(data)
        
        if i == 0:
            df0 = df
        else:
            df0 = pd.concat([df0, df]).reset_index(drop=True)
        time.sleep(1)
    print(count)
    return df0, count
    #
    #
    
df1 = pd.read_csv(base_direntory + "\\origin_data.csv", encoding='utf-8-sig')

last_month = str(df1.loc[len(df1)-1, '년']) + str(df1.loc[len(df1)-1, '월']).zfill(2)

del df1['Unnamed: 0']

for Y in [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]:
    for M in ['01','02','03','04','05','06','07','08','09','10','11','12']:
        Gmonth = str(Y) + M
        if int(Gmonth) > int(last_month):
            if Y == 2024:
                if int(M) <= 2:
                    df0, count = get_tradedata(Gmonth, code_dict, API_KEY, count)
            else:
                
                df0, count = get_tradedata(Gmonth, code_dict, API_KEY, count)
                
            if Y == 2010 and M == "01":
                df1 = df0
            else:
                df1 = pd.concat([df1, df0]).reset_index(drop=True)
            


df1.to_csv(base_direntory + "\\origin_data.csv",  encoding='utf-8-sig')


    

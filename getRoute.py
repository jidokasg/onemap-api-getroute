#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import csv
import json
import requests

#Token - To re-write with code to request for new token every session - currently hardcoded
eToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjM5MzQsInVzZXJfaWQiOjM5MzQsImVtYWlsIjoia2VubnkudGd3QGdtYWlsLmNvbSIsImZvcmV2ZXIiOmZhbHNlLCJpc3MiOiJodHRwOlwvXC9vbTIuZGZlLm9uZW1hcC5zZ1wvYXBpXC92MlwvdXNlclwvc2Vzc2lvbiIsImlhdCI6MTU4MjcwNjM3NCwiZXhwIjoxNTgzMTM4Mzc0LCJuYmYiOjE1ODI3MDYzNzQsImp0aSI6ImFlZDg1ZjljYzZmYmM5ZjI0NjE1N2Y5MjI5NTA1NzhjIn0.7HcPC50d_z6c5aoc3Q88dMeIr1jJMHF-VZ47qOfDHH4"

#File path of start and end 6 digit postal code
filepath = r'C:\Users\\Kenny\Desktop\PostCode.csv'
df = pd.read_csv(filepath)

#build output dataframe
columns = ['date','apptime','startpoint','start_Lat','start_Lng','endpoint','end_Lat','end_Lng','transportMode','duration','total_distance','transfers','walkTime','transitTime','waitingTime','walkDistance']
output_df = pd.DataFrame(columns=columns)

#build dictionary to append
output_dict = dict.fromkeys(columns)

for i in range(df.shape[0]):

    #Function to get startpoint and endpoint coordinates 
    startPoint = requests.get("https://developers.onemap.sg/commonapi/search?searchVal=" + str(df['StartPoint'][i]) + "&returnGeom=Y&getAddrDetails=Y&pageNum=1")

    for key, value in startPoint.json().items():
        if key == 'results':
            start_Lat = value[0]['LATITUDE']
            start_Lng = value[0]['LONGITUDE']


    endPoint = requests.get("https://developers.onemap.sg/commonapi/search?searchVal=" + str(df['EndPoint'][i]) + "&returnGeom=Y&getAddrDetails=Y&pageNum=1")

    for key, value in endPoint.json().items():
        if key == 'results':
            end_Lat = value[0]['LATITUDE']
            end_Lng = value[0]['LONGITUDE']

            for mode in ['DRIVE', 'BUS','RAIL','TRANSIT']:
                if mode == 'DRIVE':
                ##Get route direction and details for driving
                    drive_response = requests.get("https://developers.onemap.sg/privateapi/routingsvc/route?start="+start_Lat+ ","+start_Lng+"&end=" + end_Lat + "," + end_Lng + "&routeType=drive&token=" + eToken)

                    for key,value in drive_response.json().items():
                        if key == 'route_summary':
                            start_point = value['start_point']
                            end_point = value['end_point']
                            duration = value['total_time']
                            total_distance = value['total_distance']

                            output_dict['date'] = df['Date'][0]
                            output_dict['apptime'] = df['AppTime'][0] 
                            output_dict['startpoint'] = start_point
                            output_dict['start_Lat'] = start_Lat
                            output_dict['start_Lng'] = start_Lng
                            output_dict['endpoint'] = end_point
                            output_dict['end_Lat'] = end_Lat
                            output_dict['end_Lng'] = end_Lng
                            output_dict['transportMode'] = mode
                            output_dict['duration'] = duration
                            output_dict['total_distance'] = total_distance
                            output_dict['transfers'] = None
                            output_dict['walkTime'] = None
                            output_dict['transitTime'] = None
                            output_dict['waitingTime'] = None
                            output_dict['walkDistance'] = None

                            output_df = output_df.append(output_dict, ignore_index= True)

                else:
                    ##Get Route Direction and details for public transport (pt) 
                    pt_response = requests.get("https://developers.onemap.sg/privateapi/routingsvc/route?start="+start_Lat+ ","+start_Lng+"&end=" + end_Lat + "," + end_Lng + "&routeType=pt&token=" + eToken + "&date=" + df['Date'][i] +"&time=" + df['AppTime'][i] + "&mode=" + mode +"&numItineraries=1")
                    for x,y in pt_response.json().items():
                        if x == 'plan':

                            duration = y['itineraries'][0]['duration']
                            startTime = y['itineraries'][0]['startTime']
                            endTime = y['itineraries'][0]['endTime']
                            walkTime = y['itineraries'][0]['walkTime']
                            transitTime = y['itineraries'][0]['transitTime']
                            waitingTime = y['itineraries'][0]['waitingTime']
                            walkDistance = y['itineraries'][0]['walkDistance']
                            transfers = y['itineraries'][0]['transfers']

                            output_dict['date'] = df['Date'][i]
                            output_dict['apptime'] = df['AppTime'][i] 
                            output_dict['startpoint'] = start_point
                            output_dict['start_Lat'] = start_Lat
                            output_dict['start_Lng'] = start_Lng
                            output_dict['endpoint'] = end_point
                            output_dict['end_Lat'] = end_Lat
                            output_dict['end_Lng'] = end_Lng
                            output_dict['transportMode'] = mode
                            output_dict['duration'] = duration
                            output_dict['total_distance'] = total_distance
                            output_dict['transfers'] = transfers
                            output_dict['walkTime'] = walkTime
                            output_dict['transitTime'] = transitTime
                            output_dict['waitingTime'] = waitingTime
                            output_dict['walkDistance'] = walkDistance

                            output_df = output_df.append(output_dict, ignore_index= True)

###Rename to desired destination path and filename
output_df.to_csv(r'C:\Users\kenny\desktop\output.csv')


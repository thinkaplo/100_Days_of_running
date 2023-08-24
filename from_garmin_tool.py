# ________________________________________________Import packages, modules and constants definition
import csv
import pandas as pd 

GARMIN_EPOCH = 631065600                                                                    # Garmin epoch starts in
TO_DEGREES = 180/(2**31)                                                                    # Degrees = semicircles * ( 180 / 2^31 )
TO_KMH = 3.6                                                                               # Conversion rate of m/s to Km/h

# ________________________________________________Create name list to convert into dataframes.
names_txt = []
list_of_names = []

with open('file_names.txt','r') as file:
    reader = csv.reader(file,delimiter=' ')
    for i in reader:
        names_txt.append(i)

for i in names_txt:
    pairs = [j for j in range(0,len(i)) if j % 2 == 0]
    for k in pairs:
        list_of_names.append(i[k])

# ________________________________________________Create dataframes for historic and daily data.
historic_data = pd.DataFrame(columns = ['Date','Timestamp','Latitude','Longitude','Distance','Altitude','Speed','Heart_rate'])
daily_data = pd.DataFrame(columns = ['Date','Timestamp','Latitude','Longitude','Distance','Altitude','Speed','Heart_rate'])

# ________________________________________________Populate daily data csv to a dataframe.
for i in list_of_names:
    file = pd.read_csv(f"csv_files/{i}", low_memory=False, dtype=str)
    file = file.loc[:,['Type','Value 1','Field 2','Value 2','Value 3','Value 4','Value 5','Value 6','Value 7']]
    
    if 'Run' in file['Value 1'].values:
        filter_positions = file['Field 2'] == 'position_lat'
        filter_type = file['Type'] == 'Definition'

        file = file[filter_positions & ~filter_type]

        file['Value 1'] = file['Value 1'].astype('int64')
        file['Value 2'] = file['Value 2'].astype('int64')
        file['Value 3'] = file['Value 3'].astype('int64')
        file['Value 4'] = file['Value 4'].astype('float64')
        file['Value 5'] = file['Value 5'].astype('float64')
        file['Value 6'] = file['Value 6'].astype('float64')
        file['Value 7'] = file['Value 7'].astype('float64')

        daily_data['Timestamp'] = file.loc[:,'Value 1'] + GARMIN_EPOCH
        daily_data['Latitude'] = file.loc[:,'Value 2'] * TO_DEGREES
        daily_data['Longitude'] = file.loc[:,'Value 3'] * TO_DEGREES
        daily_data['Distance'] = file.loc[:,'Value 4']
        daily_data['Altitude'] = file.loc[:,'Value 5']
        daily_data['Speed'] = file.loc[:,'Value 6'] * TO_KMH
        daily_data['Heart_rate'] = file.loc[:,'Value 7']
        daily_data['Date'] = pd.to_datetime(daily_data.loc[:,'Timestamp'],unit='s')

    # ________________________________________________Populate daily data dataframe to history dataframe.
        historic_data = pd.concat([historic_data,daily_data],ignore_index=True)
        daily_data.drop(daily_data.index,inplace=True)

    # ________________________________________________Export data to a csv file.
historic_data.to_csv('historic_data.csv',index=False)

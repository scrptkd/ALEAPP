__artifacts_v2__ = {
    "Turbo_Battery": {
        "name": "Turbo_Battery",
        "description": "Parses battery percentage for device and bluetooth connected devices",
        "author": "@KevinPagano3",
        "version": "0.0.1",
        "date": "2021-06-29",
        "requirements": "none",
        "category": "Device Health Services",
        "notes": "",
        "paths": ('*/com.google.android.apps.turbo/databases/turbo.db*','*/com.google.android.apps.turbo/databases/bluetooth.db*'),
        "function": "get_Turbo_Battery"
    }
}

import sqlite3
import textwrap

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_Turbo_Battery(files_found, report_folder, seeker, wrap_text):
    
    source_file_bluetooth = ''
    source_file_turbo = ''
    bluetooth_db = ''
    turbo_db = ''
    data_list_battery = []
    data_list_bluetooth = []
        
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.lower().endswith('turbo.db'):
            turbo_db = str(file_found)
            source_file_turbo = file_found.replace(seeker.data_folder, '')
           
            db = open_sqlite_db_readonly(turbo_db)
            cursor = db.cursor()
            cursor.execute('''
            select
            case timestamp_millis
                when 0 then ''
                else datetime(timestamp_millis/1000,'unixepoch')
            End as D_T,
            battery_level,
            case charge_type
                when 0 then ''
                when 1 then 'Charging Rapidly'
                when 2 then 'Charging Slowly'
                when 3 then 'Charging Wirelessly'
            End as C_Type,
            case battery_saver
                when 2 then ''
                when 1 then 'Enabled'
            End as B_Saver,
            timezone
            from battery_event
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    timestamp = row[0]
                    if timestamp is None:
                        pass
                    else:
                        timestamp = convert_utc_human_to_timezone(convert_ts_human_to_utc(timestamp),'UTC')
                    data_list_battery.append((timestamp,row[1],row[2],row[3],row[4],file_found))
            
            db.close()

        if file_found.lower().endswith('bluetooth.db'):
            bluetooth_db = str(file_found)
            source_file_bluetooth = file_found.replace(seeker.data_folder, '')
           
            db = open_sqlite_db_readonly(bluetooth_db)
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(timestamp_millis/1000,'unixepoch'),
            bd_addr,
            device_identifier,
            battery_level,
            volume_level,
            time_zone
            from battery_event
            join device_address on battery_event.device_idx = device_address.device_idx
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    timestamp = row[0]
                    if timestamp is None:
                        pass
                    else:
                        timestamp = convert_utc_human_to_timezone(convert_ts_human_to_utc(timestamp),'UTC')
                    data_list_bluetooth.append((timestamp,row[1],row[2],row[3],row[4],row[5],file_found))
            db.close()
    
        else:
            continue # Skip all other files
            
    if data_list_battery:    
        report = ArtifactHtmlReport('Turbo - Phone Battery')
        report.start_artifact_report(report_folder, 'Turbo - Phone Battery')
        report.add_script()
        data_headers = ('Timestamp','Battery Level','Charge Type','Battery Saver','Timezone','Source') # Don't remove the comma, that is required to make this a tuple as there is only 1 element

        report.write_artifact_data_table(data_headers, data_list_battery, source_file_turbo)
        report.end_artifact_report()
        
        tsvname = f'Turbo - Phone Battery'
        tsv(report_folder, data_headers, data_list_battery, tsvname)
        
        tlactivity = f'Turbo - Phone Battery'
        timeline(report_folder, tlactivity, data_list_battery, data_headers)
    else:
        logfunc('No Turbo - Phone Battery data available')
    
    if data_list_bluetooth:
        report = ArtifactHtmlReport('Turbo - Bluetooth Device Info')
        report.start_artifact_report(report_folder, 'Turbo - Bluetooth Device Info')
        report.add_script()
        data_headers = ('Timestamp','BT Device MAC Address','BT Device ID','Battery Level','Volume Level','Timezone','Source') # Don't remove the comma, that is required to make this a tuple as there is only 1 element

        report.write_artifact_data_table(data_headers, data_list_bluetooth, source_file_bluetooth)
        report.end_artifact_report()
        
        tsvname = f'Turbo - Bluetooth Device Info'
        tsv(report_folder, data_headers, data_list_bluetooth, tsvname)
        
        tlactivity = f'Turbo - Bluetooth Device Info'
        timeline(report_folder, tlactivity, data_list_bluetooth, data_headers)
    else:
        logfunc('No Turbo - Bluetooth Device Info data available')
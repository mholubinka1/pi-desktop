#!/usr/bin/env python3

import argparse
import datetime
import os
import re
import sys
import time

from constants import INFLUX_HOST, INFLUX_PORT, INFLUX_USER, INFLUX_PWD
from influxdb import InfluxDBClient

SAMPLING_PERIOD = 10

def get_cpu_temp():
    result = os.popen("vcgencmd measure_temp").readline()
    return (float)(result.replace("temp=", "").replace("'C\n",""))

def get_cpu_use():
    return (float)(os.popen("top -b -n1 | grep 'Cpu(s)' | awk '{print $2 + $4}'").readline().strip())

# Index 0: total RAM
# Index 1: used RAM
# Index 2: free RAM
def get_ram_info():
    p = os.popen("free")
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i == 2:
            return (line.split()[1:4])
        
def get_disk_space():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i == 2:
            return (line.split()[1:5])
        
def get_args():        
    parser = argparse.ArgumentParser(description='Script writes monitoring data to specified Influx database.')
    parser.add_argument(
        '-db','--database', type=str, help='Database Name', required=True
    )
    parser.add_argument(
        '-p','--policy', type=str, help='Retention Policy Name', required=True
    )
    time = datetime.datetime.now()
    parser.add_argument(
        '-r','--run', type=str, help='Run Number', required=False, default=time.strftime("%Y%m%d%H%M")
    )
    args=parser.parse_args()
    database=args.database
    run = args.run
    policy = args.policy
    return database, run, policy

def get_data_points():
    cpu_use = get_cpu_use()
    cpu_temp = get_cpu_temp()
    ram_used_raw = float(get_ram_info()[1]) + 64 * 1024
    ram_used_percent = int((ram_used_raw / float(get_ram_info()[0])) * 100)
    timestamp=datetime.datetime.utcnow().isoformat()

    # Create InfluxDB data points (using lineprotocol as of Influxdb >1.1)
    datapoints = [
        {
            'measurement': policy,
            'tags': {'run': run,
            },
            'time': timestamp,
            'fields': {
                'cpu_use': cpu_use,
                'cpu_temp': cpu_temp,
                'ram_used_percent': ram_used_percent
            }
        }
    ]
    return datapoints

db, run, policy = get_args()

client = InfluxDBClient(INFLUX_HOST, INFLUX_PORT, INFLUX_USER, INFLUX_PWD, db)
try:
    for x in range(1, 6):
        datapoints=get_data_points()
        bResult=client.write_points(datapoints)
        print('Write points {0} Bresult:{1}'.format(datapoints,bResult))
        time.sleep(SAMPLING_PERIOD)
except KeyboardInterrupt:
    print ('Monitoring script stopped by keyboard interrupt [CTRL_C].')
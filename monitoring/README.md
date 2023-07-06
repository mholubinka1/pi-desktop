# Monitoring

## **InfluxDB**

### **1. Installation**

To install the service, it is necessary to add InfluxDB's authentication key, add the repository to trusted sources, and then install it via ```apt```:

``wget -qO- https://repos.influxdata.com/influxdata-archive_compat.key | sudo apt-key add -``

``source /etc/os-release``

The repository depends on which distribution is running on the Raspberry Pi, this can be found with the following command under the 'Codename' section:

``lsb_release -irdc``

Then replace $codename in the next command with the value found above to add the repository to trusted sources:

``echo "deb https://repos.influxdata.com/debian $codename stable" | sudo tee /etc/apt/sources.list.d/influxdb.list``

Installing InfluxDB is then as simple as running

``sudo apt update && sudo apt install influxdb``

When executing the ``sudo apt update`` command, the following error may occur:

``The following signatures couldn't be verified because the public key is not available: NO_PUBKEY``

In order to fix this, run this command, where $pubkey is the key given in the error message and then run the installation commands again.

``sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $pubkey``

Once the installation command has finished, check the installation completed successfully and the version with:

``influx --version``

### **2. Configuration**

#### **2.1. Change Storage Location**

Given the monitoring stack will be performing many write and delete operations to the SD Card, it is best to store the InfluxDB data on an external drive to avoid rapid degradation of the SD Card.

The method for changing the storage location given below only works for **InfluxDB v1.x.x**, if the version installed is **InfluxDB v2.x.x** please follow the instructions given in [this forum post](https://community.influxdata.com/t/influxdb-2-0-moving-database/20452).

First, make a new directory,

``mkdir /mnt/pi-media/monitoring/influxdb``

And set the correct permissions,

``sudo chown influxdb:influxdb /mnt/pi-media/monitoring/influxdb``

Next, edit the following **three** lines of ``/etc/influxdb/influxdb.conf`` so that the configuration file is pointing to the new location:

``sudo nano /etc/influxdb/influxdb.conf``
    
    [meta]
    dir = "/mnt/pi-media/monitoring/influxdb/meta"

    [data]
    dir = "/mnt/pi-media/monitoring/influxdb/data"
    wal-dir = "/mnt/pi-media/monitoring/influxdb/wal"

Point the process to this configuration file:

``influxd -config /etc/influxdb/influxdb.conf``

#### **2.2. Enable Autostart**

Since the service will be continuously collecting metrics via different data sources (Telegraf, custom Python scripts and Docker containers), it needs to start on reboot to ensure that there is always a location to write the data to.

First, ``unmask`` InfluxDB whichs enables it to be added as a service and then tell the system to start the service both now and every time it restarts.

``sudo systemctl unmask influxdb && sudo systemctl enable --now influxdb``

If the storage location was configured incorrectly above and the **data** and **WAL** directories are not writeable, the service will not start.

#### **2.3. Configure Authentication and HTTP Access**

It now probably healthy to add authentication to the InfluxDB instance, especially if the system is exposed to external networks. A basic ``admin`` account can be created easily. First, start the shell with:

``influx -precision rfc3339``

And then create the user, replacing ``$password`` with a secure password:

``CREATE USER admin WITH PASSWORD '$password' WITH ALL PRIVILEGES``

To exit the shell:

``exit``

Now perform the basic configuration to enable other services to communicate with the InfluxDB instance over HTTP with authentication.

Open the configuration file again:

``sudo nano /etc/influxdb/influxdb.conf``

Uncomment the following **six** lines to enable HTTP communication, configure the port and disable authentication:

    [http]
    enabled = true
    bind-address = ":8086"
    auth-enabled = true
    pprof-enabled = true
    pprof-auth-enabled = true
    ping-auth-enabled = true

Now, restart the service to allow for the changes to take effect:

``sudo service influxdb start``

And confirm everything is working:

``influx -precision rfc3339``

This should connect to the HTTP instance configured above and open the Influx shell. 

In order to work with InfluxDB it is necessary to make sure that the service is started and the shell is connected.

#### **2.4. Create Database/s**

Given the data collected is going to be a time series, it is prudent to configure retention policies (which are best considered as databases themselves) so that the volume of the data being stored does not increase to infinity over time. Unfortunately there is no way to set a default duration for a retention policy via the configuration in InfluxDB: retention policy durations are typically defined during their creation.

First create a database which will store all monitoring data and at the same time define a retention policy for the data which will be collected from the custom Python script:

``CREATE DATABASE monitoring WITH DURATION 7d REPLICATION 1 NAME python_ts``

This command creates our database ``monitoring`` and then defines the first retention policy ``python_ts`` which will store time series data for a duration of seven days.

**Create A New Policy**

``CREATE RETENTION POLICY telegraf ON monitoring DURATION 7d REPLICATION 1``

**Update Existing Policy**

``ALTER RETENTION POLICY speedtest ON monitoring DURATION 4w REPLICATION 1``

## **Custom Monitoring Script**

The customer monitoring script retrieves CPU tempeature, CPU usage and an accurate picture of RAM used (understanding that the GPU uses some of the RAM available).

Navigate to the folder containing the monitoring scripts and make the python script executable for testing:

``chmod u+x ./custom.py``

Create a new python file in the same folder called ``constants.py`` and add the following configuration variables to it:

    INFLUX_HOST = "localhost"
    INFLUX_PORT = 8086
    INFLUX_USER = "admin"
    INFLUX_PWD = "$password"
    INFLUX_DB = "monitoring"

And add the correct database and retention policy to the shell script ``run_custom_monitor.sh``

    -db=monitoring -p=custom_ts

Make the shell script executable:

``chmod +x run_custom_monitor.sh``

Finally, make the shell script a cron job

``crontab -e``

Select ``/bin/nano`` as the preferred editor and add the following line to the file so that the script executes every minute:

``* * * * * /home/pi/git/pi-desktop/monitoring/run_custom_monitor.sh``

By default the 

## **Grafana**

Before integrating any additional data sources to the monitoring systems, it is sensible to test the current set up with Grafana to ensure data is being written and can be read for dashboarding purposes.

**Do not attempt to simply ``sudo apt install grafana``!** The main repository contained an outdated version of Grafana which will display a blank screen on log in.

Instead install Grafana via ``dpkg``. First check for the most recent version on the [Grafana downloads page](https://grafana.com/grafana/download), replace the version number in the commands below with the most recent version on the downloads page. Remember that the ARMv7 version is required for the Raspberry Pi 4.

First ensure required dependencies are installed:

``sudo apt-get install -y adduser libfontconfig1``

Download the Grafana OSS package (with the current version as found on the downloads page):

``wget https://dl.grafana.com/oss/release/grafana_10.0.1_armhf.deb``

Once the package has downloaded, install it:

``sudo dpkg -i grafana_10.0.1_armhf.deb``

For completeness, delete the downloaded package to avoid cluttering the internal storage unnecessarily:

``rm grafana_10.0.1_armhf.deb``

Grafana can be managed almost entirely from a web UI, so start the service now and on boot with a similar to that which was used for InfluxDB:

``sudo systemctl enable --now grafana-server``

The default web page to access the service is ``localhost:3000`` if the Raspberry Pi has a static IP then it can be accessed from another machine as well.

Configure InfluxDB as a data source ensuring to toggle _Basic Auth_ and logging in with the credentials specified earlier.

## **Telegraf**

With confirmation that InfluxDB is running, data being written to the correct retention policy and that data is accessible through Grafana, it is time to ramp up the monitoring capabilities, which means installing and configuring Telegraf. Again this installation will be via `dpkg`, so confirm the most recent version on [the releases page](https://portal.influxdata.com/downloads/).

``wget https://dl.influxdata.com/telegraf/releases/telegraf_1.27.1-1_armhf.deb``

Then install via `dpkg`:

``sudo dpkg -i telegraf_1.27.1-1_armhf.deb``

Once completed, delete the downloaded package.

``rm telegraf_1.27.1-1_armhf.deb``

Enable and start the service as before:

``sudo systemctl enable --now telegraf``

The service start will likely fail, this is due to the configuration file not providing any outputs.

``sudo nano /etc/telegraf/telegraf.conf``

A sample configuration file is provided, once a valid config is supplied the service will start and begin collecting data into InfluxDB. Telegraf operates by co-ordinating a collection of _plugins_ which collect and write data to and from a variety of sources. A full list of plugins is available on [the github repository](https://github.com/influxdata/telegraf/tree/master/plugins). 

Unfortunately, Telegraf's native plugin to measure system temperature is incompatible with Raspberry Pi systems. Earlier, however, a custom collection script was configured to get around this issue.

## Put It All Together

Everything is now in place to gather detailed real time metrics about the Raspberry Pi. It is now simply a matter of playing around with Grafana and building the perfect dashboard.
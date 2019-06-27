# Databricks notebook source
dbutils.widgets.text("infilefolder", "", "In - Folder Path")
infilefolder = dbutils.widgets.get("infilefolder")

dbutils.widgets.text("loadid", "", "Load Id")
loadid = dbutils.widgets.get("loadid")

# COMMAND ----------

import datetime

# For testing
# infilefolder = 'datalake/data/lnd/2019_03_11_01_38_00/'
load_id = loadid
loaded_on = datetime.datetime.now()
base_path = 'dbfs:/mnt/datalake/data/lnd/'
parkingbay_filepath = base_path + infilefolder + "/MelbParkingBayData.json"
sensors_filepath = base_path + infilefolder + "/MelbParkingSensorData.json"

# COMMAND ----------

import ddo_transform.standardize as s

# Read data
parkingbay_sdf = spark.read.json(parkingbay_filepath, multiLine=True)
sensordata_sdf = spark.read.json(sensors_filepath, multiLine=True)

# Standardize
t_parkingbay_sdf = s.standardize_parking_bay(parkingbay_sdf, load_id, loaded_on)
t_sensordata_sdf = s.standardize_sensordata(sensordata_sdf, load_id, loaded_on)

# Insert new rows
t_parkingbay_sdf.write.mode("append").insertInto("interim.parking_bay")
t_sensordata_sdf.write.mode("append").insertInto("interim.sensor")

# COMMAND ----------


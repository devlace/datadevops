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

import ddo_transform.ddo_transform as t

# Read data
parkingbay_sdf = spark.read.json(parkingbay_filepath, multiLine=True)
sensordata_sdf = spark.read.json(sensors_filepath, multiLine=True)

# Dimensions
dim_parkingbay_sdf = spark.read.table("dim_parking_bay")
dim_location_sdf = spark.read.table("dim_location")
dim_st_marker = spark.read.table("dim_st_marker")
fact_parking = spark.read.table("fact_parking")

# Process
nr_parkingbay_sdf = t.process_dim_parking_bay(parkingbay_sdf, dim_parkingbay_sdf, load_id, loaded_on)
nr_location_sdf = t.process_dim_location(sensordata_sdf, dim_location_sdf, load_id, loaded_on)
nr_st_marker_sdf = t.process_dim_st_marker(sensordata_sdf, dim_st_marker, load_id, loaded_on)

# Insert new rows
nr_parkingbay_sdf.write.mode("append").insertInto("dim_parking_bay")
nr_location_sdf.write.mode("append").insertInto("dim_location")
nr_st_marker_sdf.write.mode("append").insertInto("dim_st_marker")

# COMMAND ----------

# Read data
parkingbay_sdf = spark.read.json(parkingbay_filepath, multiLine=True)
sensordata_sdf = spark.read.json(sensors_filepath, multiLine=True)

# Read in Dims and Facts
dim_parkingbay_sdf = spark.read.table("dim_parking_bay")
dim_location_sdf = spark.read.table("dim_location")
dim_st_marker = spark.read.table("dim_st_marker")
fact_parking = spark.read.table("fact_parking")

# Process
nr_fact_parking = t.process_fact_parking(sensordata_sdf, dim_parkingbay_sdf, dim_location_sdf, dim_st_marker, load_id, loaded_on)

# Insert new rows
nr_fact_parking.write.mode("append").insertInto("fact_parking")


# COMMAND ----------

dbutils.notebook.exit("success")
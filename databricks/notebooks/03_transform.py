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

import ddo_transform.transform as t

# Read interim cleansed data
parkingbay_sdf = spark.read.table("interim.parking_bay")
sensordata_sdf = spark.read.table("interim.sensor")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Transform and load Dimension tables

# COMMAND ----------

# Read existing Dimensions
dim_parkingbay_sdf = spark.read.table("dw.dim_parking_bay")
dim_location_sdf = spark.read.table("dw.dim_location")
dim_st_marker = spark.read.table("dw.dim_st_marker")

# Transform
new_dim_parkingbay_sdf = t.process_dim_parking_bay(parkingbay_sdf, dim_parkingbay_sdf, load_id, loaded_on).cache()
new_dim_location_sdf = t.process_dim_location(sensordata_sdf, dim_location_sdf, load_id, loaded_on).cache()
new_dim_st_marker_sdf = t.process_dim_st_marker(sensordata_sdf, dim_st_marker, load_id, loaded_on).cache()

# Load
new_dim_parkingbay_sdf.write.mode("overwrite").insertInto("dw.dim_parking_bay")
new_dim_location_sdf.write.mode("overwrite").insertInto("dw.dim_location")
new_dim_st_marker_sdf.write.mode("overwrite").insertInto("dw.dim_st_marker")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Transform and load Fact tables

# COMMAND ----------

# Read data
sensordata_sdf = spark.read.table("interim.sensor")

# Process
nr_fact_parking = t.process_fact_parking(sensordata_sdf, new_dim_parkingbay_sdf, new_dim_location_sdf, new_dim_st_marker_sdf, load_id, loaded_on)

# Insert new rows
nr_fact_parking.write.mode("append").insertInto("dw.fact_parking")

# COMMAND ----------

dbutils.notebook.exit("success")

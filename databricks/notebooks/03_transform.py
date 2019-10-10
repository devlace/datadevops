# Databricks notebook source
dbutils.widgets.text("infilefolder", "", "In - Folder Path")
infilefolder = dbutils.widgets.get("infilefolder")

dbutils.widgets.text("loadid", "", "Load Id")
loadid = dbutils.widgets.get("loadid")

# COMMAND ----------

import datetime
import os

# For testing
# infilefolder = 'datalake/data/lnd/2019_03_11_01_38_00/'
load_id = loadid
loaded_on = datetime.datetime.now()
base_path = 'dbfs:/mnt/datalake/data/dw/'

# COMMAND ----------

from pyspark.sql.functions import col, lit
import ddo_transform.transform as t
import ddo_transform.util as util

# Read interim cleansed data
parkingbay_sdf = spark.read.table("interim.parking_bay").filter(col('load_id') == lit(load_id))
sensordata_sdf = spark.read.table("interim.sensor").filter(col('load_id') == lit(load_id))

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
util.save_overwrite_unmanaged_table(spark, new_dim_parkingbay_sdf, table_name="dw.dim_parking_bay", path=os.path.join(base_path, "dim_parking_bay"))
util.save_overwrite_unmanaged_table(spark, new_dim_location_sdf, table_name="dw.dim_location", path=os.path.join(base_path, "dim_location"))
util.save_overwrite_unmanaged_table(spark, new_dim_st_marker_sdf, table_name="dw.dim_st_marker", path=os.path.join(base_path, "dim_st_marker"))

# new_dim_parkingbay_sdf.write.mode("overwrite").saveAsTable("dw.dim_parking_bay_temp")
# new_dim_location_sdf.write.mode("overwrite").saveAsTable("dw.dim_location_temp")
# new_dim_st_marker_sdf.write.mode("overwrite").saveAsTable("dw.dim_st_marker_temp")
# spark.read.table("dw.dim_parking_bay_temp").write.mode("overwrite").option("path", os.path.join(base_path, "dim_parking_bay")).saveAsTable("dw.dim_parking_bay")
# spark.read.table("dw.dim_location_temp").write.mode("overwrite").option("path", os.path.join(base_path, "dim_location")).saveAsTable("dw.dim_location")
# spark.read.table("dw.dim_st_marker_temp").write.mode("overwrite").option("path", os.path.join(base_path, "dim_st_marker")).saveAsTable("dw.dim_st_marker")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Transform and load Fact tables

# COMMAND ----------

# Read existing Dimensions
dim_parkingbay_sdf = spark.read.table("dw.dim_parking_bay")
dim_location_sdf = spark.read.table("dw.dim_location")
dim_st_marker = spark.read.table("dw.dim_st_marker")

# Process
nr_fact_parking = t.process_fact_parking(sensordata_sdf, dim_parkingbay_sdf, dim_location_sdf, dim_st_marker, load_id, loaded_on)

# Insert new rows
nr_fact_parking.write.mode("append").insertInto("dw.fact_parking")

# COMMAND ----------

dbutils.notebook.exit("success")

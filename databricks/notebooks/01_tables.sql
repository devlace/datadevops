-- Databricks notebook source
DROP TABLE IF EXISTS fact_parking;
DROP TABLE IF EXISTS dim_st_marker;
DROP TABLE IF EXISTS dim_location;
DROP TABLE IF EXISTS dim_parking_bay;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_time;

-- COMMAND ----------

CREATE TABLE fact_parking (
  dim_date_id STRING,
  dim_time_id STRING,
  dim_parking_bay_id STRING,
  dim_location_id STRING,
  dim_st_marker_id STRING,
  status STRING,
  load_id STRING,
  loaded_on TIMESTAMP
)
USING delta

-- COMMAND ----------

CREATE TABLE dim_st_marker (
  dim_st_marker_id STRING,
  st_marker_id STRING,
  load_id STRING,
  loaded_on TIMESTAMP
)
USING delta

-- COMMAND ----------

CREATE TABLE dim_location (
  dim_location_id STRING,
  `location` STRUCT<`coordinates`: ARRAY<DOUBLE>, `type`: STRING>,
  lat FLOAT,
  lon FLOAT,
  load_id STRING,
  loaded_on TIMESTAMP
)
USING delta

-- COMMAND ----------

CREATE TABLE dim_parking_bay (
  dim_parking_bay_id STRING,
  bay_id STRING,
  `marker_id` STRING, 
  `meter_id` STRING, 
  `rd_seg_dsc` STRING, 
  `rd_seg_id` STRING, 
  `the_geom` STRUCT<`coordinates`: ARRAY<ARRAY<ARRAY<ARRAY<DOUBLE>>>>, `type`: STRING>,
  load_id STRING,
  loaded_on TIMESTAMP
)
USING delta

-- COMMAND ----------

-- MAGIC %python
-- MAGIC from pyspark.sql.functions import col
-- MAGIC 
-- MAGIC # DimDate
-- MAGIC dimdate = spark.read.csv("dbfs:/mnt/datalake/data/seed/DimDate.csv", header=True)
-- MAGIC dimdate.write.saveAsTable("dim_date")
-- MAGIC 
-- MAGIC # DimTime
-- MAGIC dimtime = spark.read.csv("dbfs:/mnt/datalake/data/seed/DimTime.csv", header=True)
-- MAGIC dimtime = dimtime.select(dimtime["second_of_day"].alias("dim_time_id"), col("*"))
-- MAGIC dimtime.write.saveAsTable("dim_time")

-- COMMAND ----------


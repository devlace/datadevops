-- Databricks notebook source
CREATE SCHEMA IF NOT EXISTS dw;
CREATE SCHEMA IF NOT EXISTS lnd;
CREATE SCHEMA IF NOT EXISTS interim;

-- COMMAND ----------

DROP TABLE IF EXISTS dw.fact_parking;
DROP TABLE IF EXISTS dw.dim_st_marker;
DROP TABLE IF EXISTS dw.dim_location;
DROP TABLE IF EXISTS dw.dim_parking_bay;
DROP TABLE IF EXISTS dw.dim_date;
DROP TABLE IF EXISTS dw.dim_time;

-- COMMAND ----------

CREATE TABLE dw.fact_parking (
  dim_date_id STRING,
  dim_time_id STRING,
  dim_parking_bay_id STRING,
  dim_location_id STRING,
  dim_st_marker_id STRING,
  status STRING,
  load_id STRING,
  loaded_on TIMESTAMP
)
USING parquet
LOCATION '/mnt/datalake/data/dw/fact_parking/';

REFRESH TABLE dw.fact_parking;

-- COMMAND ----------

CREATE TABLE dw.dim_st_marker (
  dim_st_marker_id STRING,
  st_marker_id STRING,
  load_id STRING,
  loaded_on TIMESTAMP
)
USING parquet
LOCATION '/mnt/datalake/data/dw/dim_st_marker/';

REFRESH TABLE dw.dim_st_marker;

-- COMMAND ----------

CREATE TABLE dw.dim_location (
  dim_location_id STRING,
  `location` STRUCT<`coordinates`: ARRAY<DOUBLE>, `type`: STRING>,
  lat FLOAT,
  lon FLOAT,
  load_id STRING,
  loaded_on TIMESTAMP
)
USING parquet
LOCATION '/mnt/datalake/data/dw/dim_location/';

REFRESH TABLE dw.dim_location;

-- COMMAND ----------

CREATE TABLE dw.dim_parking_bay (
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
USING parquet
LOCATION '/mnt/datalake/data/dw/dim_parking_bay/';

REFRESH TABLE dw.dim_parking_bay;

-- COMMAND ----------

-- MAGIC %python
-- MAGIC from pyspark.sql.functions import col
-- MAGIC 
-- MAGIC # DimDate
-- MAGIC dimdate = spark.read.csv("dbfs:/mnt/datalake/data/seed/DimDate.csv", header=True)
-- MAGIC dimdate.write.saveAsTable("dw.dim_date")
-- MAGIC 
-- MAGIC # DimTime
-- MAGIC dimtime = spark.read.csv("dbfs:/mnt/datalake/data/seed/DimTime.csv", header=True)
-- MAGIC dimtime = dimtime.select(dimtime["second_of_day"].alias("dim_time_id"), col("*"))
-- MAGIC dimtime.write.saveAsTable("dw.dim_time")

-- COMMAND ----------

DROP TABLE IF EXISTS interim.parking_bay;
CREATE TABLE interim.parking_bay (
  bay_id INT,
  `last_edit` TIMESTAMP,
  `marker_id` STRING, 
  `meter_id` STRING, 
  `rd_seg_dsc` STRING, 
  `rd_seg_id` STRING, 
  `the_geom` STRUCT<`coordinates`: ARRAY<ARRAY<ARRAY<ARRAY<DOUBLE>>>>, `type`: STRING>,
  load_id STRING,
  loaded_on TIMESTAMP
)
USING parquet
LOCATION '/mnt/datalake/data/interim/parking_bay/';

REFRESH TABLE interim.parking_bay;

-- COMMAND ----------

DROP TABLE IF EXISTS interim.sensor;
CREATE TABLE interim.sensor (
  bay_id INT,
  `st_marker_id` STRING,
  `lat` FLOAT,
  `lon` FLOAT, 
  `location` STRUCT<`coordinates`: ARRAY<DOUBLE>, `type`: STRING>, 
  `status` STRING, 
  load_id STRING,
  loaded_on TIMESTAMP
)
USING parquet
LOCATION '/mnt/datalake/data/interim/sensors/';

REFRESH TABLE interim.sensor;
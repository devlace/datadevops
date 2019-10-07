# -*- coding: utf-8 -*-

"""Main module."""


import uuid
from pyspark.sql import DataFrame
from pyspark.sql.functions import lit, udf, col, when
from pyspark.sql.types import (
    ArrayType, StructType, StructField, StringType, TimestampType, DoubleType, IntegerType)  # noqa: E501

uuidUdf = udf(lambda: str(uuid.uuid4()), StringType())


def get_schema(schema_name):
    if schema_name == 'interim_parkingbay_schema':
        schema = StructType([
            StructField('bay_id', IntegerType(), False),
            StructField('last_edit', StringType()),
            StructField('marker_id', StringType()),
            StructField('meter_id', StringType()),
            StructField('rd_seg_id', StringType()),
            StructField('rd_seg_dsc', StringType()),
            StructField('the_geom', StructType([
                StructField('coordinates', ArrayType(
                    ArrayType(ArrayType(ArrayType(DoubleType())))
                )),
                StructField('type', StringType())
            ])),
            StructField('load_id', StringType()),
            StructField('loaded_on', TimestampType())
        ])
    return schema


def process_dim_parking_bay(parkingbay_sdf: DataFrame,
                            dim_parkingbay_sdf: DataFrame,
                            load_id, loaded_on):
    """Transform sensordata into dim_parking_bay"""

    # Get landing data distint rows
    parkingbay_sdf = parkingbay_sdf\
        .select([
            "bay_id",
            "marker_id",
            "meter_id",
            "rd_seg_dsc",
            "rd_seg_id",
            "the_geom"])\
        .distinct()

    # Get new rows to insert through LEFT JOIN with existing rows
    nr_parkingbay_sdf = parkingbay_sdf.alias("pb")\
        .join(dim_parkingbay_sdf, "bay_id", "left_outer")\
        .where(dim_parkingbay_sdf["bay_id"].isNull())\
        .select(col("pb.*"))

    # Add load_id, loaded_at and dim_parking_bay_id
    nr_parkingbay_sdf = nr_parkingbay_sdf.withColumn("load_id", lit(load_id))\
        .withColumn("loaded_on", lit(loaded_on.isoformat()))\
        .withColumn("dim_parking_bay_id", uuidUdf())

    # Select relevant columns
    nr_parkingbay_sdf = nr_parkingbay_sdf.select([
        "dim_parking_bay_id",
        "bay_id",
        "marker_id",
        "meter_id",
        "rd_seg_dsc",
        "rd_seg_id",
        "the_geom",
        "load_id",
        "loaded_on"
    ])
    return nr_parkingbay_sdf


def process_dim_location(sensordata_sdf: DataFrame, dim_location: DataFrame,
                         load_id, loaded_on):
    """Transform sensordata into dim_location"""

    # Get landing data distint rows
    sensordata_sdf = sensordata_sdf\
        .select(["lat", "lon", "location"]).distinct()

    # Get new rows to insert through LEFT JOIN with existing rows
    nr_location_sdf = sensordata_sdf\
        .join(dim_location, ["lat", "lon", "location"], "left_outer")\
        .where(dim_location["lat"].isNull() & dim_location["lon"].isNull())

    # Add load_id, loaded_at and dim_parking_bay_id
    nr_location_sdf = nr_location_sdf.withColumn("load_id", lit(load_id))\
        .withColumn("loaded_on", lit(loaded_on.isoformat()))\
        .withColumn("dim_location_id", uuidUdf())

    # Select relevant columns
    nr_location_sdf = nr_location_sdf.select([
        "dim_location_id",
        "location",
        "lat",
        "lon",
        "load_id",
        "loaded_on"
    ])
    return nr_location_sdf


def process_dim_st_marker(sensordata_sdf: DataFrame,
                          dim_st_marker: DataFrame,
                          load_id, loaded_on):
    """Transform sensordata into dim_st_marker"""

    # Get landing data distint rows
    sensordata_sdf = sensordata_sdf.select(["st_marker_id"]).distinct()

    # Get new rows to insert through LEFT JOIN with existing rows
    nr_st_marker_sdf = sensordata_sdf\
        .join(dim_st_marker, ["st_marker_id"], "left_outer")\
        .where(dim_st_marker["st_marker_id"].isNull())

    # Add load_id, loaded_at and dim_parking_bay_id
    nr_st_marker_sdf = nr_st_marker_sdf.withColumn("load_id", lit(load_id))\
        .withColumn("loaded_on", lit(loaded_on.isoformat()))\
        .withColumn("dim_st_marker_id", uuidUdf())

    # Select relevant columns
    nr_st_marker_sdf = nr_st_marker_sdf.select([
        "dim_st_marker_id",
        "st_marker_id",
        "load_id",
        "loaded_on"
    ])
    return nr_st_marker_sdf


def process_fact_parking(sensordata_sdf: DataFrame,
                         dim_parkingbay_sdf: DataFrame,
                         dim_location_sdf: DataFrame,
                         dim_st_marker_sdf: DataFrame,
                         load_id, loaded_on):
    """Transform sensordata into fact_parking"""

    dim_date_id = loaded_on.strftime("%Y%M%d")
    midnight = loaded_on.replace(hour=0, minute=0, second=0, microsecond=0)
    dim_time_id = (midnight - loaded_on).seconds

    # Build fact
    fact_parking = sensordata_sdf\
        .join(dim_parkingbay_sdf.alias("pb"), "bay_id", "left_outer")\
        .join(dim_location_sdf.alias("l"), ["lat", "lon", "location"], "left_outer")\
        .join(dim_st_marker_sdf.alias("st"), "st_marker_id", "left_outer")\
        .select(
            lit(dim_date_id).alias("dim_date_id"),
            lit(dim_time_id).alias("dim_time_id"),
            when(col("pb.dim_parking_bay_id").isNull(), -1)
            .otherwise(col("pb.dim_parking_bay_id")).alias("dim_parking_bay_id"),
            when(col("l.dim_location_id").isNull(), -1)
            .otherwise(col("l.dim_location_id")).alias("dim_location_id"),
            when(col("st.dim_st_marker_id").isNull(), -1)
            .otherwise(col("st.dim_st_marker_id")).alias("dim_st_marker_id"),
            "status",
            lit(load_id).alias("load_id"),
            lit(loaded_on.isoformat()).alias("loaded_on")
        )
    return fact_parking

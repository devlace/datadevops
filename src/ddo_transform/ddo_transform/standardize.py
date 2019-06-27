# -*- coding: utf-8 -*-

"""Main module."""


from pyspark.sql import DataFrame
from pyspark.sql.functions import lit, col, to_timestamp


def standardize_parking_bay(parkingbay_sdf: DataFrame, load_id, loaded_on):
    t_parkingbay_sdf = (
        parkingbay_sdf
        .withColumn("last_edit", to_timestamp("last_edit", "YYYYMMddHHmmss"))
        .select(
            col("bay_id").cast("int").alias("bay_id"),
            "last_edit",
            "marker_id",
            "meter_id",
            "rd_seg_dsc",
            col("rd_seg_id").cast("int").alias("rd_seg_id"),
            "the_geom",
            lit(load_id).alias("load_id"),
            lit(loaded_on.isoformat()).alias("loaded_on")
        )
    )
    return t_parkingbay_sdf


def standardize_sensordata(sensordata_sdf: DataFrame, load_id, loaded_on):
    t_sensordata_sdf = (
        sensordata_sdf
        .select(
            col("bay_id").cast("int").alias("bay_id"),
            "st_marker_id",
            col("lat").cast("float").alias("lat"),
            col("lon").cast("float").alias("lon"),
            "location",
            "status",
            lit(load_id).alias("load_id"),
            lit(loaded_on.isoformat()).alias("loaded_on")
        )
    )
    return t_sensordata_sdf

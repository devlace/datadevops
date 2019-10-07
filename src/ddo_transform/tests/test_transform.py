#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ddo_transform` package."""

import os
import pytest
import datetime

from ddo_transform import transform

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def spark():
    """Spark Session fixture
    """
    from pyspark.sql import SparkSession

    spark = SparkSession.builder\
        .master("local[2]")\
        .appName("Unit Testing")\
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def test_process_dim_parking_bay(spark):
    """Test data transform"""
    parkingbay_schema = transform.get_schema("interim_parkingbay_schema")
    parkingbay_sdf = spark.read.json("./data/interim_parking_bay.json", multiLine=True, schema=parkingbay_schema)
    dim_parkingbay_sdf = spark.read.json("./data/dim_parking_bay.json", multiLine=True)
    load_id = 1
    loaded_on = datetime.datetime.now()
    results_df = transform.process_dim_parking_bay(parkingbay_sdf, dim_parkingbay_sdf, load_id, loaded_on)

    # TODO add more asserts
    assert results_df.count() != 0

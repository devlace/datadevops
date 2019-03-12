#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ddo_transform` package."""

import os
import pytest
import datetime
from click.testing import CliRunner

from ddo_transform import ddo_transform
from ddo_transform import cli

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
    parkingbay_sdf = spark.read.json("./data/MelbParkingBayData.json", multiLine=True)
    dim_parkingbay_sdf = spark.read.json("./data/dim_parking_bay.json", multiLine=True)
    load_id = 1
    loaded_on = datetime.datetime.now()
    results_df = ddo_transform.process_dim_parking_bay(parkingbay_sdf, dim_parkingbay_sdf, load_id, loaded_on)

    # TODO add more asserts
    assert results_df.count() != 0


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'ddo_transform.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output

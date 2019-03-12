#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ddo_transform` package."""

import os
import pytest

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


def test_transform(spark):
    """Test data transform"""
    df = spark.read.csv("./data/On-street_Parking_Bay_Sensors.csv")
    count = ddo_transform.transform(df)
    print(count)
    # df = ddo_transform(spark, sample_df)


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'ddo_transform.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output

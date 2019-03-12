# -*- coding: utf-8 -*-

"""Main module."""

from pyspark.sql import DataFrame, SparkSession


def transform(spark: SparkSession, df: DataFrame):
    print("transform!!")
    count = df.count()
    return(count)

from pyspark.sql import SparkSession

spark = SparkSession.builder\
        .master("local[2]")\
        .appName("Unit Testing")\
        .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
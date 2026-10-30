
import os
import sys

# Configuration Windows
os.environ["SPARK_LOCAL_HOSTNAME"] = "localhost"
os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"

# Utiliser exactement Python 3.11 du venv
python_executable = sys.executable

os.environ["PYSPARK_PYTHON"] = python_executable
os.environ["PYSPARK_DRIVER_PYTHON"] = python_executable

from pyspark.sql import SparkSession

print("Python utilisé :", python_executable, flush=True)
print("1. Démarrage de Spark...", flush=True)

spark = (
    SparkSession.builder
    .master("local[2]")
    .appName("5CLOUD-Velib-Test")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .config("spark.pyspark.python", python_executable)
    .getOrCreate()
)

try:
    print("2. Spark démarré !", flush=True)
    print("Version Spark :", spark.version, flush=True)

    df = spark.createDataFrame(
        [("1001", 14), ("1002", 8)],
        ["stationcode", "numbikesavailable"]
    )

    df.show()

    print("3. Test PySpark réussi !", flush=True)

finally:
    spark.stop()

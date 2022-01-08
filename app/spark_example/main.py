import pyspark


def spark_text_example(spark: pyspark.sql.SparkSession, filename: str = "text_example.txt"):
    print("### SPARK TEXT EXAMPLE ###")

    # DECLARE AND RUN COMPUTATION
    rows = spark.__search.text(filename).rdd
    lines = rows.map(lambda row: row.value)
    words = lines.flatMap(lambda line: line.split(" "))
    tokens = words.map(lambda word: 1)
    num_words = tokens.reduce(lambda a, b: a + b)

    print(f"rows: {rows.collect()}")
    print(f"lines: {lines.collect()}")
    print(f"words: {words.collect()}")
    print(f"tokens: {tokens.collect()}")
    print(f"num_words: {num_words}")
    print()
    return


def spark_table_example(spark: pyspark.sql.SparkSession, filename: str = "table_example.csv"):
    print("### SPARK TABLE EXAMPLE ###")

    delimiter = ","
    # DECLARE AND RUN COMPUTATION
    rows = spark.__search \
        .option("header", True) \
        .option("inferSchema", True) \
        .option("delimiter", delimiter) \
        .csv(filename).rdd

    total_value = rows \
        .map(lambda row: int(row["count"]) * float(row["value"])) \
        .reduce(lambda a, b: a + b)

    print(f"dataframe: {rows.collect()}")
    print(f"total_value: {total_value}")

    print()
    return


if __name__ == "__main__":
    # CREATE SPARK SESSION
    spark = pyspark.sql.SparkSession.builder \
        .appName("spark test") \
        .config("spark.some.config.option", "some-value") \
        .getOrCreate()

    # RUN EXAMPLE
    spark_text_example(spark)
    spark_table_example(spark)

    # STOP SESSION
    spark.stop()

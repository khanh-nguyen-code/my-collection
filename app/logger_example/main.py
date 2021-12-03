from my_collection import logger

if __name__ == "__main__":
    logger.now().debug("debug1")
    logger.now().debug("debug2")
    logger.now().info("hello1")
    logger.now().info("hello2")
    logger.now().with_field("key", "val").error("with field1")
    logger.now().with_field("key", "val").error("with field2")

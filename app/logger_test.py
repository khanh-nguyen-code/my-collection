from logger import Logger

if __name__ == "__main__":
    logger = Logger()
    logger.now().info("hello")
    logger.now().with_field("key", "val").error("with field")

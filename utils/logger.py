import logging
import sys

def setup_logger(name='whiz_md_bot', level=logging.INFO):
    """
    Configures and returns a logger instance.
    """
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False # Prevents log duplication if root logger is also configured

    return logger

if __name__ == '__main__':
    # Example usage:
    debug_logger = setup_logger('AppDebug', level=logging.DEBUG)
    info_logger = setup_logger('AppInfo', level=logging.INFO)
    error_logger = setup_logger('AppError', level=logging.ERROR)

    debug_logger.debug("This is a debug message.")
    info_logger.info("This is an info message.")
    info_logger.warning("This is a warning message (using info_logger).")
    error_logger.error("This is an error message.")
    error_logger.critical("This is a critical message.")

    # Test that loggers with different names don't interfere
    # if configured correctly (e.g. no duplicate handlers on root)
    another_logger = setup_logger('AnotherModule', level=logging.INFO)
    another_logger.info("Message from another module.")

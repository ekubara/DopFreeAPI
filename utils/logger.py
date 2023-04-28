import logging
import os
import sys


def set_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatterError = logging.Formatter(
        "[%(asctime)s] - [%(levelname)s] - [%(name)s(%(filename)s) - %(funcName)s%(lineno)d] "
        "- %(message)s\n[%(processName)s:%(process)d] [%(threadName)s:%(thread)d] - %("
        "pathname)s\n"
    )
    formatter = logging.Formatter("[%(asctime)s] - [%(levelname)s] - %(message)s")

    try:
        os.mkdir("logs")
    except Exception as _ex:
        logging.exception("Folder 'logs' already exists - %s" % _ex)

    # хэндлеры для разных видов ошибок и записи в файлы
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    file_handler_debug = logging.FileHandler("logs/debug.log")
    file_handler_debug.setLevel(logging.DEBUG)
    file_handler_debug.setFormatter(formatter)

    file_handler_warning = logging.FileHandler("logs/warning.log")
    file_handler_warning.setLevel(logging.WARNING)
    file_handler_warning.setFormatter(formatterError)

    file_handler_errors = logging.FileHandler("logs/error.log")
    file_handler_errors.setLevel(logging.ERROR)
    file_handler_errors.setFormatter(formatterError)

    file_handler_info = logging.FileHandler("logs/info.log")
    file_handler_info.setLevel(logging.INFO)
    file_handler_info.setFormatter(formatter)

    file_handler_critical = logging.FileHandler("logs/critical.log")
    file_handler_critical.setLevel(logging.CRITICAL)
    file_handler_critical.setFormatter(formatterError)

    file_handler_fatal = logging.FileHandler("logs/fatal.log")
    file_handler_fatal.setLevel(logging.FATAL)
    file_handler_fatal.setFormatter(formatterError)

    logger.addHandler(file_handler_debug)
    logger.addHandler(file_handler_warning)
    logger.addHandler(file_handler_errors)
    logger.addHandler(file_handler_info)
    logger.addHandler(file_handler_critical)
    logger.addHandler(file_handler_fatal)
    logger.addHandler(stdout_handler)

import logging
import logging.handlers
import os

def get_logger(name=None):

    logger = logging.getLogger(name)

    # check handler
    if len(logger.handlers) > 0:
        return logger

    # add custom Level
    logging.addLevelName(25, "DATA")
    logging.DATA = 25
    logger.setLevel(logging.DATA)

    # log format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s")

    # path validation
    log_dir = "./logs"
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)


    # TimedRotatingFileHandler
    # console = logging.StreamHandler()
    # timedFileHandler_info = logging.handlers.TimedRotatingFileHandler(filename="./logs/info.log",
    #                                                                   when="D",
    #                                                                   interval=1,
    #                                                                   encoding="utf-8")
    timedFileHandler_data = logging.handlers.TimedRotatingFileHandler(filename="./logs/data.log",
                                                                      when="D",
                                                                      interval=1,
                                                                      encoding="utf-8")
    timedFileHandler_error = logging.handlers.TimedRotatingFileHandler(filename="./logs/error.log",
                                                                      when="D",
                                                                      interval=1,
                                                                      encoding="utf-8")

    # logging Level
    # console.setLevel(logging.INFO)
    # timedFileHandler_info.setLevel(logging.INFO)
    timedFileHandler_data.setLevel(logging.DATA)
    timedFileHandler_error.setLevel(logging.ERROR)

    # format
    # console.setFormatter(formatter)
    # timedFileHandler_info.setFormatter(formatter)
    timedFileHandler_data.setFormatter(formatter)
    timedFileHandler_error.setFormatter(formatter)

    # add handler
    # logger.addHandler(console)
    # logger.addHandler(timedFileHandler_info)
    logger.addHandler(timedFileHandler_data)
    logger.addHandler(timedFileHandler_error)

    return logger
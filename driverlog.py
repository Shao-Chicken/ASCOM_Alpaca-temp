# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# driverlog.py - Shared global logger (originally log.py)
#
# Part of the MyAlpacaDriver sample device driver
#
# MIT License
# -----------------------------------------------------------------------------
import logging
import logging.handlers
import time

from config import Config

logger = None  # 全局单例

def init_logging():
    logging.basicConfig(level=Config.log_level)
    logger = logging.getLogger('myalpaca')  # 你可以自定义任何名字
    logger.setLevel(Config.log_level)

    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d %(levelname)s %(message)s',
        '%Y-%m-%dT%H:%M:%S'
    )
    formatter.converter = time.gmtime  # 日志时间使用UTC

    # 默认stdout handler
    if len(logger.handlers) == 0:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        ch.setLevel(Config.log_level)
        logger.addHandler(ch)

    # 如果配置文件里 log_to_stdout = false，就移除上面默认的 stdout
    if not Config.log_to_stdout:
        if logger.handlers:
            for h in logger.handlers:
                if isinstance(h, logging.StreamHandler):
                    logger.removeHandler(h)

    # 增加滚动日志文件 handler
    fh = logging.handlers.RotatingFileHandler(
        'my_alpaca.log',  # log 文件名
        mode='w',         # 每次启动都覆盖原先的日志
        maxBytes=Config.max_size_mb * 1000000,
        backupCount=Config.num_keep_logs,
        delay=True
    )
    fh.setFormatter(formatter)
    fh.setLevel(Config.log_level)
    fh.doRollover()  # 启动时先滚动一次，让日志文件从0开始
    logger.addHandler(fh)

    return logger

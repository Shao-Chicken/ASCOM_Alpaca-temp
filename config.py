# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# config.py - Device configuration loader (originally conf.py)
#
# Part of the MyAlpacaDriver sample device driver
#
# MIT License
# -----------------------------------------------------------------------------
import sys
import toml
import logging

_dict = toml.load(f'{sys.path[0]}/config.toml')  # 如果找不到文件会抛异常

def get_toml(sect: str, item: str):
    return _dict[sect][item]

class Config:
    # 从 config.toml 中对应字段加载
    ip_address: str = get_toml('network', 'ip_address')
    port: int = get_toml('network', 'port')

    location: str = get_toml('server', 'location')
    verbose_driver_exceptions: bool = get_toml('server', 'verbose_driver_exceptions')

    can_reverse: bool = get_toml('device', 'can_reverse')
    step_size: float = get_toml('device', 'step_size')
    steps_per_sec: int = get_toml('device', 'steps_per_sec')

    log_level: int = logging.getLevelName(get_toml('logging', 'log_level'))
    log_to_stdout: bool = get_toml('logging', 'log_to_stdout')
    max_size_mb: int = get_toml('logging', 'max_size_mb')
    num_keep_logs: int = get_toml('logging', 'num_keep_logs')

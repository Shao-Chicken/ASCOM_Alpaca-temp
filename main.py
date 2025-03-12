# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# main.py - Main Application module (originally app.py)
#
# Part of the MyAlpacaDriver sample device driver
#
# MIT License (retain from original)
# -----------------------------------------------------------------------------
# Python Compatibility: Requires Python 3.7 or later
#
# Edit History:
#   2025-03- (your date)  Migrated from the original Alpaca template
#
import sys
import traceback
import inspect
from wsgiref.simple_server import WSGIRequestHandler, make_server

import falcon
from falcon import Request, Response, App, HTTPInternalServerError

# 自定义模块的导入
import discovery
import exceptions
import management
import setupcontroller
import driverlog
import rotatorcontroller

from config import Config
from discovery import DiscoveryResponder
from common import set_common_logger

# ------------------------------------------------------------------
# 全局常量
# ------------------------------------------------------------------
API_VERSION = 1

# ------------------------------------------------------------------
# 自定义 WSGI Request Handler，用于在非200返回时进行额外日志处理
# ------------------------------------------------------------------
class LoggingWSGIRequestHandler(WSGIRequestHandler):
    """
    在 Python wsgiref.SimpleServer 之上做简单的封装，
    可以定制非200状态时的日志行为。
    """

    def log_message(self, format: str, *args):
        # 如果你想记录非 200 返回，可以解开下面注释
        # if args[1] != '200':
        #     driverlog.logger.info(f'{self.client_address[0]} <- {format % args}')
        pass

# ------------------------------------------------------------------
# 动态为某个“设备类型”模块下的类生成路由
# ------------------------------------------------------------------
def init_routes(app: App, devname: str, module):
    """
    从某个模块中找到所有类（假设都是 Falcon resource 类），
    并添加路由规则到 falcon.App 对象中。
    假定路由格式为 /api/v1/<devname>/<devnum>/<class_name_lower>
    """
    memlist = inspect.getmembers(module, inspect.isclass)
    for cname, ctype in memlist:
        # 只处理在该 module 中定义的类
        if ctype.__module__ == module.__name__:
            # 将类名小写作为 endpoint
            app.add_route(
                f'/api/v{API_VERSION}/{devname}/{{devnum:int(min=0)}}/{cname.lower()}',
                ctype()
            )

# ------------------------------------------------------------------
# 处理 falcon 中尚未被捕获的异常，记录日志并返回 500
# ------------------------------------------------------------------
def custom_excepthook(exc_type, exc_value, exc_traceback):
    # 不处理 Ctrl+C
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    driverlog.logger.error(f'Uncaught {exc_type.__name__} exception occurred:')
    driverlog.logger.error(exc_value)

    if Config.verbose_driver_exceptions and exc_traceback:
        format_exception = traceback.format_tb(exc_traceback)
        for line in format_exception:
            driverlog.logger.error(repr(line))

def falcon_uncaught_exception_handler(req: Request, resp: Response, ex: BaseException, params):
    exc = sys.exc_info()
    custom_excepthook(exc[0], exc[1], exc[2])
    raise HTTPInternalServerError('Internal Server Error', 'See logfile for details.')

# ------------------------------------------------------------------
# 主启动函数
# ------------------------------------------------------------------
def main():
    # 初始化日志
    logger = driverlog.init_logging()
    driverlog.logger = logger
    exceptions.logger = logger
    discovery.logger = logger
    set_common_logger(logger)
    # 让 rotator 设备的逻辑准备就绪
    rotatorcontroller.start_rot_device(logger)

    # 用于兜底处理 “最后机会” 异常
    sys.excepthook = custom_excepthook

    # 启动发现应答
    _DSC = DiscoveryResponder(Config.ip_address, Config.port)

    # 构造 Falcon APP
    falc_app = App()
    # 注册各类 “ASCOM设备” 路由
    init_routes(falc_app, 'rotator', rotatorcontroller)

    # 注册 Alpaca management 相关路由
    falc_app.add_route('/management/apiversions', management.apiversions())
    falc_app.add_route(f'/management/v{API_VERSION}/description', management.description())
    falc_app.add_route(f'/management/v{API_VERSION}/configureddevices', management.configureddevices())
    # setup
    falc_app.add_route('/setup', setupcontroller.svrsetup())
    falc_app.add_route(f'/setup/v{API_VERSION}/rotator/{{devnum}}/setup', setupcontroller.devsetup())

    # 钩子： Falcon 中处理未捕获异常
    falc_app.add_error_handler(Exception, falcon_uncaught_exception_handler)

    # 启动 wsgi server
    with make_server(Config.ip_address, Config.port, falc_app,
                     handler_class=LoggingWSGIRequestHandler) as httpd:
        logger.info(f'==STARTUP== Serving on {Config.ip_address}:{Config.port} (UTC timestamps).')
        httpd.serve_forever()

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# common.py - Shared helpers (originally shr.py)
#
# Part of the MyAlpacaDriver sample device driver
#
# MIT License
# -----------------------------------------------------------------------------
import json
from threading import Lock
from falcon import Request, Response, HTTPBadRequest
from logging import Logger

from exceptions import Success

logger: Logger = None

def set_common_logger(lgr):
    global logger
    logger = lgr

_bad_title = 'Bad Alpaca Request'

def to_bool(val_str: str) -> bool:
    # 只接受 "true" / "false"
    val = val_str.lower()
    if val not in ['true','false']:
        raise HTTPBadRequest(title=_bad_title,
                             description=f'Invalid boolean value "{val_str}"')
    return val == 'true'

def get_request_field(name: str, req: Request, caseless: bool=False, default=None) -> str:
    """
    从 query params 或者 form (PUT body) 中获取指定字段
    如果 default=None 表示该字段必填，否则抛 400。
    """
    bad_desc = f'Missing/empty parameter "{name}"'
    lower_name = name.lower()

    if req.method == 'GET':
        for k, v in req.params.items():
            if k.lower() == lower_name:
                return v
        if default is None:
            raise HTTPBadRequest(title=_bad_title, description=bad_desc)
        return default

    else:  # PUT
        formdata = req.get_media()
        if caseless:
            for k in formdata.keys():
                if k.lower() == lower_name:
                    return formdata[k]
        else:
            if name in formdata and formdata[name] != '':
                return formdata[name]

        if default is None:
            raise HTTPBadRequest(title=_bad_title, description=bad_desc)
        return default

def log_request(req: Request):
    msg = f'{req.remote_addr} -> {req.method} {req.path}'
    if req.query_string:
        msg += f'?{req.query_string}'
    logger.info(msg)

    if req.method == 'PUT' and req.content_length != 0:
        logger.info(f'{req.remote_addr} -> {req.media}')

class PreProcessRequest:
    """
    Falcon 钩子，做一些公共校验，例如 device number 合法性，clientId 合法性等。
    """

    def __init__(self, maxdev):
        self.maxdev = maxdev

    def _pos_or_zero(self, val: str) -> bool:
        try:
            test = int(val)
            return test >= 0
        except ValueError:
            return False

    def _check_request(self, req: Request, devnum: int):
        if devnum > self.maxdev:
            msg = f'Device number {devnum} not exist, max device = {self.maxdev}.'
            logger.error(msg)
            raise HTTPBadRequest(title=_bad_title, description=msg)

        # ClientID
        cid = get_request_field('ClientID', req, caseless=True, default=None)
        if cid is None:
            msg = 'Missing Alpaca ClientID'
            logger.error(msg)
            raise HTTPBadRequest(title=_bad_title, description=msg)
        if not self._pos_or_zero(cid):
            msg = f'Invalid ClientID {cid}'
            logger.error(msg)
            raise HTTPBadRequest(title=_bad_title, description=msg)

        # ClientTransactionID
        ctid = get_request_field('ClientTransactionID', req, caseless=True, default='0')
        if not self._pos_or_zero(ctid):
            msg = f'Invalid ClientTransactionID {ctid}'
            logger.error(msg)
            raise HTTPBadRequest(title=_bad_title, description=msg)

    def __call__(self, req: Request, resp: Response, resource, params):
        log_request(req)
        self._check_request(req, params['devnum'])

# 线程安全的全局自增
_tid_lock = Lock()
_tid = 0
def getNextTransId() -> int:
    global _tid
    with _tid_lock:
        _tid += 1
        return _tid

class PropertyResponse:
    """
    处理 GET 属性请求的 JSON 返回
    """
    def __init__(self, value, req: Request, err=Success()):
        self.ServerTransactionID = getNextTransId()
        # GET 情况下，ClientTransactionID 大小写不敏感，但若没给就默认为0
        self.ClientTransactionID = int(get_request_field('ClientTransactionID', req, True, '0'))

        self.ErrorNumber = err.Number
        self.ErrorMessage = err.Message

        # 如果无错误，可以返回 Value；若有错误，最好不要返回空值
        if self.ErrorNumber == 0 and value is not None:
            self.Value = value
            logger.info(f'{req.remote_addr} <- {value}')

    @property
    def json(self):
        return json.dumps(self.__dict__)

class MethodResponse:
    """
    处理 PUT 方法请求的 JSON 返回
    """
    def __init__(self, req: Request, err=Success(), value=None):
        self.ServerTransactionID = getNextTransId()
        # PUT 情况下，若字段名大小写不对，则默认0
        self.ClientTransactionID = int(get_request_field('ClientTransactionID', req, False, '0'))

        self.ErrorNumber = err.Number
        self.ErrorMessage = err.Message
        if self.ErrorNumber == 0 and value is not None:
            self.Value = value
            logger.info(f'{req.remote_addr} <- {value}')

    @property
    def json(self):
        return json.dumps(self.__dict__)

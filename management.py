# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# management.py - Management API for Alpaca
#
# Part of the MyAlpacaDriver sample device driver
#
# MIT License
# -----------------------------------------------------------------------------
import falcon
from falcon import Request, Response

from common import PropertyResponse
from config import Config
from logging import Logger

from rotatorcontroller import RotatorMetadata

logger: Logger = None

class apiversions:
    def on_get(self, req: Request, resp: Response):
        apis = [1]  # 可以根据需要添加更多版本
        resp.text = PropertyResponse(apis, req).json

class description:
    def on_get(self, req: Request, resp: Response):
        desc = {
            'ServerName'   : TelescopeMetadata.Description,
            'DeviceType' : TelescopeMetadata.DeviceType,
            'Version'      : TelescopeMetadata.Version,
            'Location'     : Config.location
        }
        resp.text = PropertyResponse(desc, req).json

class configureddevices:
    def on_get(self, req: Request, resp: Response):
        # 如果有多个 device，可以把它们都加入列表
        confarray = [
            {
                'DeviceName':     RotatorMetadata.Name,
                'DeviceType':     RotatorMetadata.DeviceType,
                'DeviceNumber':   0,
                'UniqueID':       RotatorMetadata.DeviceID
            }
        ]
        resp.text = PropertyResponse(confarray, req).json

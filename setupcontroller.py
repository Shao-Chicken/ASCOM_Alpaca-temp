# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# setupcontroller.py - Device setup endpoints (originally setup.py)
#
# Part of the MyAlpacaDriver sample device driver
#
# MIT License
# -----------------------------------------------------------------------------
from falcon import Request, Response
from common import log_request

class svrsetup:
    def on_get(self, req: Request, resp: Response):
        log_request(req)
        resp.content_type = 'text/html'
        resp.text = '<!DOCTYPE html><html><body><h2>Server setup is in config.toml</h2></body></html>'

class devsetup:
    def on_get(self, req: Request, resp: Response, devnum: str):
        log_request(req)
        resp.content_type = 'text/html'
        resp.text = '<!DOCTYPE html><html><body><h2>Device setup is in config.toml</h2></body></html>'

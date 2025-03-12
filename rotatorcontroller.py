# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# rotatorcontroller.py - ASCOM Alpaca Rotator endpoints (originally rotator.py)
#
# Part of the MyAlpacaDriver sample device driver
#
# MIT License
# -----------------------------------------------------------------------------
import falcon
from falcon import Request, Response, HTTPBadRequest, before
from logging import Logger

from common import PropertyResponse, MethodResponse, PreProcessRequest, \
                   get_request_field, to_bool
from exceptions import *
from rotatordevice import RotatorDevice

logger: Logger = None

maxdev = 0  # 单设备示例，如果要支持多实例，可以增大这个值

class RotatorMetadata:
    """
    描述“Rotator”这个设备类型的静态信息
    """
    Name = 'Sample Rotator'
    Version = '0.2'
    Description = 'Sample ASCOM Rotator'
    DeviceType = 'Rotator'
    DeviceID = '1892ED30-92F3-4236-843E-DA8EEEF2D1CC'
    DeviceManufacturer = 'ASCOM Initiative'
    InterfaceVersion = 3

# 单例模拟的设备实例
rot_dev = None

def start_rot_device(log: Logger):
    """
    在 main.py 中被调用，用来初始化模拟器
    """
    global logger, rot_dev
    logger = log
    rot_dev = RotatorDevice(logger)

# 以下是一系列 Falcon Resource 类（对应 Alpaca Rotator 的属性/方法）:

@before(PreProcessRequest(maxdev))
class action:
    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = MethodResponse(req, NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class commandblind:
    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = MethodResponse(req, NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class commandbool:
    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = MethodResponse(req, NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class commandstring:
    def on_put(self, req: Request, resp: Response, devnum: int):
        resp.text = MethodResponse(req, NotImplementedException()).json

@before(PreProcessRequest(maxdev))
class description:
    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(RotatorMetadata.Description, req).json

@before(PreProcessRequest(maxdev))
class driverinfo:
    def on_get(self, req: Request, resp: Response, devnum: int):
        info = f'{RotatorMetadata.Name} by {RotatorMetadata.DeviceManufacturer}'
        resp.text = PropertyResponse(info, req).json

@before(PreProcessRequest(maxdev))
class interfaceversion:
    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(RotatorMetadata.InterfaceVersion, req).json

@before(PreProcessRequest(maxdev))
class driverversion:
    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(RotatorMetadata.Version, req).json

@before(PreProcessRequest(maxdev))
class name:
    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(RotatorMetadata.Name, req).json

@before(PreProcessRequest(maxdev))
class supportedactions:
    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse([], req).json

@before(PreProcessRequest(maxdev))
class canreverse:
    def on_get(self, req: Request, resp: Response, devnum: int):
        # 在原示例中，始终返回 True
        resp.text = PropertyResponse(True, req).json

@before(PreProcessRequest(maxdev))
class connected:
    def on_get(self, req: Request, resp: Response, devnum: int):
        resp.text = PropertyResponse(rot_dev.connected, req).json

    def on_put(self, req: Request, resp: Response, devnum: int):
        conn_str = get_request_field('Connected', req)
        conn_val = to_bool(conn_str)
        try:
            rot_dev.connected = conn_val
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                                       DriverException(0x500, 'Rotator.Connected failed', ex)).json

@before(PreProcessRequest(maxdev))
class ismoving:
    def on_get(self, req: Request, resp: Response, devnum: int):
        if not rot_dev.connected:
            resp.text = PropertyResponse(None, req, NotConnectedException()).json
            return
        try:
            moving = rot_dev.is_moving
            resp.text = PropertyResponse(moving, req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                                         DriverException(0x500, 'Rotator.IsMoving failed', ex)).json

@before(PreProcessRequest(maxdev))
class mechanicalposition:
    def on_get(self, req: Request, resp: Response, devnum: int):
        if not rot_dev.connected:
            resp.text = PropertyResponse(None, req, NotConnectedException()).json
            return
        try:
            pos = rot_dev.mechanical_position
            resp.text = PropertyResponse(pos, req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                                         DriverException(0x500, 'Rotator.MechanicalPosition failed', ex)).json

@before(PreProcessRequest(maxdev))
class position:
    def on_get(self, req: Request, resp: Response, devnum: int):
        if not rot_dev.connected:
            resp.text = PropertyResponse(None, req, NotConnectedException()).json
            return
        try:
            pos_val = rot_dev.position
            resp.text = PropertyResponse(pos_val, req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                                         DriverException(0x500, 'Rotator.Position failed', ex)).json

@before(PreProcessRequest(maxdev))
class reverse:
    def on_get(self, req: Request, resp: Response, devnum: int):
        if not rot_dev.connected:
            resp.text = PropertyResponse(None, req, NotConnectedException()).json
            return
        try:
            rev = rot_dev.reverse
            resp.text = PropertyResponse(rev, req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                                         DriverException(0x500, 'Rotator.Reverse failed', ex)).json

    def on_put(self, req: Request, resp: Response, devnum: int):
        if not rot_dev.connected:
            resp.text = MethodResponse(req, NotConnectedException()).json
            return
        rev_str = get_request_field('Reverse', req)
        rev_val = to_bool(rev_str)
        try:
            rot_dev.reverse = rev_val
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                                       DriverException(0x500, 'Rotator.Reverse failed', ex)).json

@before(PreProcessRequest(maxdev))
class stepsize:
    def on_get(self, req: Request, resp: Response, devnum: int):
        if not rot_dev.connected:
            resp.text = PropertyResponse(None, req, NotConnectedException()).json
            return
        try:
            st = rot_dev.step_size
            resp.text = PropertyResponse(st, req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                                         DriverException(0x500, 'Rotator.StepSize failed', ex)).json

@before(PreProcessRequest(maxdev))
class targetposition:
    def on_get(self, req: Request, resp: Response, devnum: int):
        if not rot_dev.connected:
            resp.text = PropertyResponse(None, req, NotConnectedException()).json
            return
        try:
            tp = rot_dev.target_position
            resp.text = PropertyResponse(tp, req).json
        except Exception as ex:
            resp.text = PropertyResponse(None, req,
                                         DriverException(0x500, 'Rotator.TargetPosition failed', ex)).json

@before(PreProcessRequest(maxdev))
class halt:
    def on_put(self, req: Request, resp: Response, devnum: int):
        if not rot_dev.connected:
            resp.text = MethodResponse(req, NotConnectedException()).json
            return
        try:
            rot_dev.Halt()
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                                       DriverException(0x500, 'Rotator.Halt failed', ex)).json

@before(PreProcessRequest(maxdev))
class move:
    def on_put(self, req: Request, resp: Response, devnum: int):
        if not rot_dev.connected:
            resp.text = MethodResponse(req, NotConnectedException()).json
            return
        pos_str = get_request_field('Position', req)
        try:
            delta = float(pos_str)
        except:
            resp.text = MethodResponse(req, InvalidValueException(f'Invalid Position={pos_str}')).json
            return

        # 简单做个归约
        while delta < 0:
            delta += 360.0
        while delta >= 360.0:
            delta -= 360.0

        try:
            rot_dev.Move(delta)
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                                       DriverException(0x500, 'Rotator.Move failed', ex)).json

@before(PreProcessRequest(maxdev))
class moveabsolute:
    def on_put(self, req: Request, resp: Response, devnum: int):
        if not rot_dev.connected:
            resp.text = MethodResponse(req, NotConnectedException()).json
            return
        pos_str = get_request_field('Position', req)
        try:
            newpos = float(pos_str)
        except:
            resp.text = MethodResponse(req, InvalidValueException(f'Invalid Position={pos_str}')).json
            return

        if newpos < 0.0 or newpos >= 360.0:
            resp.text = MethodResponse(req, InvalidValueException(f'Position out of range: {newpos}')).json
            return

        try:
            rot_dev.MoveAbsolute(newpos)
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                                       DriverException(0x500, 'Rotator.MoveAbsolute failed', ex)).json

@before(PreProcessRequest(maxdev))
class movemechanical:
    def on_put(self, req: Request, resp: Response, devnum: int):
        if not rot_dev.connected:
            resp.text = MethodResponse(req, NotConnectedException()).json
            return

        pos_str = get_request_field('Position', req)
        try:
            newpos = float(pos_str)
        except:
            resp.text = MethodResponse(req, InvalidValueException(f'Invalid Position={pos_str}')).json
            return

        if newpos < 0.0 or newpos >= 360.0:
            resp.text = MethodResponse(req, InvalidValueException(f'Position out of range: {newpos}')).json
            return

        try:
            rot_dev.MoveMechanical(newpos)
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                                       DriverException(0x500, 'Rotator.MoveMechanical failed', ex)).json

@before(PreProcessRequest(maxdev))
class sync:
    def on_put(self, req: Request, resp: Response, devnum: int):
        if not rot_dev.connected:
            resp.text = MethodResponse(req, NotConnectedException()).json
            return

        pos_str = get_request_field('Position', req)
        try:
            newpos = float(pos_str)
        except:
            resp.text = MethodResponse(req, InvalidValueException(f'Invalid Position={pos_str}')).json
            return

        if newpos < 0.0 or newpos >= 360.0:
            resp.text = MethodResponse(req, InvalidValueException(f'Position out of range: {newpos}')).json
            return

        try:
            rot_dev.Sync(newpos)
            resp.text = MethodResponse(req).json
        except Exception as ex:
            resp.text = MethodResponse(req,
                                       DriverException(0x500, 'Rotator.Sync failed', ex)).json

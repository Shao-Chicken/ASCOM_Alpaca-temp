# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# exceptions.py - Alpaca Exception Classes
#
# Part of the MyAlpacaDriver sample device driver
#
# MIT License
# -----------------------------------------------------------------------------
import traceback
from config import Config
from logging import Logger

logger: Logger = None

class Success:
    def __init__(self):
        self.number: int = 0
        self.message: str = ''

    @property
    def Number(self) -> int:
        return self.number

    @property
    def Message(self) -> str:
        return self.message

class ActionNotImplementedException:
    def __init__(self, message: str = 'The requested action is not implemented in this driver.'):
        self.number = 0x40C
        self.message = message
        logger.error(f'{self.__class__.__name__}: {message}')

    @property
    def Number(self) -> int:
        return self.number

    @property
    def Message(self) -> str:
        return self.message

class DriverException:
    def __init__(self, number: int = 0x500, message: str = 'Internal driver error.', exc=None):
        if number <= 0x500 or number >= 0xFFF:
            logger.error(f'Bad DriverException number {hex(number)}, use 0x500 instead.')
            number = 0x500

        self.number = number
        if exc is not None:
            if Config.verbose_driver_exceptions:
                self.fullmsg = f'{self.__class__.__name__}: {message}\n{traceback.format_exc()}'
            else:
                self.fullmsg = f'{self.__class__.__name__}: {message}\n{type(exc).__name__}: {str(exc)}'
        else:
            self.fullmsg = f'{self.__class__.__name__}: {message}'

        logger.error(self.fullmsg)

    @property
    def Number(self) -> int:
        return self.number

    @property
    def Message(self) -> str:
        return self.fullmsg

class InvalidOperationException:
    def __init__(self, message: str = 'The requested operation cannot be done at this time.'):
        self.number = 0x40B
        self.message = message
        logger.error(f'{self.__class__.__name__}: {message}')

    @property
    def Number(self) -> int:
        return self.number

    @property
    def Message(self) -> str:
        return self.message

class InvalidValueException:
    def __init__(self, message: str = 'Invalid value given.'):
        self.number = 0x401
        self.message = message
        logger.error(f'{self.__class__.__name__}: {message}')

    @property
    def Number(self) -> int:
        return self.number

    @property
    def Message(self) -> str:
        return self.message

class NotConnectedException:
    def __init__(self, message: str = 'The device is not connected.'):
        self.number = 0x407
        self.message = message
        logger.error(f'{self.__class__.__name__}: {message}')

    @property
    def Number(self) -> int:
        return self.number

    @property
    def Message(self) -> str:
        return self.message

class NotImplementedException:
    def __init__(self, message: str = 'Property or method not implemented.'):
        self.number = 0x400
        self.message = message
        logger.error(f'{self.__class__.__name__}: {message}')

    @property
    def Number(self) -> int:
        return self.number

    @property
    def Message(self) -> str:
        return self.message

class ParkedException:
    def __init__(self, message: str = 'Illegal operation while parked.'):
        self.number = 0x408
        self.message = message
        logger.error(f'{self.__class__.__name__}: {message}')

    @property
    def Number(self) -> int:
        return self.number

    @property
    def Message(self) -> str:
        return self.message

class SlavedException:
    def __init__(self, message: str = 'Illegal operation while slaved.'):
        self.number = 0x409
        self.message = message
        logger.error(f'{self.__class__.__name__}: {message}')

    @property
    def Number(self) -> int:
        return self.number

    @property
    def Message(self) -> str:
        return self.message

class ValueNotSetException:
    def __init__(self, message: str = 'The value has not yet been set.'):
        self.number = 0x402
        self.message = message
        logger.error(f'{self.__class__.__name__}: {message}')

    @property
    def Number(self) -> int:
        return self.number

    @property
    def Message(self) -> str:
        return self.message

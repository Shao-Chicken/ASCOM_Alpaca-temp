# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# rotatordevice.py - Simple simulator for a Rotator device
#
# Part of the MyAlpacaDriver sample device driver
#
# MIT License
# -----------------------------------------------------------------------------
from threading import Timer, Lock
from logging import Logger

class RotatorDevice:
    def __init__(self, logger: Logger):
        self._lock = Lock()
        self.logger = logger

        # 设备配置
        self._can_reverse = True
        self._step_size = 1.0
        self._steps_per_sec = 6

        # 设备状态
        self._reverse = False
        self._mech_pos = 0.0
        self._tgt_mech_pos = 0.0
        self._pos_offset = 0.0
        self._is_moving = False
        self._connected = False

        # 定时器
        self._timer = None
        self._interval = 1.0 / self._steps_per_sec
        self._stopped = True

    def _pos_to_mech(self, pos: float) -> float:
        mech = pos - self._pos_offset
        if mech >= 360.0:
            mech -= 360.0
        if mech < 0.0:
            mech += 360.0
        return mech

    def _mech_to_pos(self, mech: float) -> float:
        pos = mech + self._pos_offset
        if pos >= 360.0:
            pos -= 360.0
        if pos < 0.0:
            pos += 360.0
        return pos

    def start(self, from_run: bool = False):
        with self._lock:
            if from_run or self._stopped:
                self._stopped = False
                self._timer = Timer(self._interval, self._run)
                self._timer.start()

    def _run(self):
        with self._lock:
            delta = self._tgt_mech_pos - self._mech_pos
            if delta < -180.0:
                delta += 360.0
            if delta >= 180.0:
                delta -= 360.0

            if abs(delta) > (self._step_size / 2.0):
                self._is_moving = True
                # 简单地每次移动 step_size
                if delta > 0:
                    self._mech_pos += self._step_size
                    if self._mech_pos >= 360.0:
                        self._mech_pos -= 360.0
                else:
                    self._mech_pos -= self._step_size
                    if self._mech_pos < 0.0:
                        self._mech_pos += 360.0
            else:
                self._is_moving = False
                self._stopped = True

        if self._is_moving:
            self.start(from_run=True)

    def stop(self):
        with self._lock:
            self._stopped = True
            self._is_moving = False
            if self._timer is not None:
                self._timer.cancel()
            self._timer = None

    @property
    def can_reverse(self) -> bool:
        with self._lock:
            return self._can_reverse

    @property
    def reverse(self) -> bool:
        with self._lock:
            return self._reverse

    @reverse.setter
    def reverse(self, value: bool):
        with self._lock:
            self._reverse = value

    @property
    def step_size(self) -> float:
        with self._lock:
            return self._step_size

    @step_size.setter
    def step_size(self, val: float):
        with self._lock:
            self._step_size = val

    @property
    def steps_per_sec(self) -> int:
        with self._lock:
            return self._steps_per_sec

    @steps_per_sec.setter
    def steps_per_sec(self, val: int):
        with self._lock:
            self._steps_per_sec = val
            self._interval = 1.0 / self._steps_per_sec

    @property
    def position(self) -> float:
        with self._lock:
            return self._mech_to_pos(self._mech_pos)

    @property
    def mechanical_position(self) -> float:
        with self._lock:
            return self._mech_pos

    @property
    def target_position(self) -> float:
        with self._lock:
            return self._mech_to_pos(self._tgt_mech_pos)

    @property
    def is_moving(self) -> bool:
        with self._lock:
            return self._is_moving

    @property
    def connected(self) -> bool:
        with self._lock:
            return self._connected

    @connected.setter
    def connected(self, value: bool):
        with self._lock:
            if (not value) and self._connected and self._is_moving:
                raise RuntimeError('Cannot disconnect while rotator is moving')
            self._connected = value
        if value:
            self.logger.info('[connected]')
        else:
            self.logger.info('[disconnected]')

    def Move(self, delta_pos: float):
        self.logger.debug(f'[Move] delta={delta_pos}')
        with self._lock:
            if self._is_moving:
                raise RuntimeError('Rotator is already moving')
            self._is_moving = True
            self._tgt_mech_pos = self._mech_pos + delta_pos - self._pos_offset
            if self._tgt_mech_pos >= 360.0:
                self._tgt_mech_pos -= 360.0
            if self._tgt_mech_pos < 0.0:
                self._tgt_mech_pos += 360.0
        self.start()

    def MoveAbsolute(self, pos: float):
        self.logger.debug(f'[MoveAbs] pos={pos}')
        with self._lock:
            if self._is_moving:
                raise RuntimeError('Rotator is already moving')
            self._is_moving = True
            self._tgt_mech_pos = self._pos_to_mech(pos)
        self.start()

    def MoveMechanical(self, pos: float):
        self.logger.debug(f'[MoveMech] pos={pos}')
        with self._lock:
            if self._is_moving:
                raise RuntimeError('Rotator is already moving')
            self._is_moving = True
            self._tgt_mech_pos = pos
        self.start()

    def Sync(self, pos: float):
        self.logger.debug(f'[Sync] pos={pos}')
        with self._lock:
            if self._is_moving:
                raise RuntimeError('Cannot sync while moving')
            self._pos_offset = pos - self._mech_pos
            if self._pos_offset < -180.0:
                self._pos_offset += 360.0
            if self._pos_offset >= 180.0:
                self._pos_offset -= 360.0

    def Halt(self):
        self.logger.debug('[Halt]')
        self.stop()

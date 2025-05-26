# sensors/base.py
from abc import ABC, abstractmethod


class StepSensorBase(ABC):
    """
    计步传感器抽象类
    子类分为计步传感器(内置)或加速度传感器计步算法
    """

    CURRENT_STEP = 0  # 全局步数计数

    def __init__(self, step_callback=None):
        self.step_callback = step_callback
        self.is_available = False

    @abstractmethod
    def register_step_listener(self):
        """注册计步监听器，如有需要"""
        pass

    @abstractmethod
    def unregister_step_listener(self):
        """注销计步监听器，如有需要"""
        pass

    def on_step_detected(self, steps=1):
        """
        检测到步数增加时的回调
        """
        StepSensorBase.CURRENT_STEP += steps
        if self.step_callback:
            self.step_callback(StepSensorBase.CURRENT_STEP)

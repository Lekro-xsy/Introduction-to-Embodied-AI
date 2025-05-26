# sensors/pedometer.py
from .base import StepSensorBase
import logging

logger = logging.getLogger(__name__)


class StepSensorPedometer(StepSensorBase):
    def __init__(self, step_callback=None):
        super().__init__(step_callback)
        self.sensor_mode = -1
        self.last_step = -1
        self.live_step = 0

    def register_step_listener(self):
        self.is_available = True
        logger.info("计步传感器可用！")

    def unregister_step_listener(self):
        # 注销监听（如果有）
        pass

    def on_sensor_data(self, sensor_type, value):
        """
        模拟从计步传感器获取数据的函数。
        sensor_type: 'detector' or 'counter'
        value: 传感器返回的当前步数或步检测
        """
        self.live_step = int(value)
        if sensor_type == "detector":
            logger.info(f"Detector步数: {self.live_step}")
            self.on_step_detected(self.live_step)  # 检测到走了一步就+1
        elif sensor_type == "counter":
            logger.info(f"Counter步数: {self.live_step}")
            # Counter模式下传感器直接给出累计步数
            current_absolute_steps = self.live_step
            # 将基类的CURRENT_STEP设为当前传感器给出的数值
            step_diff = current_absolute_steps - StepSensorBase.CURRENT_STEP
            if step_diff > 0:
                self.on_step_detected(step_diff)

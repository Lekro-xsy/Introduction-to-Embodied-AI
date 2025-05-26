# sensors/acceleration.py
from .base import StepSensorBase
import math
import logging

logger = logging.getLogger(__name__)


class StepSensorAcceleration(StepSensorBase):
    def __init__(self, step_callback=None):
        super().__init__(step_callback)
        # 算法相关参数
        self.valueNum = 5
        self.tempValue = [0] * self.valueNum
        self.tempCount = 0
        self.isDirectionUp = False
        self.continueUpCount = 0
        self.continueUpFormerCount = 0
        self.lastStatus = False
        self.peakOfWave = 0
        self.valleyOfWave = 0
        self.timeOfThisPeak = 0
        self.timeOfLastPeak = 0
        self.timeOfNow = 0
        self.gravityOld = 0
        self.ThreadValue = 1.3
        self.initialValue = 1.7
        self.minValue = 0
        self.maxValue = 19.6

    def register_step_listener(self):
        self.is_available = True
        logger.info("加速度传感器可用！")

    def unregister_step_listener(self):
        # 注销逻辑
        pass

    def on_sensor_data(self, x, y, z, timestamp):
        """
        传入加速度传感器的x,y,z数据以及时间戳(timestamp)，
        timestamp可用系统时间（ms）表示。
        """
        magnitude = math.sqrt(x * x + y * y + z * z)
        self.detectorNewStep(magnitude, timestamp)

    def detectorNewStep(self, values, timestamp):
        if self.gravityOld == 0:
            self.gravityOld = values
        else:
            if self.DetectorPeak(values, self.gravityOld, timestamp):
                self.timeOfLastPeak = self.timeOfThisPeak
                self.timeOfNow = timestamp
                if (
                    self.timeOfNow - self.timeOfLastPeak >= 200
                    and (self.peakOfWave - self.valleyOfWave >= self.ThreadValue)
                    and (self.timeOfNow - self.timeOfLastPeak) <= 2000
                ):
                    self.timeOfThisPeak = self.timeOfNow
                    self.preStep()
                if self.timeOfNow - self.timeOfLastPeak >= 200 and (
                    self.peakOfWave - self.valleyOfWave >= self.initialValue
                ):
                    self.timeOfThisPeak = self.timeOfNow
                    self.ThreadValue = self.Peak_Valley_Thread(
                        self.peakOfWave - self.valleyOfWave
                    )
        self.gravityOld = values

    def preStep(self):
        # 检测到一步
        self.on_step_detected(1)

    def DetectorPeak(self, newValue, oldValue, timestamp):
        self.lastStatus = self.isDirectionUp
        if newValue >= oldValue:
            self.isDirectionUp = True
            self.continueUpCount += 1
        else:
            self.continueUpFormerCount = self.continueUpCount
            self.continueUpCount = 0
            self.isDirectionUp = False

        # 判断波峰
        if (
            not self.isDirectionUp
            and self.lastStatus
            and (self.continueUpFormerCount >= 2)
            and (oldValue >= self.minValue and oldValue < self.maxValue)
        ):
            self.peakOfWave = oldValue
            return True
        elif not self.lastStatus and self.isDirectionUp:
            self.valleyOfWave = oldValue
            return False
        else:
            return False

    def Peak_Valley_Thread(self, value):
        tempThread = self.ThreadValue
        if self.tempCount < self.valueNum:
            self.tempValue[self.tempCount] = value
            self.tempCount += 1
        else:
            tempThread = self.averageValue(self.tempValue, self.valueNum)
            for i in range(1, self.valueNum):
                self.tempValue[i - 1] = self.tempValue[i]
            self.tempValue[self.valueNum - 1] = value
        return tempThread

    def averageValue(self, value, n):
        ave = sum(value) / n
        if ave >= 8:
            ave = 4.3
        elif 7 <= ave < 8:
            ave = 3.3
        elif 4 <= ave < 7:
            ave = 2.3
        elif 3 <= ave < 4:
            ave = 2.0
        else:
            ave = 1.7
        return ave

# main.py
import logging
import sys

from sensors.acceleration import StepSensorAcceleration
from utils.file_io import load_sensor_data
from utils.signal_processing import preprocess_data

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def step_callback(step_count):
    print(f"当前步数：{step_count}")


def main():
    # 从命令行参数读取数据文件名称，默认使用walk_data.csv
    # 用法: python main.py data/run_data.csv
    data_file = "data/walk_data.csv"
    if len(sys.argv) > 1:
        data_file = sys.argv[1]

    logger.info(f"加载数据文件: {data_file}")
    data = load_sensor_data(data_file)
    # data格式: [time(ms), X, Y, Z]
    t = data[:, 0]
    x = data[:, 1]
    y = data[:, 2]
    z = data[:, 3]

    # 可选数据预处理，如低通滤波10Hz
    sampling_rate = 100
    x_proc, y_proc, z_proc = preprocess_data(
        x, y, z, sampling_rate=sampling_rate, lowpass_cutoff=10
    )

    # 初始化加速度传感器步数统计
    step_sensor = StepSensorAcceleration(step_callback=step_callback)
    step_sensor.register_step_listener()

    # 将预处理后的数据逐点送入计步算法
    # 注意: on_sensor_data参数为(x, y, z, time)顺序
    for i in range(len(t)):
        step_sensor.on_sensor_data(x_proc[i], y_proc[i], z_proc[i], t[i])

    step_sensor.unregister_step_listener()

    # 最终结果
    final_steps = step_sensor.CURRENT_STEP
    logger.info(f"分析完成，最终步数：{final_steps}")


if __name__ == "__main__":
    main()

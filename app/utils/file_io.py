# utils/file_io.py
import pandas as pd
from datetime import datetime


def load_sensor_data(csv_path):
    """
    读取包含Timestamp,X,Y,Z列的数据。
    Timestamp列格式类似：15-Dec-2024 07:12:54.004
    X,Y,Z为加速度数据。

    """
    df = pd.read_csv(csv_path)

    # 解析Timestamp为datetime对象
    # 格式推测：%d-%b-%Y %H:%M:%S.%f
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%d-%b-%Y %H:%M:%S.%f")

    # 转换为相对时间戳，以第一条记录为0
    start_time = df["Timestamp"].iloc[0]
    # 计算与首条记录的时间差，转换为毫秒
    df["rel_time_ms"] = (df["Timestamp"] - start_time).dt.total_seconds() * 1000.0

    # 提取数据列
    # 最终返回列顺序: time(ms), X, Y, Z
    data = df[["rel_time_ms", "X", "Y", "Z"]].to_numpy()

    return data

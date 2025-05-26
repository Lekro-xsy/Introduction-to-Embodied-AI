# utils/signal_processing.py
import numpy as np


def moving_average_filter(data, window_size=5):
    """
    对1D数据应用移动平均滤波。

    参数:
        data: 1D numpy数组，待滤波数据
        window_size: 滑动窗口大小

    返回:
        filtered_data: 滤波后的数据（与data长度相同）
    """
    if window_size < 1:
        raise ValueError("window_size must be at least 1.")
    cumsum = np.cumsum(np.insert(data, 0, 0))
    filtered = (cumsum[window_size:] - cumsum[:-window_size]) / float(window_size)
    # 前 (window_size - 1) 个点无法完全构建窗，因此简单处理为复制或用原值
    # 这里选择将前几个点用平均后的第一个有效值代替
    front_fill = np.full(window_size - 1, filtered[0])
    return np.concatenate((front_fill, filtered))


def fft_lowpass_filter(data, cutoff_freq, sampling_rate):
    """
    使用FFT对数据进行简单的低通滤波。此为示例性代码，非严格的滤波器设计。

    步骤：
    1. 对data进行FFT得到频域数据
    2. 将高于截止频率的频率分量设置为0
    3. 对修改后的频谱进行IFFT得到时域信号

    参数:
        data: 1D numpy数组
        cutoff_freq: 截止频率 (Hz)
        sampling_rate: 采样频率 (Hz)

    返回:
        filtered_data: 滤波后的时域信号
    """
    # 频域长度
    n = len(data)
    freqs = np.fft.rfftfreq(n, d=1.0 / sampling_rate)
    fft_data = np.fft.rfft(data)

    # 将高于截止频率的分量置零
    fft_data[freqs > cutoff_freq] = 0

    filtered = np.fft.irfft(fft_data, n)
    return filtered


def fft_highpass_filter(data, cutoff_freq, sampling_rate):
    """
    使用FFT对数据进行简单的高通滤波。此为示例性代码。

    步骤与低通类似，不同在于将低于截止频率的频率分量置0。

    参数:
        data: 1D numpy数组
        cutoff_freq: 截止频率 (Hz)
        sampling_rate: 采样频率 (Hz)

    返回:
        filtered_data: 滤波后的时域信号
    """
    n = len(data)
    freqs = np.fft.rfftfreq(n, d=1.0 / sampling_rate)
    fft_data = np.fft.rfft(data)

    # 将低于截止频率的分量置零
    fft_data[freqs < cutoff_freq] = 0

    filtered = np.fft.irfft(fft_data, n)
    return filtered


def remove_mean(data):
    """
    去除数据的直流分量（均值），即将数据的平均值减去，以数据中心化。

    参数:
        data: 1D numpy数组

    返回:
        data_centered: 减均值后的数据
    """
    return data - np.mean(data)


def standardize(data):
    """
    数据标准化： (data - mean) / std

    参数:
        data: 1D numpy数组

    返回:
        data_standardized: 标准化后的数据
    """
    return (data - np.mean(data)) / np.std(data)


def preprocess_data(
    x, y, z, sampling_rate=100, lowpass_cutoff=None, highpass_cutoff=None
):
    """
    示例预处理函数，将x, y, z三个方向的加速度数据进行相同的滤波和处理。
    可以根据需要自由组合上述滤波和归一化操作。

    参数:
        x, y, z: 1D numpy数组，加速度数据三个通道
        sampling_rate: 采样频率，默认100Hz
        lowpass_cutoff: 若不为None，则进行低通滤波
        highpass_cutoff: 若不为None，则进行高通滤波

    返回:
        x_proc, y_proc, z_proc: 处理后的数据
    """
    # 去均值
    x_proc = remove_mean(x)
    y_proc = remove_mean(y)
    z_proc = remove_mean(z)

    # 滤波
    if lowpass_cutoff is not None:
        x_proc = fft_lowpass_filter(x_proc, lowpass_cutoff, sampling_rate)
        y_proc = fft_lowpass_filter(y_proc, lowpass_cutoff, sampling_rate)
        z_proc = fft_lowpass_filter(z_proc, lowpass_cutoff, sampling_rate)

    if highpass_cutoff is not None:
        x_proc = fft_highpass_filter(x_proc, highpass_cutoff, sampling_rate)
        y_proc = fft_highpass_filter(y_proc, highpass_cutoff, sampling_rate)
        z_proc = fft_highpass_filter(z_proc, highpass_cutoff, sampling_rate)

    # 移动平均平滑
    x_proc = moving_average_filter(x_proc, window_size=5)
    y_proc = moving_average_filter(y_proc, window_size=5)
    z_proc = moving_average_filter(z_proc, window_size=5)

    return x_proc, y_proc, z_proc

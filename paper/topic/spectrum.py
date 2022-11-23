from scipy.signal import savgol_filter
from numpy.fft import fft, fftfreq
from siml.detect_peaks import *
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

def psd(y_values, sampling_frequency, mph=1):
    '''
    sampling_frequency
        the number of samples per second (or per other unit)
    '''

    f_values, psd_values = welch(y_values, fs=sampling_frequency)
    indices_peaks = detect_peaks(psd_values, mph)

    fig, ax = plt.subplots(figsize=(15, 6))
    ax.plot(f_values, psd_values, linestyle='-', color='blue')
    ax.scatter([f_values[i] for i in indices_peaks], [psd_values[i] for i in indices_peaks], color='red',marker='D')
    for idx in indices_peaks:
        x,y = f_values[idx], psd_values[idx]
        text = "  F = {:.2f}".format(x)
        ax.annotate(text, (x,y))
        print('F={}, T={}, psd={}'.format(x, 1/x, y))
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('PSD [V**2 / Hz]')
    plt.show()
 
def signal_fft(sampled_signal, sampling_frequency, mph=100):
    assert len(sampled_signal > 50)
    trend =  pd.Series(savgol_filter(sampled_signal, len(sampled_signal),1), index=sampled_signal.index)
    trend.plot()
    detrended = (sampled_signal - trend).rename('detrended')
    detrended.plot(secondary_y=True, legend=True)

    fft_y_  = fft(detrended) * 2.0 / len(detrended)
    fft_y = np.abs(fft_y_[:len(fft_y_)//2])
    indices_peaks = detect_peaks(fft_y, mph)

    fft_x_ = fftfreq(len(detrended), 1/sampling_frequency)
    fft_x = fft_x_[:len(fft_x_)//2]
    fig, ax = plt.subplots(figsize=(15, 6))

    ax.plot(fft_x, fft_y)
    ax.scatter([fft_x[i] for i in indices_peaks], [fft_y[i] for i in indices_peaks], color='red',marker='D')
    for idx in indices_peaks:
        x,y = fft_x[idx], fft_y[idx]
        text = "  F = {:.2f}".format(x)
        ax.annotate(text, (x,y))
        print('F={}, T={}, Amplitude={}'.format(x, 1/x, y))

def demo(T=0.05, mph_fft=0.5, mph_psd=0.5):
    amplitude = 1
    frequency = 1 / T
    T_sample_N = 40
    sampling_frequency = T_sample_N / T
    N_periods = 10
    x_value = np.linspace(0, T * N_periods, T_sample_N * N_periods)
    y_values = amplitude*np.sin(2*np.pi*frequency*x_value)
    df = pd.DataFrame({
        'x': x_value,
        'y': y_values
    })
    df.plot(x='x', y='y')
    plt.show()
    signal_fft(df.y, sampling_frequency, mph_fft)
    plt.show()
    psd(df.y, sampling_frequency, mph_psd)

if __name__ == '__main__':
    from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
    from paper.systems.simplesystem import simplesystem
    from ctse.systems.ct_system import ct_system
    import pandas as pd
    import matplotlib.pyplot as plt

    system = ct_system()
    rawdata = system.rawdata
    data = system.data

    def snr(s: pd.Series):
        return abs((s[-1] - s[0])) / s.diff().abs().sum()

    term = 40
    inss = [ins for ins in system.get_instrument_list()]
    snrs = [data.daily_prices(ins).dropna().rolling(term, min_periods=term).apply(snr).rename(ins) for ins in inss]
    df = pd.concat(snrs, axis=1)
    mdi = df.mean(axis=1).rename('mdi')

    detrend =(mdi - mdi.mean()).dropna()

    from paper.topic.spectrum import signal_fft
    signal_fft(detrend, 0.012)
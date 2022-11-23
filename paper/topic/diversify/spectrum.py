from scipy.signal import savgol_filter
from numpy.fft import fft, fftfreq
from siml.detect_peaks import *
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def price_fft(price, mph=100):
    trend =  pd.Series(savgol_filter(price, len(price),1), index=price.index)
    trend.plot()
    detrended = price - trend
    detrended.plot(secondary_y=True)

    fft_y_  = fft(detrended) * 2.0 / len(detrended)
    fft_y = np.abs(fft_y_[:len(fft_y_)//2])
    indices_peaks = detect_peaks(fft_y, mph)

    fft_x_ = fftfreq(len(detrended))
    fft_x = fft_x_[:len(fft_x_)//2]
    fig, ax = plt.subplots(figsize=(15, 6))

    ax.plot(fft_x, fft_y)
    ax.scatter(fft_x[indices_peaks], fft_y[indices_peaks], color='red',marker='D')
    for idx in indices_peaks:
        x,y = fft_x[idx], fft_y[idx]
        text = "  T = {:.2f}".format(1/x)
        ax.annotate(text, (x,y))
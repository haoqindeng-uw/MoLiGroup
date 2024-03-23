# import the necessary packages
import numpy as np
import matplotlib.pyplot as plt
from functions import *
import scipy.fft

""" UNDER CONSTRUCTION
class S21Gating:
    def __init__(self, s21_pol_data_name):
        self.s21_pol_data_name = s21_pol_data_name
        self.freq, self.t_span, self.s21_ift, self.t_reso = Prepare_data_and_ifft(s21_pol_data_name)
        self.N_pts = len(self.s21_ift)
"""

def Prepare_data_and_ifft(s21_pol_data_name):
    
    # import the data
    freq, r, i = import_pol_data(s21_pol_data_name)
    cmpl_s21 = r + 1j*i
    N_pts = len(cmpl_s21)

    # Perform ifft on the imported data
    s21_ift = scipy.fft.ifft(cmpl_s21)
    
    # Calculate the time resolution
    t_reso = 1/((freq[-1]-freq[0]))
    print('Time resolution is:', t_reso, 'nano sec')
    
    # The time here inclued the flipped data
    t_span = np.array(range(N_pts))*t_reso #s
    
    return freq, t_span, np.array(s21_ift), t_reso

def transform_back_to_frequency(filtd_ift_data):
    from scipy.fft import fft
    filtd_fft_data = fft(filtd_ift_data)
    return filtd_fft_data

def convert_time_to_index(t_thr_multi, t_reso, expand):
    t_reso_ns = t_reso/1e-9 
    expand = expand #ns
    t_zone = []
    for t_step in t_thr_multi:
        t_zone.append(t_step - expand)
        t_zone.append(t_step + expand)

    #convert to array index
    index_of_t = []
    for tt in t_zone:
        index_of_t.append(round(tt/t_reso_ns))
    
    return index_of_t

def filter_data(ift_org_data, t_idx, N_pts = 16001):
    #Copy the original data
    filtd_ift_data = np.array(ift_org_data)
    
    #Filtered everything before the first arrival
    filtd_ift_data[0:t_idx[0]] = 0
    
    for idx, t in enumerate(t_idx):
        
        #filtered everything before the first arrive
        if idx ==0:
            filtd_ift_data[0:t] = 0
            
        if idx%2 == 0 and idx != 0:
            filtd_ift_data[ t_idx[idx-1]:t_idx[idx] ] = 0
        
        if idx == len(t_idx)-1:
            filtd_ift_data[ t_idx[idx]: N_pts-1 ] = 0
            
    #Have to copy the first half of the filtered data and flip/concatenate to be transformed back
    half_ift_data = np.array(filtd_ift_data[:N_pts]) 
    #flip_ift = np.flip(half_ift_data)
    #full_filtd_ift = np.concatenate((half_ift_data,flip_ift))
    
    return filtd_ift_data

def filter_selected_data(ift_org_data, t_idx, N_pts = 16001):
    #Copy the original data
    filtd_ift_data = np.array(ift_org_data)
    
    #Filtered everything before the first arrival
    filtd_ift_data[0:t_idx[0]] = 0
    
    for idx, t in enumerate(t_idx):
        
        #filtered everything before the first arrive
        if idx ==0:
            filtd_ift_data[0:t] = 0
            
        if idx%2 == 0 and idx != 0:
            filtd_ift_data[ t_idx[idx-1]:t_idx[idx] ] = 0
        
        if idx == len(t_idx)-1:
            filtd_ift_data[ t_idx[idx]: N_pts-1 ] = 0
            
    #Have to copy the first half of the filtered data and flip/concatenate to be transformed back
    half_ift_data = np.array(ift_org_data[:N_pts]) - np.array(filtd_ift_data[:N_pts]) 
    
    #flip_ift = np.flip(half_ift_data)
    #full_filtd_ift = np.concatenate((half_ift_data,flip_ift))
    
    return half_ift_data

def filter_before_data(ift_org_data, t_idx, N_pts = 16001):
    #Copy the original data
    filtd_ift_data = np.array(ift_org_data)
    
    #Filtered everything before the first arrival
    filtd_ift_data[0:t_idx[0]] = 0
            
    #Have to copy the first half of the filtered data and flip/concatenate to be transformed back
    #half_ift_data = np.array(ift_org_data[:N_pts]) - np.array(filtd_ift_data[:N_pts]) 
    
    #flip_ift = np.flip(half_ift_data)
    #full_filtd_ift = np.concatenate((half_ift_data,flip_ift))
    
    return filtd_ift_data

# This function is used to plot the IFFT data and the time domain data
def plot_ift_and_TD(time_ift, t, filtered_ift_data, TD, xmax=1000, ymax=200e-6,  N_pts = 16001):
    fig = plt.figure()
    ax1 = plt.subplot(221)
    ax2 = plt.subplot(222)
    ax3 = plt.subplot(223)
    ax4 = plt.subplot(224)

    ax1.plot(time_ift[:N_pts-1]/1e-9, abs(filtered_ift_data[:N_pts-1]), label='IFFT-Amplitude', c='green')
    
    ax2.plot(t, TD, label='Raw TD data from VNA', c='green')
    
    ax3.plot(time_ift[:N_pts-1]/1e-9, np.real(filtered_ift_data[:N_pts-1]), label='IFFT-real', c='red')
    ax3.plot(time_ift[:N_pts-1]/1e-9, np.imag(filtered_ift_data[:N_pts-1]), label='IFFT-imag', c='blue')
    
    ax4.plot(time_ift[:N_pts-1]/1e-9, np.angle(filtered_ift_data[:N_pts-1]), label='IFFT-phase', c='orange')
    
    ax1.set_xlabel('Time(ns)')
    ax1.set_ylabel('Amplitude')
    #ax1.title.set_text('S12 time gated signal at 4K')
    ax1.legend(loc="upper right")
    x1,x2,y1,y2 = ax1.axis()  
    ax1.axis((0,xmax,0,ymax))
    ax1.grid()


    ax2.set_xlabel('Time(ns)')
    ax2.set_ylabel('Amplitude')
    ax2.legend(loc="upper right")
    x1,x2,y1,y2 = ax2.axis()  
    ax2.axis((0,xmax,0,ymax))
    ax2.grid()
    
    ax3.set_xlabel('Time(ns)')
    ax3.set_ylabel('Phase')
    ax3.legend(loc="upper right")
    x1,x2,y1,y2 = ax3.axis()  
    ax3.axis((0,xmax,-2000e-7,2000e-7))
    ax3.grid()
    
    x1,x2,y1,y2 = ax4.axis()  
    ax4.axis((0,1000,y1,y2))
    ax4.grid()
    
    fig.tight_layout()
    fig.set_size_inches(10,4)

# This function is used to plot the filtered IFFT data and overlaid with the original IFFT data
def plot_filtd_and_org_data(time_ift, filtd_ift_data, ift_org_data , N_pts = 16001, xmax=2000, ymax = 1000e-6, savefig = False):
    fig = plt.figure()
    ax1 = plt.subplot(111)

    #ax1.plot(time_ift[:N_pts-1]/1e-9, abs(ift_org_data[:N_pts-1]), label='IFFT', c='green')
    #ax1.plot(time_ift[:N_pts-1]/1e-9, abs(filtd_ift_data[:N_pts-1]), label='IFFT-filtered', c='blue')

    ax1.plot(time_ift[0:N_pts]/1e-9, abs(ift_org_data[0:N_pts]), label='IFFT data', c='green')
    ax1.plot(time_ift[0:N_pts]/1e-9, abs(filtd_ift_data[0:N_pts]), label='Time-gated region', c='xkcd:royal blue')

    
    ax1.set_xlabel('Time(ns)')
    ax1.set_ylabel('Transmission |S12|(mU)')
    ax1.legend(loc="upper right")
    x1,x2,y1,y2 = ax1.axis()  
    ax1.axis((0,xmax,0,ymax))
    ax1.grid()
    
    fig.set_size_inches(10,4)
    
    if savefig == True:
        fig.savefig('time_domain_filtering_data.pdf',format='pdf')

# This function is used to plot the filtered frequency domain data
def plot_fft_data(freq, filtd_fft_data, y_max, N_pts = 16001, manual_scale = False,  savefig = False):
    fig = plt.figure()
    ax1 = plt.subplot(111)
    ax1.plot(freq/1e9, abs(filtd_fft_data)*1e3, label='FFT time-gated date', c='xkcd:royal blue')

    ax1.set_xlabel('Frequency(GHz)')
    ax1.set_ylabel('Transmission |S12|(mU)')

    x1,x2,y1,y2 = ax1.axis() 
    if manual_scale == True:
        ax1.axis((x1,x2,y1, y_max))
    ax1.grid()
    
    fig.set_size_inches(10,4)
    
    if savefig == True:
        fig.savefig('freq_domain_filtering_data.pdf',format='pdf')

# This is the main function to filter the data. 
def Filter_S21_signals( freq, 
                        org_ift_data, 
                        t_reso,   
                        N_pts=20001,  
                        filter_noise = False,
                        filter_peaks = False,
                        filter_picking = False, 
                        filter_stop = False,
                        t_noise=[0], expand_noise = 0,
                        t_peaks=[0], expand_peaks = 200,
                        t_picked = [0], expand_picked = 20,
                        t_stop = 1000,
                        xmax=2000, ymax=1000e-6, ymax_fdom = 10e-5, manual_scale= False,
                        savefig = False,
                        plot_filtering = False):

    """
    Filter_S21_signals function takes in the original IFFT data, frequency array, and several optional parameters to filter the data in the frequency domain.
    It applies various filters to the data based on the optional parameters provided, including noise filtering, peak filtering, manual signal picking, and stop filtering.

    The function outputs the filtered IFFT data, frequency array, time span, and original IFFT data. It also includes several plotting functions to display the filtered and original data.

    Input Parameters:
    - freq (array): Frequency array for the signal being filtered.
    - org_ift_data (array): Original IFFT data that needs to be filtered.
    - t_reso (float): Time resolution of the data.
    - N_pts (int, optional): Number of points in the frequency array. Default value is 20001.

    - filter_noise (bool, optional): Whether to filter the signal before t < t_noise in the data. Default value is False.
    - filter_peaks (bool, optional): Whether to filter peaks in the data. Default value is False.
    - filter_picking (bool, optional): Whether to manually select what signals to be left in the data while filter out all other data. Default value is False.
    - filter_stop (bool, optional): Whether to filter signal after a certain time t > t_stop. Default value is False.

    - t_noise (array, optional): Time at which the time gating starts. Default value is [0].
    - expand_noise (int, optional): Number of points to expand around the time-gating start time. Default value is 0.
    - t_peaks (array, optional): Time at which peaks occur in the data. Default value is [0].
    - expand_peaks (int, optional): Number of points to expand around the peak signal. Default value is 200.
    - t_picked (array, optional): Time at which manually picked signals occur in the data. Default value is [0].
    - expand_picked (int, optional): Number of points to expand around the picked signal. Default value is 20.
    - t_stop (float, optional): Time after which signal is filtered. Default value is 1000.

    - xmax (int, optional): Maximum value for x-axis in the plot. Default value is 2000.
    - ymax (float, optional): Maximum value for y-axis in the time domain plot. Default value is 1e-3.
    - ymax_fdom (float, optional): Maximum value for y-axis in the frequency domain plot. Default value is 1e-5.
    - manual_scale (bool, optional): Whether to manually set y-axis scale in frequency domain plot. Default value is False.
    - savefig (bool, optional): Whether to save the plots as image files. Default value is False.

    Output Parameters:
    - freq (array): Frequency array for the signal being filtered.
    - nor_cmpl_filtered (array): Filtered data in the frequency domain.
    - t_span (array): Time span of the data.
    - filtered_ift_data (array): Filtered data in the time domain.
    - org_ift_data (array): Original IFFT data that was filtered.
    """
   
    filtered_ift_data = np.array(org_ift_data)
    t_span = t_reso * np.array(range(N_pts))

    #Filtering the data
    if filter_noise == True:
        print('Filtering(1) noise...')
        #Filtere everything before
        t_idx_before = convert_time_to_index(t_noise, t_reso, expand=expand_noise)
        filtered_ift_data = filter_before_data(filtered_ift_data, t_idx_before, N_pts = N_pts)

    if filter_peaks == True:
        print('Filtering(2) peaks...')
        #-----------------------------------------------------------------
        #Filtere signal between 
        t_idx_peaks = convert_time_to_index(t_peaks, t_reso, expand=expand_peaks)
        filtered_ift_data = filter_selected_data(filtered_ift_data , t_idx_peaks,N_pts = N_pts)
        #-----------------------------------------------------------------

    if filter_picking == True:
        print('Filtering(3) pickings...')
        #Manually pick signals
        t_idx_picked = convert_time_to_index(t_picked, t_reso, expand=expand_picked)
        filtered_ift_data = filter_data(filtered_ift_data , t_idx_picked , N_pts = N_pts)
        #-----------------------------------------------------------------
        
    if filter_stop == True:
        t_filter_stop =  t_stop*1e-9 #ns
        t_index_stop = int(t_filter_stop/t_reso)
        filtered_ift_data[t_index_stop:] = 0

    nor_cmpl_filtered = scipy.fft.fft(filtered_ift_data)

    if plot_filtering == True:
    #Plot
        plot_filtd_and_org_data(t_span, filtered_ift_data, org_ift_data , N_pts = N_pts, xmax=xmax, ymax=ymax, savefig= savefig)
        plot_fft_data(freq, nor_cmpl_filtered, y_max=ymax_fdom, N_pts = N_pts,  manual_scale= manual_scale, savefig= savefig )
    
    
    return freq, nor_cmpl_filtered, t_span, filtered_ift_data, org_ift_data
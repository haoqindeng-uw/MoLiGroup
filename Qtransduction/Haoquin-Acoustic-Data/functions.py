import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os, glob
import cmath as cm
from scipy.optimize import least_squares
from scipy.optimize import curve_fit
from glob import glob
from matplotlib.pyplot import figure

def import_pol_data(filename, print_file_name = False):
    if print_file_name:
        print(filename)
        
    filename = filename
    #Import file
    data = pd.read_csv(filename, skiprows =[0,1], header=None, sep=", ", 
                     names=['Frequency (Hz)', 'Real', 'Imag', '_'], engine='python').replace('"','', regex=True)
    data = data.replace(',','', regex=True)

    freq =np.array(data['Frequency (Hz)'].astype(float))
    real =np.array(data['Real'])
    imag =np.array(data['Imag'].astype(float))
    
        
    return freq, real, imag

def import_pol_s21_data(filename):
    print(filename)
    filename = filename
    #Import file
    data = pd.read_csv(filename, skiprows =[0,1], header=None, sep=", ", 
                     names=['Frequency (Hz)', 'Real', 'Imag', '_'], engine='python').replace('"','', regex=True)
    data = data.replace(',','', regex=True)
    freq =np.array(data['Frequency (Hz)'].astype(float))
    real =np.array(data['Real'])
    imag =np.array(data['Imag'])
    
        
    return freq, real, imag

def import_TD_data(filename):
    print(filename)
    filename = filename
    #Import file
    
    data = pd.read_csv(filename, skiprows =[0])
    
    t =np.array(data['Time (sec)'])
    lin =np.array(data['U'])
        
    return t, lin

def import_lin_data(filename):
    print(filename)
    filename = filename
    #Import file
    data = pd.read_csv(filename, skiprows =[0])
    
    frequency =np.array(data['Frequency (Hz)'])
    lin =np.array(data['U'])
        
    return frequency, lin

def import_data(filename):
    filename = filename
    data = np.loadtxt(filename, delimiter=None, skiprows=2)
    frequency =[]
    y_val =[]
    #Import file
    for i in range(len(data)):
        frequency.append(data[i][0])
        y_val.append(data[i][1])
    return frequency, y_val

#Load ,fit data and spit out the normalized admittence.
#And show the lump elements of the fitted data
def f(cmplx_imp_opt, y_data):
    
    #Setup the least square fitting function

    cmplx_imp_data = 50*(1+y_data)/(1-y_data)
    residule = cmplx_imp_opt - cmplx_imp_data   
    return residule

def f_wrap(x,freq,y_data):
    resSers = np.array(x[0]) #x[0]
    resLeak = np.array(x[1]) #x[1]
    capElcd = np.array(x[2]) #x[2]
    
    jOmega = 1j*2*np.pi*np.array(freq)*1e-9
    jOmegaCapElcd = jOmega*capElcd
    
    fx = f(x[0] + 1/(x[1]**(-1)+jOmega*x[2]) , y_data)
    #for i in range(len(fx)):
    return np.array([fx.real, fx.imag]).flatten()

def Do_the_thing(file_name,selected_fit_data):
    
    #import data with the given name
    f1,r1,i1 = import_pol_data(file_name)
    r1 = np.array(r1)
    i1 = np.array(i1)
    freq = np.array(f1)
    
    #convert real and imaginary to complex Gamma 
    cmplGamma = r1 + i1*1j
    phase = np.angle(cmplGamma)
    r = (r1**2 + i1**2)**0.5
    
    #Start the fitting process form the data
    
    #Initialized the parameters
    cmplImpChrt = 50
    ftResSersInit = 6 # (Ohm)
    ftResLeakInit = 300 # (Ohm)
    ftCapElcdInit = 0.2e-4 # (nF)
    ft_Init = [ftResSersInit,ftResLeakInit,ftCapElcdInit]
    
    #From the imported frequency
    
    freq_select = np.append(freq[selected_fit_data[0]:selected_fit_data[1]],freq[selected_fit_data[2]:selected_fit_data[3]])
    #From the complex gamma value
    cmplGamma_select = np.append(cmplGamma[selected_fit_data[0]:selected_fit_data[1]] , cmplGamma[selected_fit_data[2]:selected_fit_data[3]])
    
    #least square function set up
    res_wrapped = least_squares(f_wrap, (5, 300, 0.0015), args=(freq_select,cmplGamma_select), xtol=1e-11, ftol=1e-11, \
                            loss = 'cauchy',max_nfev=3000, bounds=([0,1e9]))
    
    #Print the fitted params
    print('Fitting results:')
    print('fitted R_s=', res_wrapped.x[0])
    print('fitted R_L=',res_wrapped.x[1])
    print('fitted C=',res_wrapped.x[2])
    
    #print(res_wrapped)
    
    #Use the fitted parameter to calculate the physical value
    fit_resSers = np.array(res_wrapped.x[0]) #x[0]
    fit_resLeak = np.array(res_wrapped.x[1]) #x[1]
    fit_capElcd = np.array(res_wrapped.x[2]) #x[2]
    
    jOmega = 1j*2*np.pi*np.array(freq)*1e-9
    jOmegaCapElcd = jOmega*fit_capElcd

    cmpl_imp_load = 50*(1+cmplGamma)/(1-cmplGamma)

    #Calculate the fitted load, gamma and admittnace using the fitted parameter
    ft_cmpl_re_im_load = fit_resSers+ 1/(fit_resLeak**(-1) + jOmegaCapElcd)
    ft_cmpl_gamma = (ft_cmpl_re_im_load-50)/(ft_cmpl_re_im_load+50)
    ft_cmplAdm = 1/(cmpl_imp_load-fit_resSers) - 1/fit_resLeak - jOmegaCapElcd
    
    #The following calculation assume the complex Characteristic Impedance (cmpl_chrt_Imp) is real = 50 ohm
    cmpl_chrt_Imp = 50
    Pwr_input = 1

    Vol_Load_RMS = np.sqrt(Pwr_input*cmpl_chrt_Imp/(1-cmplGamma**2))*(1+cmplGamma)
    Crt_Load_RMS = Vol_Load_RMS/cmpl_imp_load
    Crt_Res_Sers_RMS = Crt_Load_RMS
    Vol_Res_Sers_RMS = Crt_Res_Sers_RMS * fit_resSers

    Vol_Adm_RMS = Vol_Load_RMS - Vol_Res_Sers_RMS
    Vol_Res_Leak_RMS = Vol_Adm_RMS
    Crt_Adm_RMS = Vol_Adm_RMS*ft_cmplAdm
    Crt_Res_Leak_RMS = Vol_Res_Leak_RMS/fit_resLeak

    Pwr_refletion_from_data = cmplGamma.real**2 + cmplGamma.imag**2
    Pwr_Res_Sers = Vol_Res_Sers_RMS*np.conj(Crt_Res_Sers_RMS)
    Pwr_Res_Leak = Vol_Res_Leak_RMS*np.conj(Crt_Res_Leak_RMS)
    Pwr_Adm = Vol_Adm_RMS*np.conj(Crt_Adm_RMS)
    
    #Polar chart fited curve
    phase_fit = np.angle(ft_cmpl_gamma)
    r_fit = (ft_cmpl_gamma.real**2 + ft_cmpl_gamma.imag**2)**0.5
    
    return Pwr_Adm, Pwr_refletion_from_data, Pwr_Res_Sers, Pwr_Res_Leak, \
		cmplGamma, phase, r,  \
		ft_cmpl_gamma, phase_fit, r_fit, \
		 freq



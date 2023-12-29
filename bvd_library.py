import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os, glob
import cmath as cm
from scipy.optimize import least_squares
from scipy.optimize import curve_fit
from glob import glob
from matplotlib.pyplot import figure
import os
import sys
import skrf as rf
import matlab.engine
import numpy as np
import matplotlib as mpl


class BVD_Model:
    def __init__(self):
        self.file_name = None
        self.s11_pol = None
        self.freq = None
        self.Z_org = None

    def load_file(self, file_name, normalize=True):
        '''
        supports loading both the '.s2p' and '.prn' file.
        '''
        self.file_name = file_name
        if file_name.endswith('.s2p'):
            data = rf.Network(file_name)
            self.s11_pol = data.s[:,0,0]
            self.freq = data.f
        elif file_name.endswith('.prn'):
            import matlab.engine
            eng = matlab.engine.start_matlab()
            s11_pol, freq = eng.load_prn('4K-2-S11-pol.prn', nargout=2)
            self.s11_pol = np.squeeze(np.asarray(s11_pol))
            self.freq = np.squeeze(np.asarray(freq))
        if normalize is True:
            max = np.max(np.absolute(self.s11_pol))
            self.s11_pol = self.s11_pol / max
        self.Z_org = self.convert_s11_to_impedance(self.s11_pol)
        return

    def plot_s11(self, freq_unit='GHz', method='python', figsize=(12, 4), figscale=1):
        '''
        freq_unit: 'GHz', 'MHz', 'KHz', 'default'
        figsize: (12, 4)
        figscale: 0.8, 1.2
        '''
        scale = 1
        if freq_unit == 'GHz':
            scale = 1e9
        elif freq_unit == 'MHz':
            scale = 1e6
        elif freq_unit == 'KHz':
            scale = 1e3
        elif freq_unit == 'default':
            scale = 1
        x_label = 'Frequency (' + freq_unit + ')'
        figsize = [figsize[0] * figscale, figsize[1] * figscale]
        plt.figure(figsize=figsize)
        plt.suptitle('Raw S11 data')
        plt.subplot2grid((2, 3), (0, 0), colspan=2, rowspan=2)
        plt.plot(self.freq / scale, np.absolute(self.s11_pol))
        plt.xlabel(x_label)
        plt.ylabel('|S11|')
        plt.subplot2grid((2, 3), (0, 2))
        plt.plot(self.freq / scale, self.Z_org.real)
        plt.xlabel(x_label)
        plt.ylabel('Real(S11)')
        plt.subplot2grid((2, 3), (1, 2))
        plt.plot(self.freq / scale, self.Z_org.imag)
        plt.xlabel(x_label)
        plt.ylabel('Imag(S11)')
        plt.tight_layout()

    def convert_s11_to_impedance(self, s11_pol, Z_char=50):
        s11_pol = np.array(s11_pol)
        imp_pol = Z_char * (1+s11_pol) / (1-s11_pol)
        return imp_pol

    def convert_imped_to_s11(self, impedance, Z_char=50):
        impedance = np.array(impedance)
        s11_pol = (impedance - Z_char) / (impedance + Z_char)
        return s11_pol
    
    def Z_background(self, freq, Ls, Rs, Rp, Cp, stack=True):
        N = len(freq)
        freq = freq[: N//2]
        Ls = Ls*1e-9 # use nH unit
        Cp= Cp*1e-9 # use nF unit
        Omega = freq * 2 * np.pi

        Z_real = (Rp / (1 + np.square(Omega * Cp * Rp))) + Rs
        Z_imag = -(Omega*np.square(Rp)*Cp) / (1+np.square(Omega*Rp*Cp)) + Omega*Ls

        if stack is False:
            return Z_real + Z_imag * 1j
        else:
            return np.hstack((Z_real, Z_imag))
        
    def Y_resonance(self, freq, Lm, Cm, Rm, stack=True):
        N = len(freq)
        freq = freq[: N//2]
        Lm = Lm*1e-9 # use nH unit
        Cm = Cm*1e-9 # use nF unit
        Omega = freq * 2 * np.pi

        Y_real = Rm / (np.square(Rm) + np.square(Omega * Lm - 1 / (Omega * Cm)))
        Y_imag  = -(Omega * Lm - 1 / (Omega * Cm)) / (np.square(Rm) + np.square(Omega * Lm - 1 / (Omega * Cm)))

        if stack is False:
            return Y_real + Y_imag * 1j
        else:
            return np.hstack((Y_real, Y_imag))

    def fit_BVD_model_background(self, start1, end1, start2, end2, 
                                 BG_fit_params_manual=None, p0=None, ftol = 1e-6, bounds=None, 
                                 plot_fit=True, freq_unit='GHz', figsize=(14, 4), figscale=1):
        '''
        start1: 0.3e9
        end1: 0.71e9
        start2: 0.73e9
        end2: 1.5e9
        BG_fit_params_manual: [Ls, Rs, Rp, Cp]
        p0: [Ls0, Rs0, Rp0, Cp0]
        ftol: 1e-6
        bounds: ((0, 0, 0, 0), (np.inf, np.inf, np.inf, np.inf))
        plot_fit: True
        freq_unit: 'GHz', 'MHz', 'KHz', 'default'
        figsize: (12, 4)
        figscale: 0.8, 1.2
        '''
        freq = self.freq
        p0 = [0.8, 1e-6, 2000, 1e-3] # LS, RS, RP, CP
        if bounds is None:
            bounds = ((0, 0, 0, 0), (np.inf, np.inf, np.inf, np.inf))
        # Find the indices of the range in xdata
        start_idx1 = np.argmin(np.abs(freq - start1))
        end_idx1 = np.argmin(np.abs(freq - end1))
        start_idx2 = np.argmin(np.abs(freq - start2))
        end_idx2 = np.argmin(np.abs(freq - end2))

        # Slice xdata and ydata to the two specified ranges and concatenate them
        x_fit_full = freq[start_idx1: end_idx2]
        y_fit_smoothened = np.linspace(self.Z_org[end_idx1], self.Z_org[start_idx2], start_idx2 - end_idx1)
        y_fit_full = np.concatenate((self.Z_org[start_idx1:end_idx1], y_fit_smoothened, self.Z_org[start_idx2:end_idx2])) 
        y_fit_full_stacked = np.hstack((y_fit_full.real, y_fit_full.imag))
        x_fit_full_stacked = np.hstack((x_fit_full.real, x_fit_full.imag))

        if BG_fit_params_manual is not None:
            Ls, Rs, Rp, Cp = BG_fit_params_manual[0], BG_fit_params_manual[1], BG_fit_params_manual[2], BG_fit_params_manual[3] 
        else:
            # perform fitting
            popt, _, = curve_fit(lambda freq, Ls, Rs, Rp, Cp:
                                    self.Z_background(freq, Ls, Rs, Rp, Cp),
                                    x_fit_full_stacked,
                                    y_fit_full_stacked,
                                    p0= p0,
                                    ftol=ftol
                                )
            # Assign the fitted parameters
            Ls, Rs, Rp, Cp = popt[0], popt[1], popt[2], popt[3] 
        
        # Calculate the fitted admittance & impedance
        Z_fit = self.Z_background(np.hstack((freq, freq)), Ls, Rs, Rp, Cp, stack=False)
        s11_fit = self.convert_imped_to_s11(Z_fit)

        if plot_fit:
            scale = 1
            if freq_unit == 'GHz':
                scale = 1e9
            elif freq_unit == 'MHz':
                scale = 1e6
            elif freq_unit == 'KHz':
                scale = 1e3
            elif freq_unit == 'default':
                scale = 1
            x_label = 'Frequency (' + freq_unit + ')'
            figsize = [figsize[0] * figscale, figsize[1] * figscale]
            plt.figure(figsize=figsize)
            plt.suptitle('Background fitting')
            plt.subplot2grid((2, 4), (0, 0), colspan=2, rowspan=2)
            plt.plot(freq / scale, abs(self.s11_pol))
            plt.plot(freq / scale, abs(s11_fit), linestyle='dashed')
            plt.xlabel(x_label)
            plt.ylabel('|S11|')
            # plt.legend(['measured', 'fitted'])

            plt.subplot2grid((2, 4), (0, 3))
            plt.plot(freq / scale, self.Z_org.real)
            plt.plot(freq / scale, Z_fit.real, linestyle='dashed')
            plt.xlabel(x_label)
            plt.ylabel('Real(Z)')
            # plt.legend(['measured', 'fitted'])

            plt.subplot2grid((2, 4), (1, 3))
            plt.plot(freq / scale, self.Z_org.imag)
            plt.plot(freq / scale, Z_fit.imag, linestyle='dashed')
            plt.xlabel(x_label)
            plt.ylabel('Imag(Z)')
            # plt.legend(['measured', 'fitted'])

            plt.subplot2grid((2, 4), (0, 2))
            plt.plot(freq / scale, self.s11_pol.real)
            plt.plot(freq / scale, s11_fit.real, linestyle='dashed')
            plt.xlabel(x_label)
            plt.ylabel('Imag(S11)')
            # plt.legend(['measured', 'fitted'])

            plt.subplot2grid((2, 4), (1, 2))
            plt.plot(freq / scale, self.s11_pol.imag)
            plt.plot(freq / scale, s11_fit.imag, linestyle='dashed')
            plt.xlabel(x_label)
            plt.ylabel('Imag(S11)')
            # plt.legend(['measured', 'fitted'])
            plt.tight_layout()


        return s11_fit, Z_fit, popt

    def fit_BVD_model_resonances(self, start1, end1, start2, end2, bg_params, 
                                 RS_fit_params_manual=None, ftol=1e-6, bounds=None, 
                                 plot_fit=True, freq_unit='GHz', figsize=(14, 4), figscale=1):
        '''
        start1: 0.3e9
        end1: 0.71e9
        start2: 0.73e9
        end2: 1.5e9
        bg_params: [Ls, Rs, Rp, Cp]
        RS_fit_params_manual: [Lm, Cm, Rm]
        ftol: 1e-6
        bounds: ((0, 0, 0, 0), (np.inf, np.inf, np.inf, np.inf))
        plot_fit: True
        freq_unit: 'GHz', 'MHz', 'KHz', 'default'
        figsize: (12, 4)
        figscale: 0.8, 1.2
        '''
        freq = self.freq
        # Find the indices of the range in xdata
        start_idx1 = np.argmin(np.abs(freq - start1))
        end_idx1 = np.argmin(np.abs(freq - end1))
        start_idx2 = np.argmin(np.abs(freq - start2))
        end_idx2 = np.argmin(np.abs(freq - end2))
        Ls, Rs, Rp, Cp = bg_params[0] * 1e-9, bg_params[1], bg_params[2], (bg_params[3]) * 1e-9
        Y_org = 1 / (self.Z_org - Rs - 1j*Ls*freq*2*np.pi) - (1/Rp + 1j*Cp*freq*2*np.pi)
        # Slice xdata and ydata to the two specified ranges and concatenate them
        x_fit = freq[end_idx1:start_idx2]
        y_fit = Y_org[end_idx1:start_idx2]
        x_fit_stacked = np.hstack((x_fit, x_fit))
        y_fit_stacked = np.hstack((y_fit.real, y_fit.imag))
        # Compute initial guesses of [Lm, Cm, Rm]
        w_r = x_fit[np.argmax(y_fit.real)] * 2 * np.pi
        w_l = x_fit[np.argmin(y_fit.imag)] * 2 * np.pi
        Rm0 = 1 / np.max(y_fit.real) 
        Lm0 = Rm0 * w_l  / (w_l**2 - w_r**2)
        Cm0 = 1 / Lm0 / (w_r**2)
        Lm0 = Lm0 * 1e9
        Cm0 = Cm0 * 1e9

        p0 = [Lm0, Cm0, Rm0]
        if bounds is None:
            bounds = ((0, 0, 0), (np.inf, np.inf, np.inf))

        popt = None
        if RS_fit_params_manual is not None:
            Lm, Cm, Rm = RS_fit_params_manual[0], RS_fit_params_manual[1], RS_fit_params_manual[2]
        else:
            # Perform fitting
            popt, _  = curve_fit(lambda freq, Lm, Cm, Rm:
                                    self.Y_resonance(freq, Lm, Cm, Rm),       
                                    x_fit_stacked,
                                    y_fit_stacked,
                                    p0= p0,
                                    bounds = bounds,
                                    ftol=ftol,
                                )
            # Assign the fitted parameters
            Lm, Cm, Rm = popt[0], popt[1], popt[2]

        # Calculate the fitted admittance & impedance
        Omega = 2 * np.pi * np.array(freq)
        Y_fit = self.Y_resonance(np.hstack((freq, freq)), Lm, Cm, Rm, stack=False)
        Z_tot_fit = Rs + 1j * Omega * Ls  + 1 / (1/Rp + 1j * Omega * Cp + Y_fit)

        # Convert impedance to s11
        s11_fit = self.convert_imped_to_s11(Z_tot_fit)
        s11_pol = self.convert_imped_to_s11(self.Z_org)
        if plot_fit:
            scale = 1
            if freq_unit == 'GHz':
                scale = 1e9
            elif freq_unit == 'MHz':
                scale = 1e6
            elif freq_unit == 'KHz':
                scale = 1e3
            elif freq_unit == 'default':
                scale = 1
            x_label = 'Frequency (' + freq_unit + ')'
            figsize = [figsize[0] * figscale, figsize[1] * figscale]
            plt.figure(figsize=figsize)
            plt.suptitle('Resonance fitting')
            plt.subplot2grid((2, 4), (0, 0), colspan=2, rowspan=2)
            plt.plot(freq / scale, abs(s11_pol))
            plt.plot(freq / scale, abs(s11_fit), linestyle='dashed')
            plt.xlabel(x_label)
            plt.ylabel('|S11|')
            # plt.legend(['measured', 'fitted'])

            plt.subplot2grid((2, 4), (0, 2))
            plt.plot(freq / scale, s11_pol.real)
            plt.plot(freq / scale, s11_fit.real, linestyle='dashed')
            plt.xlabel(x_label)
            plt.ylabel('Real(S11)')
            # plt.legend(['measured', 'fitted'])

            plt.subplot2grid((2, 4), (1, 2))
            plt.plot(freq / scale, s11_pol.imag)
            plt.plot(freq / scale, s11_fit.imag, linestyle='dashed')
            plt.xlabel(x_label)
            plt.ylabel('Imag(S11)')
            # plt.legend(['measured', 'fitted'])

            plt.subplot2grid((2, 4), (0, 3))
            plt.plot(freq / scale, Y_org.real)
            plt.plot(freq / scale, Y_fit.real, linestyle='dashed')
            plt.xlabel(x_label)
            plt.ylabel('Real(Y)')
            # plt.legend(['measured', 'fitted'])
            plt.xlim(end1 / scale, start2 / scale)

            plt.subplot2grid((2, 4), (1, 3))
            plt.plot(freq / scale, Y_org.imag)
            plt.plot(freq / scale, Y_fit.imag, linestyle='dashed')
            plt.xlabel(x_label)
            plt.ylabel('Imag(Y)')
            # plt.legend(['measured', 'fitted'])
            plt.xlim(end1 / scale, start2 / scale)
            plt.tight_layout()
        
        return s11_fit, Z_tot_fit, popt, Y_fit
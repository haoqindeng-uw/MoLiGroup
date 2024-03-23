# Import the necessary packages
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
from S21Gating import ifft_complex_data, Filter_S21_signals


# Make a function that let me mannually fit the idt efficiency with parameters
def manual_efficiency(s11_pol, freq, Lm=50, Cm=0.895, Rm=25, plot = False, auto_fit = False, p0=25, bounds = (1, 100), ftol = 1e-5):
    
    # Actual fitting functions below
    Impedance_data = convert_s11_to_impedance(s11_pol)

    # Fit background
    # Define the fitting range
    start_bg, end_bg = 1e9, 5e9 #Hz
    start_bg2, end_bg2 = 8e9, 12e9

    # Define the initial fitting params
    p0_bg = [0.2, 1e-6, 500, 1e-2]
    _, _, Fit_params_4K = fit_BVD_model_background_4K(freq, Impedance_data, start_bg, end_bg, start_bg2, end_bg2, p0_bg, bounds_bg, ftol, max_nfev)
    
    # The part where the manual fitting starts----------------------------------
    if auto_fit == False:
        
        # Calculate Z0
        jOmega = 1j*2*np.pi*freq
        L0, Rs, R0, C0 = Fit_params_4K[0]*1e-9, Fit_params_4K[1], Fit_params_4K[2], (Fit_params_4K[3])*1e-9 
        Z0 = np.array(1/(1/R0 + jOmega*C0)) 

        # Generate some example frequency
        Y3 = modified_BVD_model(freq, Lm=Lm, Cm=Cm, Rm=Rm) # Signal at 7.5 GHz

        # Calculate the N combined admittances
        Y_N =  Y3

        # Calculate the total impedance
        Z_total = jOmega*L0 + Rs + 1/(1/Z0 + Y_N)  

        # Calculate the total impedance
        Y_total = 1/Z_total 

        # Calculate the S11 from total impedance
        s11_fit = convert_imped_to_s11(Z_total)

    if auto_fit == True:
        start, end = 7e9, 8e9

        # Find the indices of the range in xdata
        start_idx1 = np.argmin(np.abs(freq - start))
        end_idx1 = np.argmin(np.abs(freq - end))

        # Slice xdata and ydata to the two specified ranges and concatenate them
        Freq_fit = freq[start_idx1:end_idx1+1]
        Admittance_fit = 1/Impedance_data[start_idx1:end_idx1+1]

        L0, Rs, R0, C0 = Fit_params_4K[0]*1e-9, Fit_params_4K[1], Fit_params_4K[2], (Fit_params_4K[3])*1e-9 
        
        try:
            # Perform fitting
            popt, _  = curve_fit(lambda f, R_fit:
                                hstack_BVD_for_fit(1/( 1j*2*np.pi*f*L0 + Rs + 1/(1/np.array(1/(1/R0 + 1j*2*np.pi*f*C0)) + modified_BVD_model(f, Lm=Lm, Cm=Cm, Rm=R_fit)))),
                                Freq_fit,
                                np.hstack((Admittance_fit.real, Admittance_fit.imag)),
                                p0= p0,
                                bounds = bounds,
                                ftol = ftol)
            Rm_fit = popt[0]
            
            Y3 = modified_BVD_model(freq, Lm=Lm, Cm=Cm, Rm=Rm_fit) # Signal at 7.5 GHz
            
            jOmega = 1j*2*np.pi*freq
            Z0 = np.array(1/(1/R0 + jOmega*C0))

            # Calculate the total impedance
            Z_total = jOmega*L0 + Rs + 1/(1/Z0 + Y3)

            # Calculate the S11 from total impedance
            s11_fit = convert_imped_to_s11(Z_total)
            print(popt)
        except:
            print('Fitting failed')
            return 0
    # The part where the manual fitting ends----------------------------------

    # Calculate the power ratio
    Pwr_YN_list = calculate_power_ratio(fit_Z_total = Z_total,
                                        fit_s11 = s11_fit,
                                        Rs = Rs,
                                        fit_YN_list = [Y3])
    
    if plot == True:
        
        # Plot the fitted admittance and the S11
        plot_fit(freq, Impedance_data, Z_total, s11_pol, s11_fit)

        fig = plt.figure()
        ax1 = plt.subplot(111)
        for i, Pwr_YN in enumerate(Pwr_YN_list):
            ax1.plot(freq/1e9, abs(Pwr_YN), label= 'Y'+str(i))

        ax1.set_xlabel('Frequency (GHz)')
        ax1.set_ylabel('Power ratio')
        ax1.legend()
    
    return np.max(abs(Pwr_YN_list[0]))

# Define a function that does the fourier transform, extract the peak value of the S21 at the chosen frequency
# and correct the S21 value with the IDT efficiency and fit with the exponential decay function. Finally return the loss constant alpha
def get_alpha(freq11, freq21, S21_list, S11_list, S22_list,
            N_FIT = 11,
            manual_idt_eff = True, 
            plot_filter = False, 
            plot_num = 1, 
            manual_idt_list = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.2, 0.12, 0.2, 0.5, 0.5, 0.5, 0.5 ]),
            max_val_expend = 5):
    # Fourier transform
    ifft_list = []
    for cmpl_s21 in S21_list:
        N_pts, s21_ift, t_span, t_reso = ifft_complex_data(cmpl_s21, freq21, print_time_reso = False)
        ifft_list.append(s21_ift)

    # Time gating
    time_gated_FD_list = []
    plot_filtering = False
    for num, ifft_data in enumerate(ifft_list):
        
        if num == plot_num and plot_filter == True:
            plot_filtering = True
        elif num != plot_num and plot_filter == True:
            plot_filtering = False

        _, nor_cmpl_filtered, t_span, filtered_ift_data, org_ift_data = Filter_S21_signals(   freq21, 
                                                                                        ifft_data, 
                                                                                        t_reso,   
                                                                                        N_pts = N_pts,  
                                                                                        filter_noise = True,
                                                                                        filter_peaks = False,
                                                                                        filter_picking = False, 
                                                                                        filter_stop = True,
                                                                                        t_noise=[1], expand_noise = 0.1,
                                                                                        t_peaks=[0], expand_peaks = 200,
                                                                                        t_picked = [0], expand_picked = 20,
                                                                                        t_stop = 1300,
                                                                                        xmax=1000, ymax=1000e-6, ymax_fdom = 10e-5, manual_scale= False,
                                                                                        savefig = False,
                                                                                        plot_filtering = plot_filtering)

        time_gated_FD_list.append(nor_cmpl_filtered)
        


    # Find the indices of the range in xdata
    start, end = 7e9, 8e9
    start_idx = np.argmin(np.abs(freq21 - start))
    end_idx = np.argmin(np.abs(freq21 - end))

    # Find the maximum value between the two indices
    S21_max_list = []
    S21_avg_list = []
    S21_errorbar_list = []
    for time_gated_data in time_gated_FD_list:
        Max_value = np.max(np.abs(time_gated_data[start_idx:end_idx]))
        S21_max_list.append(Max_value)

        # Find the index of the maximum value and expend around the max indx by N points and find the average and the minimum value
        Max_idx = np.argmax(np.abs(time_gated_data[start_idx:end_idx]))
        Max_idx = Max_idx + start_idx
        Min_value = np.min(np.abs(time_gated_data[Max_idx-max_val_expend:Max_idx+max_val_expend]))
        avg_value = np.average(np.abs(time_gated_data[Max_idx-max_val_expend:Max_idx+max_val_expend]))
        S21_avg_list.append(avg_value)
        
        
        print(np.abs(time_gated_data[Max_idx-max_val_expend:Max_idx+max_val_expend]))
        
    
    # Calculate IDT efficiency
    idt_eff_list = []
    for s11_pol, s22_pol in zip( S11_list, S22_list):
        p_ratio11 = manual_efficiency(s11_pol= s11_pol, freq = freq11, Lm=50, Cm=0.895, Rm=20, plot = False, auto_fit = True, p0 = 10, bounds=(1,20), ftol=1e-5)
        p_ratio22 = manual_efficiency(s11_pol= s22_pol, freq = freq11, Lm=50, Cm=0.895, Rm=6, plot = False, auto_fit = True, p0 = 10, bounds=(6,30), ftol=1e-7)  
        idt_eff_list.append(p_ratio11*p_ratio22)
    print(idt_eff_list)

    #  S21 Normalization to the IDT efficiency
    if manual_idt_eff == True:
        IDT_Manual_eff = manual_idt_list
        norm_s21 = S21_max_list/np.array(IDT_Manual_eff)
        norm_s21_avg = np.array(S21_avg_list)/np.array(IDT_Manual_eff)
        norm_s21_error = norm_s21**2 - norm_s21_avg**2

    else:
        norm_s21 = S21_max_list/np.array(idt_eff_list)
        norm_s21_avg = np.array(S21_avg_list)/np.array(idt_eff_list)
        norm_s21_error = norm_s21**2 - norm_s21_avg**2

    # Fit the data with a exponential decay function with decay constant
    exp_popt, pcov = curve_fit(exp_decay, np.array(prop_distance[:N_FIT])*1e-3, np.array(norm_s21[:N_FIT]), p0=[0.06, 0.1]) #Unit in mm
    exp_popt_min, pcov = curve_fit(exp_decay, np.array(prop_distance[:N_FIT])*1e-3, np.array(norm_s21_avg[:N_FIT]), p0=[0.06, 0.1]) #Unit in mm
    exp_popt_error = abs(abs(10*np.log10(exp_popt[1])) - abs(10*np.log10(np.abs(exp_popt_min[1]))))

    """
    Output:
    S21_max_list: list of maximum S21 value at the targeted frequency
    S21_avg_list: list of average S21 value at the targeted frequency
    S21_errorbar_list: list of errorbar of S21 value at the targeted frequency (the difference between the maximum and the minimum s21)
    norm_s21: list of normalized S21 value at the targeted frequency (normalized by the IDT efficiency)
    idt_eff_list: list of IDT efficiency
    exp_popt: list of fitted exponential decay constant and the offset
    exp_popt_error: error of the fitted exponential decay constant (alpha_fit_max - alpha_fit_min)
    """

    return  S21_max_list, S21_avg_list, norm_s21_error, norm_s21,  np.array(idt_eff_list), exp_popt, exp_popt_error
% x = [1+1j, 2-2j];
% y = [3+3j, 4];
% [a, b] = test_func1(x, y);
% disp(a)
% disp(b)
% file_name = 'B0.s2p';
% [Rs, Ls, Rl, Ce, Rm, Cm, Lm, z0_real] = S11_Fitting_RLC(file_name);
file_name = "4K-2-S11-pol.prn"
[S11, freq] = load_prn(file_name)
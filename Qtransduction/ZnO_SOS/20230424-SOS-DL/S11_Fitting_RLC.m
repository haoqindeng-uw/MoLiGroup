%% Data import
Rs_vector = zeros(1,7);
Ls_vector = zeros(1,7);
Rp_vector = zeros(1,7);
Cp_vector = zeros(1,7);
Rm_vector = zeros(1,7);
Cm_vector = zeros(1,7);
Lm_vector = zeros(1,7);
%%
% for file_iter = 1:1
file_iter = 1;
%%
% file_idx = 0;
file_name = strcat('D', num2str(file_iter));
file_name = strcat(file_name, '.s2p');
disp(file_name);
% listing(:,1) = dir('4K-2-S11-pol.prn');
% data = dir('4K-2-S11-pol.prn');
% disp(data.Parameters())
data = importdata("RT-2-S11-pol.prn");
freq = data.data(:,1)*1e-9;
S11 = data.data(:,2) + 1j * data.data(:,3);
% %%
% N = length(listing(:,1))
%  for i = 1:1
%     for k = 1:1
%       S(k,i).s11(:) = sparameters(listing(k,i).name).Parameters(1,1,:);
% %       name(k,i,:) = listing(k,i).name;
%     end
%  end
% freq = sparameters(listing(1,1).name).Frequencies*1e-9;
freq = freq * 2 * pi;
freq_plot = freq / (2 * pi);
N = length(freq);

ind_plot_i = 1;
ind_plot_k = 1:1;
figure
for i = ind_plot_i
    for k = ind_plot_k
      subplot(length(ind_plot_i),1,i+1-min(ind_plot_i))
      plot(freq_plot,abs(S11))
      legend show
      hold on
    end
end
%% 
inc = 1;
inr = 1;
%% Initialization of the data to be fitted
% for m = 1:length(inc)
m=1
Rchar = 50;   % internal resistance 50 ohm
% S11 = S(inc(m),inr).s11;   % select the data
S11 = S11./max(abs(S11));
frs = 0.71;     % start of the resonance frequency (GHz)
fre = 0.73;     % end of the resonance (GHz)
ffs = 0.3;     % start of the fitting frequencyng frequency (GHz)
ffe = 1.5;     % end of the fitting (GHz)

frs = 4.2 * 2 * pi;     % start of the resonance frequency (GHz)
fre = 4.7 * 2 * pi;     % end of the resonance (GHz)
ffs = 3 * 2 * pi;     % start of the fitting frequencyng frequency (GHz)
ffe = 8 * 2 * pi;     % end of the fitting (GHz)

Z0ff = zeros(N,1);   % initialize the fitting impedance of the idt without load
Z0 = zeros(N,1);   % initialize the impedance of the idt with load

% Initialize the fitting parameter
Rsf0 = 1e-6;   % Rs fit Initial value
Rlf0 = 2000;
Clf0 = 1e-3;
Lsf0 = 0.8;
% Least square fitting function
S11_bg = S11;
Z0 = Rchar * (1+S11)./(1-S11);
[Rs,Ls,Rl,Ce,Z0f] = Z0_fit(0,freq,Z0,frs,fre,ffs,ffe,Rsf0,Lsf0,Rlf0,Clf0,1.5) ;
Rsp(m) = Rs;
Lsp(m) = Ls;
Rlp(m) = Rl;
Cep(m) = Ce;
Rs_vector(file_iter) = Rs;
Ls_vector(file_iter) = Ls;
Rp_vector(file_iter) = Rl;
Cp_vector(file_iter) = Ce;

% Rs = 1e-10;%Rs;
% Ls = 0.846;%Ls;
% Rl = 1e13;%Rl;
% Ce = 0.00076;%Ce;
ind = find((freq-0).*(freq-fre)<0);
% fit S11 plot
figure('Position',[50 50 600 450],'Color',[1 1 1])
S11_bg = (Z0f-Rchar)./(Z0f+Rchar);
smithplot(S11(ind),'LineWidth',2.5,'FontSize',14,'Color',[0.1216,0.4667,0.7059]);
hold on
smithplot(S11_bg(ind),'LineWidth',2.5,'FontSize',14,'Color',[1,0.498,0.0549]);
% legend('S11','S11 fit')
set(gca,'FontSize',20)
grid on

% plot fitted abs(S11_bg) and real abs(S11) data
figure('Position',[50 50 600 450],'Color',[1 1 1])
plot(freq_plot',abs(S11_bg),'LineWidth',1.5,'Color','#FF4500')
hold on
plot(freq_plot',abs(S11),'LineWidth', 1.5,'Color','#0000CD')
grid on
%% Ya fitting
freq_rad = freq * 2 * pi;
Y = 1./(Z0-Rs-1i*Ls.*freq')-(1/Rl+1i*freq'.*Ce);   
[Rm,Lm,Cm] = Y_fit(freq,Y,frs,fre);
Yf = 1./(Rm+1i.*freq'.*Lm-1i./freq'./Cm);
Z_fit = Rs+1i*Ls.*freq'+1./(1/Rl+1i.*freq'.*Ce+Yf);
% Yf = 1./(Rm+1i.*freq_rad'.*Lm-1i./freq_rad'./Cm);
% Z_fit = Rs+1i*Ls.*freq_rad'+1./(1/Rl+1i.*freq_rad'.*Ce+Yf);
S11_fit = (Z_fit-Rchar)./(Z_fit+Rchar);

Rm_vector(file_iter) = Rm;
Lm_vector(file_iter) = Lm;
Cm_vector(file_iter) = Cm;

%% Fitted S11
figure('Position',[100 100 600 450])
subplot(2,1,1)
plot(freq_plot,real(S11),freq_plot,real(S11_fit),'--')
xlabel('Frequency (GHz)', 'FontSize',16,'FontWeight','bold')
ylabel('S11.Real', 'FontSize',16,'FontWeight','bold')
xlim([4.4,4.65])
subplot(2,1,2)
plot(freq_plot,imag(S11),freq_plot,imag(S11_fit),'--')
xlim([4.4,4.65])
xlabel('Frequency (GHz)', 'FontSize',16,'FontWeight','bold')
ylabel('S11.Imag', 'FontSize',16,'FontWeight','bold')
%% Calculate power
Pin = 1-abs(S11).^2;
Prs = real(Rs./Z0).*Pin;
Prl =  real(Z0-Rs)./real(Z0).*real(1/Rl)./real(1./(Z0-Rs)).*Pin;
Pyb =  real(Z0-Rs)./real(Z0).*real(Yf)./real(1./(Z0-Rs)).*Pin;
% Prl =  real(1/Rl).*real(Z0).*abs(1-Rs./Z0).^2.*Pin;
% Pyb = real(Y).*real(Z0).*abs(1-Rs./Z0).^2.*Pin;
ind = find(freq<3);
Pyb_max(m) = max(Pyb(ind));
% end
% 
%% PLOT
figure('Position',[100 100 600 450])
set(gcf,'defaultAxesColorOrder',[[0,0,0]; [0,0,0]]);
% yyaxis left
subplot(2,1,1)
plot(freq_plot,abs(S11),'LineWidth',1.5,'Color',[1,1,1].*0.7)
hold on
plot(freq_plot,abs(S11_fit),'--','LineWidth',1.5,'Color','#015c92')
legend('Measured','Fitted')
ylabel('|S11| (a.u.)')
xlabel('Frequency (GHz)')
% xlim([frs/(2*pi),fre/(2*pi)])
grid on
% set(gca,'FontSize',12,'FontName','Arial')
% subplot(2,1,2)
% plot(freq_plot,Pyb.*100,'LineWidth',1.5,'Color','#f27f0b')
% hold on
% plot(freq_plot,Prs.*100,'LineWidth',1.5,'Color',[1,1,1].*0.5)
% legend('P_Y','P_{Rs}')
% xlim([frs/(2*pi),fre/(2*pi)])
% xlabel('Frequency (GHz)');
% ylabel('Efficiency (%)')
% set(gca,'FontSize',12,'FontName','Arial')
% grid on
% %%
% fpair = 30:30:300;
% figure
% subplot(4,1,1)
% plot(fpair,flip(Rsp),'.-','MarkerSize',15)
% ylabel('Rs (Ohm)')
% xticklabels([]);
% set(gca,'FontSize',12,'FontName','Arial')
% subplot(4,1,2)
% plot(fpair,flip(Rlp),'.-','MarkerSize',15)
% yllot(4,1,3)
% plotabel('Rl (Ohm)')
% xticklabels([]);
% set(gca,'FontSize',12,'FontName','Arial')
% subp(fpair,flip(Cep),'.-','MarkerSize',15)
% ylabel('Ce (nF)')
% set(gca,'FontSize',12,'FontName','Arial')
% subplot(4,1,4)
% plot(fpair,flip(Pyb_max.*100),'.-','MarkerSize',15)
% ylabel('Efficiency (%)')
% set(gca,'FontSize',12,'FontName','Arial')
% xlabel('IDT finger (pair)')
% end
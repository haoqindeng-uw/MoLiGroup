%% Data import
listing(:,1) = dir('B0.s2p');
N = length(listing(:,1))
 for i = 1:1
    for k = 1:1
      S(k,i).s11(:) = sparameters(listing(k,i).name).Parameters(1,1,:);
%       name(k,i,:) = listing(k,i).name;
    end
 end
freq = sparameters(listing(1,1).name).Frequencies*1e-9; %convert to GHz; shape: (20001, 1)
N = length(freq); % N=20001
disp('N (number of freq points)');
disp(N);
%% Data import
ind_plot_i = 1;
ind_plot_k = 1:1;
disp(ind_plot_k);
%% Data import
figure
for i = ind_plot_i
    for k = ind_plot_k
      subplot(length(ind_plot_i),1,i+1-min(ind_plot_i))
      plot(freq,abs(S(k,i).s11(:)))
      legend show
      hold on
    end
end
%% 
inc = 1;
inr = 1;
%% Initialization of the data to be fitted
for m = 1:length(inc)
Rchar = 50;   % internal resistance 50 ohm
S11 = S(inc(m),inr).s11;   % select the data
% disp('before normalization:');
% disp(max(abs(S11)));
S11 = S11./max(abs(S11)); % normalize S11 data by 1.0192, same as I-Tung's code
% disp('after normalization:');
% disp(max(abs(S11)));
frs = 0.71;     % start of the resonance frequency (GHz)
fre = 0.74;     % end of the resonance (GHz)
ffs = 0.3;     % start of the fitting frequencyng frequency (GHz)
ffe = 1.5;     % end of the fitting (GHz)
Z0ff = zeros(N,1);   % initialize the fitting impedance of the idt without load
Z0 = zeros(N,1);   % initialize the impedance of the idt with load

% Initialize the fitting parameter
Rsf0 = 1e-6;   % Rs fit Initial value
Rlf0 = 2000;
Clf0 = 1e-3;
Lsf0 = 0.8;

% Try different initial parameter
Rsf0 = 1e-9;   % Rs fit Initial value
Rlf0 = 2000;
Clf0 = 1e-9;
Lsf0 = 0.8;
% Least square fitting function
S11_bg = S11;
Z0 = Rchar * (1+S11)./(1-S11); % convert S11 to impedance, same as I-Tung's code. shape: (1, 20001)
[Rs,Ls,Rl,Ce,Z0f] = Z0_fit(0,freq,Z0,frs,fre,ffs,ffe,Rsf0,Lsf0,Rlf0,Clf0,1.5) ; % returns parameters[Rs, Ls, Rp, Cp] and Z0f(fitted impedance)
Rsp(m) = Rs;
Lsp(m) = Ls;
Rlp(m) = Rl;
Cep(m) = Ce;

% Rs = 1e-10;%Rs;
% Ls = 0.846;%Ls;
% Rl = 1e13;%Rl;
% Ce = 0.00076;%Ce;
ind = find((freq-0).*(freq-fre)<0);
% fit S11 plot
figure('Position',[50 50 600 450],'Color',[1 1 1])
S11_bg = (Z0f-Rchar)./(Z0f+Rchar); % converted Z0f (fitted Z0) back to S11
smithplot(S11(ind),'LineWidth',2.5,'FontSize',14,'Color',[0.1216,0.4667,0.7059]);
hold on
smithplot(S11_bg(ind),'LineWidth',2.5,'FontSize',14,'Color',[1,0.498,0.0549]);
% legend('S11','S11 fit')
set(gca,'FontSize',20)
grid on

% plot fitted abs(S11_bg) and real abs(S11) data
figure('Position',[50 50 600 450],'Color',[1 1 1])
plot(freq',abs(S11_bg),'LineWidth',1.5,'Color','#FF4500')
hold on
plot(freq',abs(S11),'LineWidth', 1.5,'Color','#0000CD')
grid on
%% Ya fitting
freq_rad = freq * 2 * pi;
Y = 1./(Z0-Rs-1i*Ls.*freq_rad')-(1/Rl+1i*freq_rad'.*Ce); % same as formula; different from I-Tung's implementation.
[Rm,Lm,Cm] = Y_fit(freq,Y,frs,fre);
Yf = 1./(Rm+1i.*freq_rad'.*Lm-1i./freq_rad'./Cm);
Z_fit = Rs+1i*Ls.*freq_rad'+1./(1/Rl+1i.*freq_rad'.*Ce+Yf);
S11_fit = (Z_fit-Rchar)./(Z_fit+Rchar);
%% Fitted S11
figure('Position',[100 100 600 450])
subplot(2,1,1)
plot(freq,real(S11),freq,real(S11_fit),'--')

xlim([frs,fre])
subplot(2,1,2)
plot(freq,imag(S11),freq,imag(S11_fit),'--')
xlim([frs,fre])
%% Calculate power
Pin = 1-abs(S11).^2;
Prs = real(Rs./Z0).*Pin;
Prl =  real(Z0-Rs)./real(Z0).*real(1/Rl)./real(1./(Z0-Rs)).*Pin;
Pyb =  real(Z0-Rs)./real(Z0).*real(Yf)./real(1./(Z0-Rs)).*Pin;
% Prl =  real(1/Rl).*real(Z0).*abs(1-Rs./Z0).^2.*Pin;
% Pyb = real(Y).*real(Z0).*abs(1-Rs./Z0).^2.*Pin;
ind = find(freq<3);
Pyb_max(m) = max(Pyb(ind));
end

%% PLOT
figure('Position',[100 100 600 450])
set(gcf,'defaultAxesColorOrder',[[0,0,0]; [0,0,0]]);
% yyaxis left
subplot(2,1,1)
plot(freq,abs(S11),'LineWidth',1.5,'Color',[1,1,1].*0.7)
hold on
plot(freq,abs(S11_fit),'--','LineWidth',1.5,'Color','#015c92')
legend('Measured','Fitted')
ylabel('|S11| (a.u.)')
xlim([frs,fre])
grid on
set(gca,'FontSize',12,'FontName','Arial')
subplot(2,1,2)
plot(freq,Pyb.*100,'LineWidth',1.5,'Color','#f27f0b')
hold on
plot(freq,Prs.*100,'LineWidth',1.5,'Color',[1,1,1].*0.5)
legend('P_Y','P_{Rs}')
xlim([frs,fre])
xlabel('Frequency (GHz)');
ylabel('Efficiency (%)')
set(gca,'FontSize',12,'FontName','Arial')
grid on
%%
fpair = 30:30:300;
figure
subplot(4,1,1)
plot(fpair,flip(Rsp),'.-','MarkerSize',15)
ylabel('Rs (Ohm)')
xticklabels([]);
set(gca,'FontSize',12,'FontName','Arial')
subplot(4,1,2)
plot(fpair,flip(Rlp),'.-','MarkerSize',15)
ylabel('Rl (Ohm)')
xticklabels([]);
set(gca,'FontSize',12,'FontName','Arial')
subplot(4,1,3)
plot(fpair,flip(Cep),'.-','MarkerSize',15)
ylabel('Ce (nF)')
set(gca,'FontSize',12,'FontName','Arial')
subplot(4,1,4)
plot(fpair,flip(Pyb_max.*100),'.-','MarkerSize',15)
ylabel('Efficiency (%)')
set(gca,'FontSize',12,'FontName','Arial')
xlabel('IDT finger (pair)')
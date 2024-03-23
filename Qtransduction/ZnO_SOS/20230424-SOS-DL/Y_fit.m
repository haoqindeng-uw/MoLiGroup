function [Rm,Lm,Cm]=Y_fit(freq0,Y,frs,fre)
indr = find((freq0-frs).*(freq0-fre)<0);
ReY = real(Y(indr));
ImY = imag(Y(indr));
freq = freq0(indr);

wr = freq(find(ReY==max(ReY)));
wl = freq(find(ImY==min(ImY)));

Rm0 = 1/max(ReY);   %ohm
Lm0 = Rm0*wl/(wl^2-wr^2);    %nH
Cm0 = 1/Lm0/wr^2; 

yft = @(v,xdata)yrcl(v,xdata);
cplf(:,1) = ReY;
cplf(:,2) = ImY;
x0 = [Rm0;Lm0;Cm0]; % arbitrary initial guess
[v] = lsqcurvefit(yft,x0,freq',cplf);
Rm = v(1);
Lm = v(2);
Cm = v(3);
Yf = 1./(Rm+1i.*freq'.*Lm-1i./freq'./Cm);
figure('Position',[100 100 600 450])
subplot(1,2,1)
plot(freq/(2*pi),ReY,freq/(2*pi),real(Yf),'--');
ylabel('Re(Y)')
xlabel('Frequency (GHz)')
% xlim([min(freq)/ (2*pi),max(freq)/ (2*pi)])
grid on
subplot(1,2,2)
plot(freq/(2*pi),ImY,freq/(2*pi),imag(Yf),'--');
ylabel('Im(Y)')
xlabel('Frequency (GHz)')
% xlim([min(freq)/ (2*pi),max(freq)/ (2*pi)])
grid on
['Rm = ' num2str(Rm), ' ohm, Lm = ' num2str(Lm/2/pi), ' nH, Cm = ' num2str(Cm/2/pi),' nF']
return
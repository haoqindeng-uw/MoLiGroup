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
freq_rad = freq * 2 * pi;
Yf = 1./(Rm+1i.*freq_rad'.*Lm-1i./freq_rad'./Cm);
figure('Position',[100 100 600 450])
subplot(1,2,1)
plot(freq,ReY,freq,real(Yf),'--');
ylabel('Re(Y)')
xlabel('Frequency (GHz)')
xlim([min(freq),max(freq)])
grid on
subplot(1,2,2)
plot(freq,ImY,freq,imag(Yf),'--');
ylabel('Im(Y)')
xlabel('Frequency (GHz)')
xlim([min(freq),max(freq)])
grid on
['Rm = ' num2str(Rm), ' ohm, Lm = ' num2str(Lm/2/pi), ' nH, Cm = ' num2str(Cm/2/pi),' nF']
return
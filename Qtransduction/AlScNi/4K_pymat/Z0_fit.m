function [Rsf,Lsf,Rlf,Cef,Z0f, z0_real] = Z0_fit(p,freq0,Z0,frs,fre,ffs,ffe,Rsf0,Lsf0,Rlf0,Clf0,lw) 
indr = find((freq0-frs).*(freq0-fre)<0);
indb = find((freq0-ffs).*(freq0-ffe)<0);

Z0ff = Z0;
Z0ff(indr) = linspace(Z0(min(indr)),Z0(max(indr)),length(indr));
freq = freq0(indb);
Ref = real(Z0ff(indb));
Imf = imag(Z0ff(indb));
z0ft = @(v,xdata)rcbg(v,xdata);
cplf(:,1) = Ref;
cplf(:,2) = Imf;
x0 = [Rsf0;Rlf0;Clf0;Lsf0]; % arbitrary initial guess
[v] = lsqcurvefit(z0ft,x0,freq',cplf);

freq0_plot = freq0 / (2*pi);
% 
% % Fitting with real part
% Re_fit = fittype('c+x*b/(1+x^2*a^2*b^2)');
% Reft1 = fit(freq,Ref',Re_fit,'StartPoint',[Clf0,Rlf0,Rsf0],'Lower',[0 0 0]);
% Clf1 = Reft1.a;
% Rlf1 = Reft1.b;
% Rsf = Reft1.c;
% % Fitting with imaginary part
% Im_fit = fittype('-x*a*b^2/(1+x^2*b^2*a^2)');
% Imft1 = fit(freq,Imf',Im_fit,'StartPoint',[Clf0,Rlf0],'Lower',[0 0]);
% Clf = Imft1.a;
% Rlf = Imft1.b;
Rsf = v(1);
Rlf = v(2);
Cef = v(3);
Lsf = v(4);
% Calculate fit Z0
Z0f = Rsf + Rlf./(1+1i*freq0'.*Cef*Rlf)+1i.*freq0'.*Lsf;
z0_real = z_real(v, freq0');
% disp(z0_real)
% disp(z0_real);
% fit z0 plot
if p==0
figure('Position',[100 100 600 450])
x = freq0';
x_plot = x / (2*pi);
y1 = -x.*Cef*Rlf^2./(1+x.^2*Cef^2*Rlf^2)+x.*Lsf;
% y2 = Rsf+x.*Rlf./(1+x.^2*Cef^2*Rlf^2);
y2 = Rsf+Rlf./(1+x.^2*Cef^2*Rlf^2);
% y2 = real(Z0f);
subplot(2,1,1)
plot(freq0_plot',real(Z0),'LineWidth',lw,'Color','#FF4500')
hold on
plot(x_plot,y2,'LineWidth',lw,'Color','#0000CD')
grid on
legend('Re(Z_0)','Re(Z_0 fit)')
xlabel('Frequency (GHz)')
ylabel('Impedance (\Omega)')
set(gca,'FontSize',14)
ylim([0,100])
subplot(2,1,2)
plot(freq0_plot',imag(Z0),'LineWidth',lw,'Color','#FF4500')
hold on
plot(x_plot,y1,'LineWidth',lw,'Color','#0000CD')
grid on
legend('Im(Z_0)','Im(Z_0 fit)')
xlabel('Frequency (GHz)')
ylabel('Impedance (\Omega)')
set(gca,'FontSize',14)
ylim([-100,100])
['Rs = ' num2str(Rsf),' ohm, Ls = ' num2str(Lsf),' nH, Rl = ' num2str(Rlf),' ohm, Cl = ' num2str(Cef),' nF']
end
return 
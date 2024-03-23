function [Rsf,Lsf,Rlf,Cef,Z0f] = Z0_fit(p,freq0,Z0,frs,fre,ffs,ffe,Rsf0,Lsf0,Rlf0,Clf0,lw) 
indr = find((freq0-frs).*(freq0-fre)<0); % shape: (400, 1), [9466-9865]
indb = find((freq0-ffs).*(freq0-ffe)<0); % shape: (17336, 1), [2665-20000]
% disp('indr/indb shape: ');
% disp(indr);
% disp(indb);
Z0ff = Z0; %Z0ff copies Z0 (original data), then fill&smoothen the dip/peak to obtain background
Z0ff(indr) = linspace(Z0(min(indr)),Z0(max(indr)),length(indr)); 
freq = freq0(indb); % freq.shape: (17336, 1)
% disp('freq shape:');
% disp(size(freq));
Ref = real(Z0ff(indb));
Imf = imag(Z0ff(indb));
z0ft = @(v,xdata)rcbg(v,xdata); % this function is consistent with formula and I-Tung's code (I-Tung use .real/imag to extract real&imag parts of impedence)
% stack real&imag part of Z0ff (smoothened original data) as fitting target
cplf(:,1) = Ref; % cplf.shape: (17336, 2)
cplf(:,2) = Imf;
% disp('cplf shape:');
% disp(size(cplf));
x0 = [Rsf0;Rlf0;Clf0;Lsf0]; % arbitrary initial guess
[v] = lsqcurvefit(z0ft,x0,freq',cplf); %z0ft: formula; x0: parameters; freq': xdata; cplf: fitting target;
disp('v:')
disp(v(1));
disp(v(2));
disp(v(3));
disp(v(4));
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
freq0_rad = freq0 * 2 * pi; % w=2*pi*f
Z0f = Rsf + Rlf./(1+1i*freq0_rad'.*Cef*Rlf)+1i.*freq0_rad'.*Lsf; % this function is consistent with formula and I-Tung's code, expecpt for missing 2pi constant
% disp('Z0f shape:');
% disp(size(Z0f));
% disp('freq0 shape');
% disp(size(freq0))
% fit z0 plot
if p==0
figure('Position',[100 100 600 450])
x = freq0_rad';
y1 = -x.*Cef*Rlf^2./(1+x.^2*Cef^2*Rlf^2)+x.*Lsf;
y2 = Rsf+x.*Rlf./(1+x.^2*Cef^2*Rlf^2);
subplot(2,1,1)
plot(freq0',real(Z0),'LineWidth',lw,'Color','#FF4500')
hold on
plot(x,y2,'LineWidth',lw,'Color','#0000CD')
grid on
legend('Re(Z_0)','Re(Z_0 fit)')
xlabel('Frequency (GHz)')
ylabel('Impedance (\Omega)')
set(gca,'FontSize',14)
ylim([0,100])
subplot(2,1,2)
plot(freq0',imag(Z0),'LineWidth',lw,'Color','#FF4500')
hold on
plot(x,y1,'LineWidth',lw,'Color','#0000CD')
grid on
legend('Im(Z_0)','Im(Z_0 fit)')
xlabel('Frequency (GHz)')
ylabel('Impedance (\Omega)')
set(gca,'FontSize',14)
ylim([-100,100])
['Rs = ' num2str(Rsf),' ohm, Ls = ' num2str(Lsf),' nH, Rl = ' num2str(Rlf),' ohm, Cl = ' num2str(Cef),' nF']
end
return 
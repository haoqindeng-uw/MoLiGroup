function yout = cplxya(v,xdata)

%% v=[dx,dy,ga,ba]
dx = v(1);
dy = v(2);
ga = v(3);
ba = v(4);

yout = zeros(length(xdata),2); % allocate yout

yout(:,1) = dx+ga./(ga+xdata.^2*ba^2);
yout(:,2) = dy-xdata*ba./(ga+xdata.^2*ba^2);
end


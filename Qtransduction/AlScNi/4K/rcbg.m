function zout = rcbg(v,xdata)
zout = zeros(length(xdata),2); % zout.shape: (17336, 2); xdata.shape: (1, 17336)---xdata is freq'
xdata = xdata * 2 * pi;
% disp('xdata shape:');
% disp(xdata);
zout(:,1) = v(1) + v(2)./(1+(xdata.*v(2).*v(3)).^2);
zout(:,2) = -(xdata.*v(2).^2.*v(3))./(1+(xdata.*v(2).*v(3)).^2)+xdata.*v(4);
end
function zout = yrcl(v,xdata)
zout = zeros(length(xdata),2);
xdata = xdata * 2 * pi;
zout(:,1) = v(1)./(v(1)^2+(xdata.*v(2)-1./(xdata.*v(3))).^2);
zout(:,2) = -(xdata.*v(2)-1./(xdata.*v(3)))./(v(1)^2+(xdata.*v(2)-1./(xdata.*v(3))).^2);
end
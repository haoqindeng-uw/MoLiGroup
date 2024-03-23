function zout = rcbg(v,xdata)
    zout = zeros(length(xdata),2);
    zout(:,1) = v(1) + v(2)./(1+(xdata.*v(2).*v(3)).^2);
    zout(:,2) = -(xdata.*v(2).^2.*v(3))./(1+(xdata.*v(2).*v(3)).^2)+xdata.*v(4);
end

% function z_real = z_real(v, xdata)
%     z_real = v(1) + v(2)./(1+(xdata.*v(2).*v(3)).^2);
% end

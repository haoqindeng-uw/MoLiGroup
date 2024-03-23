function z_real = z_real(v, xdata)
    z_real = v(1) + v(2)./(1+(xdata.*v(2).*v(3)).^2);
end

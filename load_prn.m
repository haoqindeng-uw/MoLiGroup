function [S11, freq] = load_prn(file_name)
    % data = importdata("RT-2-S11-pol.prn");
    data = importdata(file_name);
    freq = data.data(:,1);
    S11 = data.data(:,2) + 1j * data.data(:,3);
end

% S11, freq = load_prn("RT-2-S11-pol.prn");
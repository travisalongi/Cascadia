% t.alongi 2018-12-03
% want to look at completeness of antelope catalog vs simulPS catalog
clear; close all; clc

d = readtable('/auto/home/talongi/Cascadia/Data_tables/Events/compare_ant2simPS_merge2.txt');
a = readtable('/auto/home/talongi/Cascadia/Data_tables/Events/NC_Events.txt');

%r- relocated in simulPS
slon = d.simps_lon;
slat = d.simps_lat;
sdepth = d.simps_depth;
smag = d.mag;

%nc- are original ant locations --- making existing code work w/o changing
%alot of var names.
nclon = d.ant_lon;
nclat = d.ant_lat;
ncdepth = d.ant_depth;
amag = a.Var5;

fn = 'STIX';

%create histogram of magnitudes - binwidth = 0.1
%histogram(M,'BinWidth',0.1)
 
%histcount is like histogram, but outputs 
% ======= our data =======
[N,mag_edges] = histcounts(smag,'BinWidth',0.3);
N = cumsum(N,'reverse'); %gr is n < m

%need to omit the zeros from the array before applying log10
%find   Find indices of nonzero elements.
index_array = find(N);
%use index_arrray to mask off and only use nonzero elements
log_N = log10(N(index_array));  % take log10 of nonzero elements
mag_masked = mag_edges(index_array);    % apply index array to mag_edges

completeness = 1.5; % by visual inspection of plot
compl_mask = mag_masked >= completeness;
[pf] = polyfit(mag_masked(compl_mask), log_N(compl_mask), 1);
%make equation of line out of polyfit outputs 
% 1st element of pf is slope/ 2nd element is intercept
y = mag_edges.*pf(1) + pf(2); % create equation of line with polyfit data



% ======= NCevents =========
[N_nc, mag_edges_nc] = histcounts(amag,'BinWidth',0.3);
N_nc = cumsum(N_nc,'reverse'); 

%need to omit the zeros from the array before applying log10
%find   Find indices of nonzero elements.
index_array_nc = find(N_nc);
%use index_arrray to mask off and only use nonzero elements
log_N_nc = log10(N_nc(index_array_nc));  % take log10 of nonzero elements
mag_masked_nc = mag_edges_nc(index_array_nc);    % apply index array to mag_edges

completeness_nc = 1.8; % by visual inspection of plot
max_mag = 4.8; 
compl_mask = mag_masked_nc >= completeness & mag_masked_nc <= max_mag;

[pf_nc] = polyfit(mag_masked(compl_mask), log_N(compl_mask), 1);
%make equation of line out of polyfit outputs 
% 1st element of pf is slope/ 2nd element is intercept
y_nc = mag_edges_nc .*pf_nc(1) + pf_nc(2); % create equation of line with polyfit data

 

%make plot
figure(1)
title('Gutenburg-Richter Relation','fontsize',18, 'FontName', fn)
% subplot(1,2,1)
p1 = plot(mag_masked,log_N,'ko','MarkerSize',8, 'MarkerFaceColor','k');, hold on
p2 = plot(mag_edges,y,'r:','LineWidth',3);
l = legend('Our Data','Best-fit');
l.FontName = fn

xlabel('Magnitude','fontsize',16, 'FontName', fn)
ylabel('Log(Number of Events)','fontsize',16, 'FontName',fn)

%ylim([0 max(log_N)])
text(1,0.25,sprintf('B value = %2.2f', (pf(1))), 'FontName',fn)
text(1,0, sprintf('Completeness ~ %2.1f', completeness), 'FontName', fn)

axis equal
grid on
 



% subplot(1,2,2)
% p1 = plot(mag_masked_nc,log_N_nc,'ko','MarkerSize',8, 'MarkerFaceColor','k');, hold on
% p2 = plot(mag_edges_nc,y_nc,'r:','LineWidth',3);
% l = legend('NCSN','Best-fit');
% l.FontName = fn
% 
% xlabel('Magnitude','fontsize',16, 'FontName', fn)
% ylabel('Log(Number of Events)','fontsize',16, 'FontName',fn)
% 
% %ylim([0 max(log_N)])
% text(1,0.25,sprintf('B value = %2.2f', (pf_nc(1))), 'FontName',fn)
% text(1,0, sprintf('Completeness ~ %2.1f', completeness_nc), 'FontName', fn)
% 
% axis equal
% grid on

hold off
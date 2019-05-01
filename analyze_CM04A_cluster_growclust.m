%T. Alongi
% 2018-10-31

% Purpose: want to make a Magnitude vs Time plot for cluster of seismicity
% located near station CM04A
% modified for growclust
% code for AGU figures at bottom of script

clear; clc; clf; close all;

%import norcalshoreline 
shpfile = '~/Cascadia/Data_tables/USGS_Base_Layer/NOS80k.shp';
shore = shaperead(shpfile);

%gridfile
grd = load('~/Cascadia/Data_tables/cascadia_grid.xyz~');

%growclust data
d = readtable('~/Cascadia/Data_tables/Events/growclust_cat_run3.txt');
    yr = d.Var1;
    mo = d.Var2;
    dy = d.Var3;
    hr = d.Var4;
    mn = d.Var5;
    sec = d.Var6;

    lat = d.Var8;
    lon = d.Var9;
    depth = d.Var10;
    mag = d.Var11;
    
    evid = d.Var7;

    date_matrix = [yr, mo, dy, hr, mn, sec];
    events_datetime = datetime(date_matrix);
    events_date_num = datenum(date_matrix);

% find template events 1366, 1190, 1429
tmp_1366 = find(evid == 1366);
tmp_1190 = find(evid == 1190);
tmp_1429 = find(evid == 1429);
    
%rectangle coordinates for CM04A cluster
x1 = -124.15;
x2 = -124;
y1 = 40.63;
y2 = 40.55;
    x = [x1 x2 x2 x1 x1];
    y = [y1 y1 y2 y2 y1];
    
%xsection
% cross-section 1
x1sec_lon = [-124.8, -123.78]; x1sec_lat = [40.85, 40.48];

% cross-section 2
x2sec_lon = [-124.8, -123.75];   x2sec_lat = [40.5, 40.22];

fn = 'STIX';
f1 = figure('rend','painters','pos',[10 10 700 1000]);
subplot(2,1,1)
    %plot grid
    scatter(grd(:,1),grd(:,2),'kp'); hold on
    axis equal

    %plot shore
    plot(shore.X,shore.Y,'color',rgb('DarkBlue'),'LineWidth',1.5)

    %plot events
    mag_scaled = 4.^mag+1; %scale magnitude marker
    s = scatter(lon,lat,mag_scaled,events_date_num,'filled'); hold on
        s.MarkerFaceAlpha = 0.7
        colormap hot
        c = colorbar;
        colorbar_label_vect = c.TickLabels;
        cbdate %function that converts datenum to dates for colorbar
        
    %plot templates
    plot(lon(tmp_1190), lat(tmp_1190), '*', 'color',rgb('green'), 'MarkerSize', 10)

    %plot xsection
    plot(x1sec_lon, x1sec_lat, 'k'); 
        text(x1sec_lon(1), x1sec_lat(1) + 0.03, 'A')
        text(x1sec_lon(2), x1sec_lat(2) + 0.03, "A'")
        
    
    plot(x2sec_lon, x2sec_lat, 'k')
        text(x2sec_lon(1), x2sec_lat(1) + 0.03, 'B')
        text(x2sec_lon(2), x2sec_lat(2) + 0.03, "B'")    
    
    %plot box to enlarge
    box_color = rgb('Turquoise')
    plot(x,y,'color',box_color,'LineWidth',3)
        
    grid on
    set(gca,'color', rgb('PaleTurquoise')) %setback ground color using rgb function
    
    % set plot size
        lonlim = [-125 -123.3]; latlim = [40 41];
        xlim(lonlim);
        ylim(latlim);
        xlabel('Longitude')
        ylabel('Lattitude')

    
    
    
subplot(2,1,2)
    %plot events
    mag_scaled = 50*mag+1; %scale magnitude marker
    s = scatter(lon,lat,mag_scaled,events_date_num,'filled'); hold on
        s.MarkerFaceAlpha = 0.7
        s.MarkerEdgeColor = [.5 .5 .5]
        colormap jet 
        c = colorbar;
        colorbar_label_vect = c.TickLabels;
        cbdate %function that converts datenum to dates for colorbar
        
    %plot xsection
    plot(x1sec_lon, x1sec_lat, 'k'); 
        text(x1sec_lon(1), x1sec_lat(1) + 0.03, 'A')
        text(x1sec_lon(2), x1sec_lat(2) + 0.03, "A'")    
        
        
    axis equal
    grid on
    set(gca,'color', rgb('Seashell')) %setback ground color using rgb function
    
    %plot box to enlarge
    plot(x,y, 'color',box_color ,'LineWidth',5)
    
    % set plot size
        xlim([-124.15 -124]) %different plot limits for cluster
        ylim([40.55 40.63])
        xlabel('Longitude')
        ylabel('Lattitude')
    


%% Stem Plots

% make the mask
lonlimits = [-125.15, -124];
latlimits = [40.54, 40.63];
    mask = lon > -124.15 & lon < -124 & lat > 40.54 & lat < 40.63;

f2 = figure(2);
% set colors
coloralldata = rgb('Black');
colorcluster = rgb('DarkOrange');
clusterfacecolor = rgb('BurlyWood');

% set x-axis limit
xlimit = [min(events_datetime) max(events_datetime)];
ylimit = [0 5.5];

ax1 = subplot(3,1,1); % All data
    stem(events_datetime, mag,...
    'color',coloralldata,'MarkerFaceColor',rgb('LightSlateGray')); hold on
    
    stem(events_datetime(mask), mag(mask),...
        'color',colorcluster,'MarkerFaceColor',clusterfacecolor)
    
    title('All Events')
    ylabel('Magnitude')
    xlim(xlimit); ylim(ylimit);
    grid on


ax2 = subplot(3,1,2); 
    stem(events_datetime(mask), mag(mask),'color',colorcluster,'MarkerFaceColor',clusterfacecolor)
    
    title('Magnitudes - CM04A Event Cluster')
    ylabel('Magnitude')
    xlim(xlimit); ylim(ylimit);
    grid on
    
    
ax3 = subplot(3,1,3)
    plot(events_datetime(mask),-depth(mask),'d','color',colorcluster, 'MarkerFaceColor', clusterfacecolor)
    
    xlim(xlimit)
    ylim([-40, 0])
    title('Depth - CM04A Event Cluster')
    ylabel('Depth [km]')
    grid on
    
set(ax1,'color', rgb('Seashell')); %setback ground color using rgb function
set(ax2,'color', rgb('PaleTurquoise')); %setback ground color using rgb function
set(ax3,'color', rgb('PaleTurquoise')); %setback ground color using rgb function







%% Write CM04 cluster to txt file

%make new mask for david to make focal mechs -- similar to above + depth
%these events are likely on interface
d_mask = lon > -124.15 & lon < -124 & lat > 40.54 & lat < 40.63 & depth > 28 & depth <12;

%apply mask to database
cluster_data = data(d_mask,:);
cld = cluster_data;

cluster_data_formated = [cld(:,1), cld(:,2), cld(:,3), cld(:,4), cld(:,5), cld(:,6) cld(:,7) cld(:,8) cld(:,9) cld(:,18)]


fname='cm04_cluster_growclust.txt';
fid=fopen(fname,'w');

header = "YEAR    MO  DY  HR  MN   Sec    Lat     Long        Depth   Mag \n"; %in simulPS format
fprintf(fid, header);

% snippet of code found online, prints matrix to a file
for ii = 1:size(cluster_data,1)
    fprintf(fid,'%g\t',cluster_data_formated(ii,:));
    fprintf(fid,'\n');
end

fclose(fid);


%%


%% Single plot of subplot
figure(8008)


%plot of inset only
mag_scaled = 60*(mag+1); %scale magnitude marker
s = scatter(lon,lat,mag_scaled,events_date_num,'filled'); hold on
    s.MarkerFaceAlpha = 0.3
    s.MarkerEdgeColor = [.3 .3 .3]
    colormap jet 
    c = colorbar;
    c.FontName = fn
    colorbar_label_vect = c.TickLabels;
    cbdate %function that converts datenum to dates for colorbar
    

axis equal
grid on
%plot templates
pt1 = plot(lon(tmp_1190), lat(tmp_1190), 'dg',  'MarkerSize', 15);   
pt2 = plot(lon(tmp_1429), lat(tmp_1429), 'dr',  'MarkerSize', 15);

pt1.MarkerFaceColor = rgb('Green')
pt2.MarkerFaceColor = rgb('darkred')

%plot box to enlarge
plot(x,y, 'color',box_color ,'LineWidth',5)

% set plot size
    xlim([-124.15 -124]) %different plot limits for cluster
    ylim([40.55 40.63])
    xlabel('Longitude','FontName',fn)
    ylabel('Lattitude','FontName',fn)
    
set(gca,  'FontSize', 16, 'FontName','STIX', 'FontWeight','normal')
set(gca,'color', rgb('OldLace')) %setback ground color using rgb function
    
hold off




%% Stem Plots - AGU

% make the mask
lonlimits = [-125.15, -124];
latlimits = [40.55, 40.63];
    mask = lon > -124.15 & lon < -124 & lat > 40.54 & lat < 40.63;

f2 = figure(2);
% set colors
coloralldata = rgb('Black');
colorcluster = rgb('DarkOrange');
clusterfacecolor = rgb('BurlyWood');

% set x-axis limit
xlimit = [min(events_datetime) max(events_datetime)];
ylimit = [0 4];

% =========== omitting all data plot =====================
% ax1 = subplot(3,1,1); % All data
%     stem(events_datetime, mag,...
%     'color',coloralldata,'MarkerFaceColor',rgb('LightSlateGray')); hold on
%     
%     stem(events_datetime(mask), mag(mask),...
%         'color',colorcluster,'MarkerFaceColor',clusterfacecolor)
%     
%     title('All Events')
%     ylabel('Magnitude')
%     xlim(xlimit); ylim(ylimit);
%     grid on


ax2 = subplot(2,1,1); 
    stem(events_datetime(mask), mag(mask),'color',colorcluster,'MarkerFaceColor',clusterfacecolor); hold on
    
    %plot templates
    stem(events_datetime(tmp_1190), mag(tmp_1190), 'MarkerFaceColor', rgb('Green'))
    stem(events_datetime(tmp_1429), mag(tmp_1429), 'MarkerFaceColor', rgb('Red'))
    
    title('Cluster - Event Magnitudes' ,'FontName',fn,'Fontsize',18)
    ylabel('Magnitude', 'FontName', fn,'Fontsize',16)
    xlim(xlimit); ylim(ylimit);
    grid on
hold off  
    
ax3 = subplot(2,1,2);
    plot(events_datetime(mask),-depth(mask),'o','color',colorcluster, 'MarkerFaceColor', clusterfacecolor); hold on
    
    %plot templates
    stem(events_datetime(tmp_1190), -depth(tmp_1190), 'MarkerFaceColor', rgb('Green') ,'color', rgb('green'))
    stem(events_datetime(tmp_1429), -depth(tmp_1429), ...
        'MarkerFaceColor', rgb('Red'), 'color', rgb('red'))
    
    xlim(xlimit)
    ylim([-30, -5])
    title('Cluster - Event Depths','FontName',fn,'Fontsize',18)
    ylabel('Depth [km]','FontName',fn,'Fontsize',16)
    grid on
    
%set(ax1,'color', rgb('Seashell')); %setback ground color using rgb function
set(ax2,'color', rgb('PaleTurquoise'),'FontName',fn,'Fontsize',12); %setback ground color using rgb function
set(ax3,'color', rgb('PaleTurquoise'),'FontName',fn,'Fontsize',12); %setback ground color using rgb function

hold off

%%
% trying to make a map that looks better ** code from pvf plot I made
% 7/2018
% == Build Map  ==
% region limits
% * setabove

% background color
figure('Color',[.95 .9 .8])

% create map
ax = usamap(latlim,lonlim);

% create state
states = shaperead('usastatehi.shp',...
    'UseGeoCoords', true, 'BoundingBox', [lonlim', latlim']);

% create colors for states
faceColors = makesymbolspec('Polygon',...
    {'INDEX', [1 numel(states)], ...
    'FaceColor', polcmap(numel(states))});

% plot
geoshow(ax, states, 'SymbolSpec', faceColors)

% sr = scaleruler; %scale
setm(scaleruler, 'Lat', 40.11,'Long', -118)   % location of sclae

setm(gca,'Flinewidth',4,'fontsize',14) % larger frame and fonts
northarrow('latitude', 33.9, 'longitude', -118.6) % add North Arrow

c = 'color';
ms = 'MarkerSize';
lw = 'LineWidth';
% plot pvf fault
% plotm(fault_lat, fault_lon,'r:',lw,6)
% textm(33.90,-118.46,'PVF','FontSize',20,'Color','red','Rotation',-37)

% plot all events with small dots
plotm(lat, lon, '.k')
scatter(lat,lon,mag_scaled)

% plot completeness events with circles
% plotm(lat_cc_c,lon_cc_c,'o',c,[0.0 1.0 0.2], ms, 5.5,lw, 2)           % comcat - lime green 

% legend('comcat','Location','southwest','Orientation','horizontal')
title(sprintf('Seismicity Map'),'FontSize',24)

setm(ax,'FFaceColor',[0.6 0.8 1.0]) % color of water

%rectangle('Position', [-118.5 33.3 0.5 0.5],lw,4);
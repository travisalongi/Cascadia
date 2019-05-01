% 2018-10-24
% written by T. Alongi

% Purpose is to read output location file from simulPS. The
% output file has repeated locations (COSMOS database combined with
% NC_Events database) Want to take out duplicates and rewrite datatable
clear; clc

fname='simPS_merge3_rm_repeats.txt'; %file name of cleaned file
system('cd ../Data_tables');
data = load('/auto/home/talongi/Cascadia/Data_tables/Events/simPS_summary2_merge3_noheader.txt'); %next time use readtable

yr = data(:,1);
mo = data(:,2);
dy = data(:,3);
hr = data(:,4);
mn = data(:,5);
sec = data(:,6);

lat = data(:,7);
lon = data(:,8);
depth = data(:,9);
mag = data(:,18);

date_matrix = [yr, mo, dy, hr, mn, sec];

events_date_num = datenum(date_matrix);  % datevec will 'undo' datenum
events_datetime = datetime(date_matrix);

%% Clean database of duplicates
%set tolerances for duplicates
time_tolerance = seconds(15);
mag_tolerance = 0.2;

N = length(yr);

% set vectors to be filled within the loop
index_orig = [];
index_repeat= [];
cleaned_data = []; % new matrix without repeats

for i=1:N
    db_time = events_datetime(i);
    time_up_bound = db_time + time_tolerance;
    time_lower_bound = db_time - time_tolerance; 
    
%     db_mag = mag(i);
%     mag_up_bound = mag + mag_tolerance;
%     mag_lower_bound = mag - mag_tolerance;
        for j=i+1:N
            count = 0;
            compare_time = events_datetime(j);
            compare_mag = mag(j);
            
            if compare_time < time_up_bound & compare_time > time_lower_bound %...
                    %& compare_mag < mag_up_bound & compare_mag > mag_lower_bound;
                index_orig = [index_orig, i];
                index_repeat = [index_repeat, j];
                count = count + 1;
                break
            end
        end
            
    if count == 0
            cleaned_data = [cleaned_data; data(i, :)];
    end
end
    
%% check that these things are correct.
N_duplicate = length(index_orig);
repeats_dates = [events_datetime(index_orig), events_datetime(index_repeat)];
repeats_location = [lat(index_orig), lat(index_repeat),...
    lon(index_orig), lon(index_repeat),...
    depth(index_orig), depth(index_repeat)]; 

%% write trimmed down datatable to textfile


fid=fopen(fname,'w');

header = "YEAR MO DY HR MN Sec Lat Long Depth Nwr Rms Az1 D1 Ser1 Az2 D2 Ser2 Mag Ser3 mdl.X mdl.Y mdl.Z Err.ot Err.x Err.y Err.z \n"; %in simulPS format
fprintf(fid, header);

% snippet of code found online, prints matrix to a file
for ii = 1:size(cleaned_data,1)
    fprintf(fid,'%g\t',cleaned_data(ii,:));
    fprintf(fid,'\n');
end

fclose(fid);

% system('gedit relocated_merged_rm_repeats.txt &')
% system('mv relocated_merged_rm_repeats.txt ../data_table');


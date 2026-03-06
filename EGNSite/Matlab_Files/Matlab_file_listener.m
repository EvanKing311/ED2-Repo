%% matlab_file_listener.m
% Periodically read the command file written by Django and display as table

commandFile = 'C:\Users\kinge\EGNSite\MatlabApp\commands.csv';  %full path to the file

% Keep MATLAB running and refresh the table every second
while true
    if isfile(commandFile)
        % Read commands from file
        cmds = readtable(commandFile);  % uses the header row in the CSV
        disp(cmds);
        % update table variable
    end
    % Open Variable Editor if not already open (first iteration)
    try
        openvar('commandsTable')
    catch
        % Already open
    end
    pause(10)  % refresh every second
end

% MQTT listener - Receives commands FROM Django

brokerHost = "localhost";
brokerPort = 1883;
topic      = "django/to_matlab";  % Changed topic - listens for Django commands
brokerURI = sprintf("tcp://%s:%d", brokerHost, brokerPort);

% Clear old MQTT connections
clear mqttClient sub

% Connect to the broker
mqttClient = mqttclient(brokerURI);

% Subscribe to the topic
sub = subscribe(mqttClient, topic);

% Initialize a table to store commands
commands = table([], [], [], 'VariableNames', {'Timestamp', 'Topic', 'Message'});

disp("Listening for commands from Django on '" + topic + "' ...");

while true
    % Check for messages
    if sub.MessageCount > 0
        msg = read(sub);
        
        % Add message to the table
        newEntry = {datetime('now'), string(msg.Topic), string(msg.Data)};
        commands = [commands; newEntry]; 

        % Display in Command Window
        fprintf("Received command: %s (%s)\n", string(msg.Data), string(datetime('now')));

        % Update variable in base workspace so you can see it live
        assignin('base', 'commands', commands);
    end

    pause(1); 
end
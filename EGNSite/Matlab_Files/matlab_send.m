%Message & topic
topic = "django/commands";
message = 'Test from Matlab';

%Full path to script
python_script = '"C:\Users\kinge\EGNSite\MatlabApp\management\commands\publish_command.py"';

%System command
cmd = sprintf('python "%s" %s "%s"', python_script, topic, message);

%Execute command
system(cmd);
disp('Message published to Django');

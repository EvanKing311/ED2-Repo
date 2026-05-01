% InitFcn callback for TestCartPend1
% Version: 1.0
% Paste this into: Model Properties → Callbacks → InitFcn
%
% Declares kp, ki, kd as ExportedGlobal Simulink.Parameter objects.
% This makes them named global C variables in generated code so that
% read_params_sfcn can write to them directly at runtime before t=0.
%
% Default values here are compile-time fallbacks only.
% Actual values come from params.json via read_params_sfcn at runtime.

kp = Simulink.Parameter(1.0);
kp.StorageClass = 'ExportedGlobal';

ki = Simulink.Parameter(0.0);
ki.StorageClass = 'ExportedGlobal';

kd = Simulink.Parameter(0.0);
kd.StorageClass = 'ExportedGlobal';

% Add new params here as the model grows:
% newparam = Simulink.Parameter(0.0);
% newparam.StorageClass = 'ExportedGlobal';

read_params S-Function — Setup Guide
=====================================
Version: 2.0

OVERVIEW
--------
Drop-in subsystem that reads params.json at t=0 and writes values
directly into ExportedGlobal PID variables (kp, ki, kd etc).
No ports, no wiring changes, PID block fields stay as-is.


FILES
-----
picontrol_src/                     SHARED — never edit these
    read_params_sfcn.c
    cJSON.c                        download from github.com/DaveGamble/cJSON
    cJSON.h                        download from github.com/DaveGamble/cJSON
    compile_mex.m

Per model folder (e.g. TestCartPend1/):
    params_config.h                ONLY file you edit per model


FIRST-TIME SETUP (once per machine)
-------------------------------------
1. Download cJSON.c and cJSON.h from github.com/DaveGamble/cJSON
   Place in picontrol_src/

2. Install MinGW-w64 via MATLAB Add-Ons if not present

3. Compile MEX (edit MODEL_CONFIG_DIR in compile_mex.m first):
       cd picontrol_src
       compile_mex       (run in MATLAB)


PER-MODEL SETUP
---------------
1. InitFcn (Model Properties → Callbacks → InitFcn):
       kp = Simulink.Parameter(1.0);
       kp.StorageClass = 'ExportedGlobal';
       ki = Simulink.Parameter(0.0);
       ki.StorageClass = 'ExportedGlobal';
       kd = Simulink.Parameter(0.0);
       kd.StorageClass = 'ExportedGlobal';

2. Copy params_config.h into your model folder
   Edit PARAM_NAMES and PARAM_PTRS to match your variables

3. Add S-Function block to model (anywhere — no wiring needed):
       Library: User-Defined Functions → S-Function
       S-function name:    read_params_sfcn
       S-function modules: cJSON.c

   Wrap in an Initialize Function block for clean architecture:
       Modeling tab → Library → User-Defined Functions → Initialize Function
       Drop S-Function block inside it

4. Model Settings → Code Generation → Custom Code:
       Additional source files:  cJSON.c
       Additional include paths: C:\path\to\picontrol_src
                                 C:\path\to\YourModelFolder

5. Build and deploy as normal


ADDING A PARAM TO AN EXISTING MODEL
-------------------------------------
1. Add to InitFcn:
       newparam = Simulink.Parameter(0.0);
       newparam.StorageClass = 'ExportedGlobal';

2. Add to params_config.h:
       PARAM_NAMES: add "newparam"
       PARAM_PTRS:  add &newparam

3. Recompile MEX and rebuild model — nothing else changes


PARAMS.JSON FORMAT
------------------
Keys must match PARAM_NAMES exactly (case sensitive):
{
  "kp": 1.5,
  "ki": 0.0,
  "kd": 0.2
}
Written by dac_daemon.py before .elf launches.


WHAT CHANGES PER MODEL
-----------------------
  params_config.h    — param names and pointers (5-10 lines)
  InitFcn            — Simulink.Parameter declarations
  Everything else    — identical across all models

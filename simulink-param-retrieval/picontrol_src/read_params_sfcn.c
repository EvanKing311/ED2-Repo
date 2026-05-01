/*
 * read_params_sfcn.c
 * Version: 2.0
 * Description: Level-2 C S-Function that reads params.json once at
 *              simulation start and writes values directly into
 *              ExportedGlobal parameter variables (e.g. kp, ki, kd).
 *              No input or output ports — truly drop-in subsystem.
 *              Shared across ALL models — never edit this file.
 *              Model-specific config lives in params_config.h only.
 *
 * Ports:   none — no wiring required in Simulink diagram
 *
 * Requires:
 *   params_config.h  — per-model: defines PARAM_NAMES, PARAM_PTRS, N_PARAMS
 *   cJSON.c / cJSON.h — JSON parser (github.com/DaveGamble/cJSON)
 *
 * How it works:
 *   mdlStart() fires once before t=0.
 *   Reads PARAMS_PATH, parses JSON, writes each value directly into
 *   the ExportedGlobal C variable via pointer defined in params_config.h.
 *   PID block reads kp/ki/kd as normal — values are already set.
 */

#define S_FUNCTION_NAME  read_params_sfcn
#define S_FUNCTION_LEVEL 2

#include "simstruc.h"
#include "params_config.h"  /* model-specific param names and pointers */
#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* =========================================================================
 * mdlInitializeSizes — no ports, no parameters
 * ======================================================================= */
static void mdlInitializeSizes(SimStruct *S)
{
    ssSetNumSFcnParams(S, 0);
    if (ssGetNumSFcnParams(S) != ssGetSFcnParamsCount(S)) return;

    if (!ssSetNumInputPorts(S, 0))  return;
    if (!ssSetNumOutputPorts(S, 0)) return;

    ssSetNumSampleTimes(S, 1);
    ssSetNumDWork(S, 0);

    ssSetOptions(S, SS_OPTION_EXCEPTION_FREE_CODE);
}

/* =========================================================================
 * mdlInitializeSampleTimes
 * ======================================================================= */
static void mdlInitializeSampleTimes(SimStruct *S)
{
    ssSetSampleTime(S, 0, INHERITED_SAMPLE_TIME);
    ssSetOffsetTime(S, 0, 0.0);
}

/* =========================================================================
 * mdlStart — runs ONCE before t=0
 * Reads params.json, writes values into ExportedGlobal variables.
 * ======================================================================= */
#define MDL_START
static void mdlStart(SimStruct *S)
{
    size_t  i;
    FILE   *f;
    long    len;
    char   *buf;
    cJSON  *json;
    cJSON  *item;

    /* Open params.json */
    f = fopen(PARAMS_PATH, "rb");
    if (!f) {
        ssPrintf("[read_params] WARNING: could not open %s\n"
                 "              Compiled defaults will be used.\n",
                 PARAMS_PATH);
        return;
    }

    /* Read entire file into buffer */
    fseek(f, 0, SEEK_END);
    len = ftell(f);
    rewind(f);

    buf = (char *)malloc((size_t)len + 1);
    if (!buf) {
        ssPrintf("[read_params] malloc failed\n");
        fclose(f);
        return;
    }

    fread(buf, 1, (size_t)len, f);
    buf[len] = '\0';
    fclose(f);

    /* Parse JSON */
    json = cJSON_Parse(buf);
    free(buf);

    if (!json) {
        ssPrintf("[read_params] JSON parse error: %s\n"
                 "              Compiled defaults will be used.\n",
                 cJSON_GetErrorPtr());
        return;
    }

    /* Write each param value directly into its ExportedGlobal variable */
    for (i = 0; i < N_PARAMS; i++) {
        item = cJSON_GetObjectItemCaseSensitive(json, PARAM_NAMES[i]);
        if (cJSON_IsNumber(item)) {
            *PARAM_PTRS[i] = item->valuedouble;
            ssPrintf("[read_params] %-24s = %f\n",
                     PARAM_NAMES[i], *PARAM_PTRS[i]);
        } else {
            ssPrintf("[read_params] %-24s not found — keeping compiled default\n",
                     PARAM_NAMES[i]);
        }
    }

    cJSON_Delete(json);
    ssPrintf("[read_params] done — params loaded from %s\n", PARAMS_PATH);
}

/* =========================================================================
 * mdlOutputs — nothing to output
 * ======================================================================= */
static void mdlOutputs(SimStruct *S, int_T tid)
{
    /* no output ports */
}

/* =========================================================================
 * mdlTerminate
 * ======================================================================= */
static void mdlTerminate(SimStruct *S)
{
    /* nothing to clean up */
}

/* =========================================================================
 * Simulink/Coder trailer — required boilerplate
 * ======================================================================= */
#ifdef MATLAB_MEX_FILE
#include "simulink.c"
#else
#include "cg_sfun.h"
#endif

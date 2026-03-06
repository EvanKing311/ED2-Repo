
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from .models import Command, Message
from .mqtt_utils import send_command
import json
import requests
from .models import ExperimentSession

# Experiment configuration - default parameters for each experiment
EXPERIMENT_DEFAULTS = {
    'SwingHoldPendulum': {
        'parameters': {
            'pendulum_mass': {'value': 0.2, 'editable': False, 'unit': 'kg'},
            'cart_mass': {'value': 2.3, 'editable': False, 'unit': 'kg'},
            'pendulum_length': {'value': 0.3, 'editable': False, 'unit': 'm'},
            'gravity': {'value': 9.81, 'editable': False, 'unit': 'm/s²'},
            'moment_inertia': {'value': 0.0099, 'editable': True, 'unit': 'kg⋅m²'},
            'initial_angle': {'value': 'pi', 'editable': True, 'unit': 'radians'},
            'cart_friction': {'value': 0.00005, 'editable': True, 'unit': ''},
            'pendulum_damping': {'value': 0.005, 'editable': True, 'unit': ''},
        }
    },
    #Other experiments for later
    'CartControl': {},
    'CartIdent': {},
    'CraneIdent': {},
    'CraneStab': {},
    'InvPendIdent': {},
    'PendstabPD': {},
    'PendSwingUp': {},
    'PendulumFriction': {},
    'SwingHoldPendulumExtra': {},
    'UpDownPendulum': {},
    'PendulumTest': {},
}


@login_required
def dashboard(request):
    """
    Main dashboard - shows experiment selection grid
    """
    
    return render(request, 'MatlabApp/dashboard.html')


@login_required
def experiment_run_dynamic(request, experiment_name):
    """
    Display the experiment run page with parameters and controls
    """
    # Check if experiment exists
    if experiment_name not in EXPERIMENT_DEFAULTS:
        django_messages.error(request, f'Experiment "{experiment_name}" not found')
        return redirect('dashboard')
    
    # Get parameters for this specific experiment
    experiment_config = EXPERIMENT_DEFAULTS[experiment_name]

    # Handle both old format (just values) and new format (with metadata)
    if 'parameters' in experiment_config:
        parameters = experiment_config['parameters']
    else:
        # Old format - treat all as editable for backwards compatibility
        parameters = {k: {'value': v, 'editable': True, 'unit': ''} 
                     for k, v in experiment_config.items()}
    
    # Get recent activity
    recent_commands = Command.objects.all()[:10]
    raspi_messages = Message.objects.all()[:10]
    
    context = {
        'experiment_name': experiment_name,
        'parameters': parameters,  # PASS PARAMETERS TO TEMPLATE
        'recent_commands': recent_commands,
        'raspi_messages': raspi_messages,
    }
    
    return render(request, 'MatlabApp/experiment_run_dynamic.html', context)


@login_required
@require_http_methods(["POST"])
def send_experiment_command(request, experiment_name):
    try:
        data = json.loads(request.body)
        command = data.get('command')

        if not command:
            return JsonResponse({'success': False, 'error': 'No command provided'})

        payload = {
            "command": command,
            "experiment": experiment_name
        }

        # If START → include latest saved parameters
        if command == "start":
            try:
                session = ExperimentSession.objects.get(
                    experiment_name=experiment_name,
                    user=request.user
                )
                payload["parameters"] = session.parameters
            except ExperimentSession.DoesNotExist:
                # If no saved params yet → use defaults
                default_params = {
                    k: v["value"]
                    for k, v in EXPERIMENT_DEFAULTS[experiment_name]["parameters"].items()
                }
                payload["parameters"] = default_params

        # Save command in DB
        cmd_obj = Command.objects.create(
            command=command,
            user=request.user
        )

        # Send full JSON payload to Pi
        success = send_command(payload, 'raspi')

        cmd_obj.success = success
        cmd_obj.save()

        return JsonResponse({
            'success': success,
            'payload': payload
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_http_methods(["POST"])
def update_experiment_params(request, experiment_name):
    try:
        data = json.loads(request.body)
        parameters = data.get('parameters', {})

        if experiment_name not in EXPERIMENT_DEFAULTS:
            return JsonResponse({
                'success': False,
                'error': f'Experiment "{experiment_name}" not found'
            })

        # Save or update parameters in DB
        session, created = ExperimentSession.objects.update_or_create(
            experiment_name=experiment_name,
            user=request.user,
            defaults={'parameters': parameters}
        )

        # Log update action
        Command.objects.create(
            command=f'Parameters updated for {experiment_name}',
            user=request.user,
        )

        return JsonResponse({
            'success': True,
            'message': 'Parameters saved successfully',
            'parameters': parameters
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def get_experiment_defaults(request, experiment_name):
    """
    API endpoint to get default parameters for an experiment
    """
    if experiment_name not in EXPERIMENT_DEFAULTS:
        return JsonResponse({
            'success': False,
            'error': f'Experiment "{experiment_name}" not found'
        })
    
    return JsonResponse({
        'success': True,
        'experiment': experiment_name,
        'defaults': EXPERIMENT_DEFAULTS[experiment_name]
    })


@login_required
def data_history(request):
    """Display all historical commands and messages from all devices"""
    
    commands = Command.objects.all().order_by('-timestamp')
    messages = Message.objects.all().order_by('-timestamp')
    
    return render(request, 'MatlabApp/data_history.html', {
        'commands': commands,
        'all_messages': messages,
    })
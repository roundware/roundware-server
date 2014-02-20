from chartit.chartdata import PivotDataPool
from chartit.charts import PivotChart
from django.db.models.aggregates import Count, Sum
from django.http import HttpResponse
import time
import string
import subprocess
import os
import logging
import json
import traceback
from roundware.rw.models import Asset
from roundware.rw.chart_functions import assets_created_per_day
from roundware.rw.models import Session
from roundware.rw.models import Tag
from roundware.rw.chart_functions import sessions_created_per_day
from roundware.rw.chart_functions import assets_by_question
from roundware.rw.chart_functions import assets_by_section
from roundwared import settings
from roundwared import db
from roundwared import convertaudio
from roundwared import discover_audiolength
from roundwared import roundexception
from roundwared import icecast2
from roundwared import gpsmixer
from roundwared import rounddbus
from roundwared import server


def main(request):
    return HttpResponse(json.dumps(catch_errors(request), sort_keys=True, indent=4, ensure_ascii=False), mimetype='application/json')


def catch_errors(request):
    try:
        config_file = "rw"
        if request.GET.has_key('config'):
            config_file = request.GET['config']
        settings.initialize_config(os.path.join('/etc/roundware/', config_file))

        logging.basicConfig(
            filename=settings.config["log_file"],
            filemode="a",
            level=logging.DEBUG,
            format='%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s',
            )

        if request.GET.has_key('operation'):
            function = operation_to_function(request.GET['operation'])
        elif request.POST.has_key('operation'):
            function = operation_to_function(request.POST['operation'])
        return function(request)
    except roundexception.RoundException as e:
        logging.error(str(e) + traceback.format_exc())
        return {"error_message": str(e)}
    except:
        logging.error(
            "An uncaught exception was raised. See traceback for details." + \
            traceback.format_exc())
        return {
            "error_message": "An uncaught exception was raised. See traceback for details.",
            "traceback": traceback.format_exc(),
        }


def operation_to_function(operation):
    if not operation:
        raise roundexception.RoundException("Operation is required")
    operations = {
        "request_stream": server.request_stream,
        "heartbeat": server.heartbeat,
        "current_version": server.current_version,
        "log_event": server.log_event,
        "create_envelope": server.create_envelope,
        "add_asset_to_envelope": server.add_asset_to_envelope,
        "get_config": server.get_config,
        "get_tags": server.get_tags_for_project,
        "modify_stream": server.modify_stream,
        "get_current_streaming_asset": server.get_current_streaming_asset,
        "get_asset_info": server.get_asset_info,
        "get_available_assets": server.get_available_assets,
        "play_asset_in_stream": server.play_asset_in_stream,
        "vote_asset": server.vote_asset,
        "skip_ahead": server.skip_ahead,
        "get_events": server.get_events,
    }
    key = string.lower(operation)
    if operations.has_key(key):
        return operations[key]
    else:
        raise roundexception.RoundException("Invalid operation, " + operation)

from chartit import DataPool, Chart
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required


@login_required
def chart_views(request):

    asset_created_per_day_chart = assets_created_per_day()
#    return render_to_response("chart_template.html", {'assetchart': asset_created_per_day_chart})

    session_created_per_day_chart = sessions_created_per_day()
    assets_by_question_chart = assets_by_question()
    assets_by_section_chart = assets_by_section()
#    return render_to_response("chart_template.html", {'sessionchart': session_created_per_day_chart, 'assetchart': asset_created_per_day_chart})
    return render_to_response("chart_template.html", {'charts': [session_created_per_day_chart, asset_created_per_day_chart, assets_by_question_chart, assets_by_section_chart]})


@login_required
def asset_map(request):
    return render_to_response("asset-map.html")
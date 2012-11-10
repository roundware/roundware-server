from chartit.chartdata import PivotDataPool
from chartit.chartdata import DataPool
from chartit.charts import Chart
from chartit.charts import PivotChart
from roundware.rw.models import Asset
from roundware.rw.models import Session
from roundware.rw.models import Tag
from django.db.models.aggregates import Count
from django.db.models import Q


def assets_created_per_day():
    all_assets = Asset.objects.extra({'created': "date(created)"}).values('created', 'id').filter(submitted__exact=1, project__id__exact=2, created__range=["2012-01-01", "2012-12-31"])

    ds = PivotDataPool(
        series=[
                {'options':{
                'source': all_assets,
                'categories': 'created'},
                    'terms': {
                        'total_assets': Count('id')}}])

    pivotchart = PivotChart(
        datasource=ds,
        series_options=[
            {'options': {
            'type': 'column'},
                'terms': ['total_assets']}],
        chart_options=
                {'title': {
                    'text': 'Number of Recordings Per Day'},
                'credits': {
                    'enabled': 'false',
                    'text': ""},
        'xAxis': {
                    'title': {
                    'text': 'Date'}},
        'yAxis': {
                    'title': {
                        'text': '# of Recordings'}}})
    return pivotchart


def sessions_created_per_day():
    all_sessions = Session.objects.extra({'starttime': "date(starttime)"}).values('starttime', 'id').filter(project__id__exact=2, starttime__range=["2012-01-01", "2012-12-31"])
    ds = PivotDataPool(
        series=[
                {'options':{
                'source': all_sessions,
                'categories': 'starttime'},
                'terms': {
                    'total_sessions': Count('id')}}])

    pivotchart = PivotChart(
        datasource=ds,
        series_options=[
                {'options': {
                'type': 'column'},
                'terms': ['total_sessions']}],
        chart_options=
                {'title': {
                    'text': 'Number of Sessions per Day'},
                'credits': {
                    'enabled': 'false',
                    'text': ""},
        'xAxis': {
            'title': {
                    'text': 'Date'},
            'labels': {
            'step': '7'}},
        'yAxis': {
            'title': {
            'text': '# of Sessions'}},
        'plotOptions': {
            'column': {
            'color': '#687424'}}})
    return pivotchart


def assets_by_question():
    question_tags = Tag.objects.values('id', 'description').filter(asset__submitted__exact=1).filter(id__in=[10, 11, 12, 18, 20])
    ds = PivotDataPool(
    series=[
        {'options':{
                'source': question_tags,
                'categories': 'description'},
        'terms': {
        'question_tags_count': Count('id')}}])

    pivotchart = PivotChart(
        datasource=ds,
        series_options=[
                {'options': {
                'type': 'bar'},
                'terms': ['question_tags_count']}],
        chart_options=
                {'title': {
                    'text': 'Recording Distribution by Question'},
                'xAxis': {
                    'title': {
                        'text': 'Question'}},
                'yAxis': {
                    'title': {
                        'text': '# of Recordings'}},
                'credits': {
                    'enabled': 'false',
                    'text': ""}})
    return pivotchart


def assets_by_section():
    section_tags = Tag.objects.values('id', 'description').filter(asset__submitted__exact=1).filter(id__in=[13, 14, 15, 16, 17, 19, 20])
    ds = PivotDataPool(
        series=[
            {'options':{
                'source': section_tags,
                'categories': 'description'},
            'terms': {
                'section_tags_count': Count('id')}}])

    pivotchart = PivotChart(
        datasource=ds,
        series_options=[
                {'options': {
                    'type': 'bar'},
                'terms': ['section_tags_count']}],
        chart_options=
                {'title': {
                   'text': 'Recording Distribution by Section'},
                'xAxis': {
                    'title': {
                        'text': 'Section'}},
                'yAxis': {
                    'title': {
                        'text': '# of Recordings'},
                'tickWidth': '1',
                'max': '50',
                'labels': {
                    'step': '1'}},
                'credits': {
                    'enabled': 'false',
                    'text': ""}})
    return pivotchart

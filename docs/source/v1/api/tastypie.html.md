---
page_title: "tastypie"
sidebar_current: "api-tastypie"
---

# TastyPie

We have implemented the TastyPie Django API app in order to have a fully RESTful and flexible alternative
API for database interactions.  We anticipate this being very useful for many future purposes,
but for now, only some basics are in place.

## Example Calls:

### Assets

This call returns information about assets and can be filtered by many parameters, including
`project_id`, `mediatype`, created date range and `audiolength`.

```
http://rw.roundware.org/roundware/api/v1/asset/?format=json&created__lte=2014-02-01&mediatype=audio&submitted=true&created__gte=2014-01-01&audiolength__gte=1&project=12
```
Return JSON

```
{
  "meta": {
    "limit": 20,
    "next": null,
    "offset": 0,
    "previous": null,
    "total_count": 2
  },
  "objects": [
    {
      "audiolength": "9868480726",
      "audiolength_in_seconds": 9.87,
      "created": "2014-01-20T13:25:32",
      "description": "",
      "file": "http://rw.roundware.org/rwmedia/20140120-132531.m4a",
      "filename": "20140120-132531.wav",
      "id": 4404,
      "language": 1,
      "latitude": 41.003571,
      "longitude": -71.27923584,
      "mediatype": "audio",
      "project": 12,
      "resource_uri": "/roundware/api/v1/asset/4404/",
      "session": 14161,
      "submitted": true,
      "volume": 1.0,
      "weight": 50
    },
    {
      "audiolength": "25843809524",
      "audiolength_in_seconds": 25.84,
      "created": "2014-01-20T15:08:21",
      "description": "",
      "file": "http://rw.roundware.org/rwmedia/20140120-150821.m4a",
      "filename": "20140120-150821.wav",
      "id": 4405,
      "language": 1,
      "latitude": 42.4984855651855,
      "longitude": -71.2808990478516,
      "mediatype": "audio",
      "project": 12,
      "resource_uri": "/roundware/api/v1/asset/4405/",
      "session": 14214,
      "submitted": true,
      "volume": 1.0,
      "weight": 50
    }
  ]
}
```

### Events

This call returns information about assets and can be filtered by many parameters, including
`session_id`, `event_type` and created date range.

```
http://rw.roundware.org/roundware/api/v1/event/?format=json&server_time__lte=2015-01-01&server_time__gte=2011-01-01&event_type=start_session&session=4892
```
Return JSON

```
{
  "meta": {
    "limit": 20,
    "next": null,
    "offset": 0,
    "previous": null,
    "total_count": 1
  },
  "objects": [
    {
      "client_time": null,
      "data": "",
      "event_type": "start_session",
      "id": 59513,
      "latitude": null,
      "longitude": null,
      "operationid": null,
      "resource_uri": "/roundware/api/v1/event/59513/",
      "server_time": "2013-01-14T14:46:02",
      "session": 4892,
      "tags": "",
      "udid": null
    }
  ]
}
```

We have also implemented APIs for the Project, Session and Listening History objects.
These behave similarly.
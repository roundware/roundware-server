---
page_title: "Settings"
sidebar_current: "setup-settings"
---


# Testing Your Setup

In order to verify that you have set things up properly, here are a few sample urls to test certain setup/config items.  Make sure to substitute the proper server url.

If you see the expected JSON responses, that is a very good sign.  If not, you'll hopefully see some useful debugging information to help track down the problem.

## Project verification

```
http://localhost:8888/api/1/?&operation=get_config&project_id=1
```

## Tag verification

```
http://localhost:8888/api/1/?&operation=get_tags&project_id=1
```

## Stream generation verification

```
http://localhost:8888/api/1/?&operation=request_stream&session_id=1234&latitude=1.0&longitude=2.0&tags=1,2,3
```
Make sure that you can actually listen to the stream_url returned and that it contains the speaker audio as well as any audio assets expected.
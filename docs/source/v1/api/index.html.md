---
page_title: "API"
sidebar_current: "api"
---

# API

Roundware clients communicate with the Roundware server using an HTTP web-service.
Most requests are GET other than media uploads which attach the binary file using a POST
request.

All API calls include an `operation` GET parameter to indicate which action is desired.

All server responses are in JSON format.

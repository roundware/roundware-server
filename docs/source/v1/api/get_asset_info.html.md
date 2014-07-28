---
page_title: "get_asset_info"
sidebar_current: "api-get-asset-info"
---

# get\_asset\_info

Returns useful info about a particular asset.  Originally developed to assist with asset voting
and has been in large part replaced by other API calls and the TastyPie REST API.

**Example Call:**

```
http://localhost:8888/api/1/?operation=get_asset_info&session_id=1&asset_id=234
```

## Parameters (some optional*):

* `asset_id`
* `session_id`

### asset_id

Indicate which asset is of interest.

### session_id

This may not be necessary, but is currently programatically required.


## Response

JSON containing asset_id, created datetime and audiolength.

### Example Response

```
{
    "asset_id": 234,
    "created": "2012-03-08T21:14:20",
    "duraton_in_ms": 2507
}
```

---
page_title: "add_asset_to_envelope"
sidebar_current: "api-add-asset-to-envelope"
---

# add\_asset\_to\_envelope

This API call uploads a media asset to the Roundware server, creates a new record in
the rw_asset table and creates a relationship between the asset and a pre-existing `envelope`
record.  In the case of audio assets, this call also triggers conversion of the audio file into
all required formats (mp3, wav) and calculates the length of the audio which it stores
in `rw_asset.audiolength`.

**Example Call:**

```
http://localhost:8888/api/1/?operation=add_asset_to_envelope&envelope_id=1&latitude=23.3456&longitude=-88.3456&tags=153,157&mediatype=photo
```

## Parameters (some optional*):

* `envelope_id`
* `file`
* `mediatype`*
* `latitude`*
* `longitude`*
* `tags`*
* `submitted`*

### envelope_id

id for envelope record in database created previously (most likely by `create_envelope`) in
preparation for asset to be uploaded.

### file

binary file data for media asset to be uploaded

Stored in MEDIA_ROOT directory on file system, as set in Django settings: `roundware/settings/common.py`

### mediatype

*OPTIONAL:* Options are: `audio` `photo` `text`. Default is `audio` if none provided.

### latitude

*OPTIONAL:* Latitude of asset

Stored in `rw_asset.latitude`

### longitude

*OPTIONAL:* Longitude of asset

Stored in ``rw_asset.longitude``

### tags

*OPTIONAL:* Comma-separated list of tag_ids to be assigned to the asset

Stored in `rw_asset_tags` many to many table

### submitted

*OPTIONAL:* Format is `submitted=Y` or `submitted=N`. This can be used to over-ride the server-side code that automatically determines whether or not an asset is marked as submitted.

The server determines the `rw_asset.submitted` value based on these cascading checks:

* if `submitted` parameter is passed in `add_asset_to_envelope` request, use that value
* if not, then check if asset is within range of project as determined by being within 2x the radius distance
from any active speaker assigned to the project.
 * if within range, set `rw_asset.submitted` to default value provided in `rw_project.auto_submit`
 * if outside of range set `rw_asset.submitted` to false


## Response

The server responds with a success boolean and the `asset_id` of the newly created asset.

### Example Response

```
{
    "success": True,
    "asset_id": 17
}
```
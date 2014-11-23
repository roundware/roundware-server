---
page_title: "move_listener"
sidebar_current: "api-move-listener"
---

# move_listener

Tells the server that the listener of a particular stream has changed their location.  This is only pertinent to geo-listen enabled projects.

Upon receiving the new location, the server performs two tasks:

* adjusts the volumes of all nearby ```speakers``` based on the newly calculated proximity of the listener to each speaker
* calculates what audio assets are in range and not already played in the stream.  NOTE: if an asset has already been played and a ```move_listener``` call is received that is still within range of the asset, it will not be added to ```nearby_available_recordings```.  In order to hear the asset again, a ```move_listener``` outside of the asset's range must be received prior to receiving a secondary in-range request.


**Example Call:**

```
http://localhost:8888/api/1/?operation=move_listener&session_id=1&latitude=1&longitude=1
```

## Parameters:

* `session_id`
* `latitude`
* `longitude`

### session_id

`session_id` is used to determine which stream to modify.

### latitude

in combination with longitude, causes stream audio to be updated for the new location

### longitude

in combination with latitude, causes stream audio to be updated for the new location

## Response

JSON response is success boolean

### Example Response

```
{"success": true}
```

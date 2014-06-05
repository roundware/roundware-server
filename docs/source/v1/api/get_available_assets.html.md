---
page_title: "get_available_assets"
sidebar_current: "api-get-available-assets"
---

# get\_available\_assets

Returns information about assets per a set of passed filters such that they can be accessed individually by clients.
This API call is very flexible and is useful for numerous pieces of functionality given the large number
of optional filtering parameters available.

**Example Call:**

```
http://rw.roundware.org/roundware/?operation=get_available_assets&project_id=3&tagids=26,36&tagbool=and&latitude=47.654139&longitude=-122.335914&radius=500
```

## Parameters (some optional*):

* `project_id`
* `mediatype`*
* `envelope_id`*
* `asset_id`*
* `language`*
* `latitude`*
* `longitude`*
* `radius`*
* `tagids`*
* `tagbool`*


### project_id

This call works on a per-project basis.  Including no other filtering parameters will simply return all
assets that exist for the indicated project.

### mediatype

*OPTIONAL:* Filter assets by mediatype.  Options are `audio`, `photo`, `text`.

### envelope_id

*OPTIONAL:* Return all assets in a particular envelope or list of envelopes as passed in comma-delimited list.

### asset_id

*OPTIONAL:* Return a single asset or set of assets as passed in comma-delimited list.

### language

*OPTIONAL:* Passed in 2-character ISO language format (i.e. 'en', 'es', 'fr' etc). The language parameter does not operate as a filter, but rather selects the language of the localized strings to be returned.  This isn't consistent with the other parameters,
so it may need to be changed to behave more like a filter depending on what future use cases emerge.

### latitude

*OPTIONAL:* in combination with longitude and radius, this will return assets that are contained in the
defined geographic region

### longitude

*OPTIONAL:* in combination with latitude and radius, this will return assets that are contained in the
defined geographic region

### radius

*OPTIONAL:* in combination with latitude and longitude, this will return assets that are contained in the
defined geographic region

### tagids

*OPTIONAL:* Returns assets related to a comma-delimited list of tag_ids.

### tagbool

*OPTIONAL:* If set to 'and', only assets that contain ALL tags indicated in the tagids parameter will be returned.
If set to 'or', assets that contain ANY of the tagids indicated in the tagids parameter will be returned.

## Response

JSON response includes nodes for each asset matching the filters as well as a summarization node
that sums the number of assets per mediatype.

### Example Response

```
{
    "assets": [
        {
            "asset_id": 3738,
            "asset_url": "http://rw.roundware.org/rwmedia/20130512-125336.jpg",
            "audio_length": null,
            "language": "en",
            "latitude": 1.0,
            "longitude": 1.0,
            "project": "Will to Adorn",
            "submitted": true,
            "tags": [
                {
                    "localized_value": "Exemplar",
                    "tag_category_name": "usertype",
                    "tag_id": 62
                },
                {
                    "localized_value": "What are you wearing today?",
                    "tag_category_name": "question",
                    "tag_id": 66
                },
                {
                    "localized_value": "West",
                    "tag_category_name": "region",
                    "tag_id": 70
                }
            ]
        },
        {
            "asset_id": 3739,
            "asset_url": "http://rw.roundware.org/rwmedia/20130512-125343.jpg",
            "audio_length": null,
            "language": "en",
            "latitude": 1.0,
            "longitude": 1.0,
            "project": "Will to Adorn",
            "submitted": true,
            "tags": [
                {
                    "localized_value": "Exemplar",
                    "tag_category_name": "usertype",
                    "tag_id": 62
                },
                {
                    "localized_value": "What are you wearing today?",
                    "tag_category_name": "question",
                    "tag_id": 66
                },
                {
                    "localized_value": "West",
                    "tag_category_name": "region",
                    "tag_id": 70
                }
            ]
        },
        {
            "asset_id": 3740,
            "asset_url": "http://rw.roundware.org/rwmedia/20130512-125349.txt",
            "audio_length": null,
            "language": "en",
            "latitude": 1.0,
            "longitude": 1.0,
            "project": "Will to Adorn",
            "submitted": true,
            "tags": [
                {
                    "localized_value": "Exemplar",
                    "tag_category_name": "usertype",
                    "tag_id": 62
                },
                {
                    "localized_value": "What are you wearing today?",
                    "tag_category_name": "question",
                    "tag_id": 66
                },
                {
                    "localized_value": "West",
                    "tag_category_name": "region",
                    "tag_id": 70
                }
            ]
        },
        {
            "asset_id": 3741,
            "asset_url": "http://rw.roundware.org/rwmedia/20130512-125357.wav",
            "audio_length": 12097596372,
            "language": "en",
            "latitude": 1.0,
            "longitude": 1.0,
            "project": "Will to Adorn",
            "submitted": true,
            "tags": [
                {
                    "localized_value": "Exemplar",
                    "tag_category_name": "usertype",
                    "tag_id": 62
                },
                {
                    "localized_value": "What are you wearing today?",
                    "tag_category_name": "question",
                    "tag_id": 66
                },
                {
                    "localized_value": "West",
                    "tag_category_name": "region",
                    "tag_id": 70
                }
            ]
        }
    ],
    "number_of_assets": {
        "audio": 1,
        "photo": 2,
        "text": 1,
        "video": 0
    }
}
```

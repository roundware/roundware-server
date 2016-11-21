---
page_title: "get_tags"
sidebar_current: "api-get-tags"
---

# get_tags

**Example Call:**

```
http://localhost:8888/api/1/?operation=get_tags&project_id=1&session_id=1234
```

This is typically the second command a Roundware client sends to the Roundware server.
It is used to configure the tag webviews for both Listen and Speak functionalities.

## Parameters (some optional*):

* `project_id`
* `session_id`*

## project_id

id from the database for the project that the client wishes to interact with and
for which it is built.

## session_id

*OPTIONAL:* `session_id` can be included if you are localizing your Roundware project.
The session table includes language_id `rw_session.language_id` which tells RW what
localized strings to return for the tags.

## Response

JSON response is broken into sections for `listen` and `speak` at the top level, allowing tags
and tag metadata to be different for each mode.  Beneath that, there are nodes for each tag category
and then the tags themselves.

`get_tags` response is governed by the `ui_group` and `ui_item` objects.

### Example Response

```
{
    "listen": [
        {
            "code": "gender",
            "defaults": [
                3,
                4
            ],
            "header_text": "",
            "name": "Select gender(s)",
            "options": [
                {
                    "data": "class=tag-one",
                    "description": "male",
                    "loc_description": "",
                    "order": 1,
                    "relationships": [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6
                    ],
                    "shortcode": "male",
                    "tag_id": 3,
                    "value": "male"
                },
                {
                    "data": "class=tag-one",
                    "description": "female",
                    "loc_description": "",
                    "order": 1,
                    "relationships": [
                        1,
                        2,
                        3,
                        4,
                        6,
                        7
                    ],
                    "shortcode": "female",
                    "tag_id": 4,
                    "value": "female"
                }
            ],
            "order": 1,
            "select": "multi"
        },
        {
            "code": "age",
            "defaults": [
                1,
                2
            ],
            "header_text": "",
            "name": "Select age(s)",
            "options": [
                {
                    "data": "class=tag-one",
                    "description": "young",
                    "loc_description": "",
                    "order": 1,
                    "relationships": [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7
                    ],
                    "shortcode": "young",
                    "tag_id": 1,
                    "value": "young"
                },
                {
                    "data": "class=tag-one",
                    "description": "old",
                    "loc_description": "",
                    "order": 2,
                    "relationships": [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7
                    ],
                    "shortcode": "old",
                    "tag_id": 2,
                    "value": "old"
                }
            ],
            "order": 2,
            "select": "multi"
        },
        {
            "code": "question",
            "defaults": [
                5,
                6,
                7
            ],
            "header_text": "",
            "name": "What topics do you want to listen to?",
            "options": [
                {
                    "data": "class=tag-two",
                    "description": "What do you remember?",
                    "loc_description": "",
                    "order": 1,
                    "relationships": [
                        1,
                        2,
                        3,
                        5,
                        6,
                        7
                    ],
                    "shortcode": "remember",
                    "tag_id": 5,
                    "value": "What is your favorite memory?"
                },
                {
                    "data": "class=tag-two",
                    "description": "What did you eat today?",
                    "loc_description": "",
                    "order": 2,
                    "relationships": [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7
                    ],
                    "shortcode": "eat",
                    "tag_id": 6,
                    "value": "What did you eat today?"
                },
                {
                    "data": "class=tag-two",
                    "description": "What is favorite place to visit?",
                    "loc_description": "",
                    "order": 3,
                    "relationships": [
                        1,
                        2,
                        4,
                        5,
                        6,
                        7
                    ],
                    "shortcode": "place",
                    "tag_id": 7,
                    "value": "What is your favorite place to visit?"
                }
            ],
            "order": 3,
            "select": "multi"
        }
    ],
    "speak": [
        {
            "code": "gender",
            "defaults": [],
            "header_text": "",
            "name": "What gender are you?",
            "options": [
                {
                    "data": "class=tag-one",
                    "description": "male",
                    "loc_description": "",
                    "order": 1,
                    "relationships": [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6
                    ],
                    "shortcode": "male",
                    "tag_id": 3,
                    "value": "male"
                },
                {
                    "data": "class=tag-one",
                    "description": "female",
                    "loc_description": "",
                    "order": 2,
                    "relationships": [
                        1,
                        2,
                        3,
                        4,
                        6,
                        7
                    ],
                    "shortcode": "female",
                    "tag_id": 4,
                    "value": "female"
                }
            ],
            "order": 1,
            "select": "single"
        },
        {
            "code": "age",
            "defaults": [],
            "header_text": "",
            "name": "Choose your age",
            "options": [
                {
                    "data": "class=tag-one",
                    "description": "young",
                    "loc_description": "",
                    "order": 1,
                    "relationships": [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7
                    ],
                    "shortcode": "young",
                    "tag_id": 1,
                    "value": "young"
                },
                {
                    "data": "class=tag-one",
                    "description": "old",
                    "loc_description": "",
                    "order": 2,
                    "relationships": [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7
                    ],
                    "shortcode": "old",
                    "tag_id": 2,
                    "value": "old"
                }
            ],
            "order": 2,
            "select": "single"
        },
        {
            "code": "question",
            "defaults": [],
            "header_text": "",
            "name": "Choose a question",
            "options": [
                {
                    "data": "class=tag-two",
                    "description": "What do you remember?",
                    "loc_description": "",
                    "order": 1,
                    "relationships": [
                        1,
                        2,
                        3,
                        5,
                        6,
                        7
                    ],
                    "shortcode": "remember",
                    "tag_id": 5,
                    "value": "What is your favorite memory?"
                },
                {
                    "data": "class=tag-two",
                    "description": "What did you eat today?",
                    "loc_description": "",
                    "order": 2,
                    "relationships": [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7
                    ],
                    "shortcode": "eat",
                    "tag_id": 6,
                    "value": "What did you eat today?"
                },
                {
                    "data": "class=tag-two",
                    "description": "What is favorite place to visit?",
                    "loc_description": "",
                    "order": 3,
                    "relationships": [
                        1,
                        2,
                        4,
                        5,
                        6,
                        7
                    ],
                    "shortcode": "place",
                    "tag_id": 7,
                    "value": "What is your favorite place to visit?"
                }
            ],
            "order": 3,
            "select": "single"
        }
    ]
}
```

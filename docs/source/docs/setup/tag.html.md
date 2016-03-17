---
page_title: "Tags"
sidebar_current: "setup-tag"
---


# Tags

<div class="alert alert-block alert-info">
	<p>
		<strong>DEFINITION:</strong> Metadata used to describe assets.  Tags are arranged by tag category.  For example, the tags within the 'gender' tag category could be 'male' and 'female'.  Tags are very flexible and allow for collecting many different types of metadata to be used for filtering the assets at a later time.
	</p>
</div>

Tags are by far the most in-depth part of the Roundware configuration.  There are several steps to setting up a full complement of Tags to satisfy the needs of your Roundware implementation.  Tag Categories must be setup, Tags must then be created and assigned to the proper Tag Categories and finally, various UI mapping steps need to be taken to determine how the Tags are handled by RW clients.  Tags are also assigned to Modes primarily for functional organization on the client.  Currently there are only two possible modes: Listen and Speak.

<br>

## 1. Add Tag Categories

* if category exists, there is no need to add a new one as categories can be used cross project
* the only item required for creating a Tag Category is the name; choose something short and descriptive

## 2. add Master UIs for UI Tag Category Management

* associate Tag Categories with Modes and Projects
* assign selection methods for each Category on a per-Mode basis
* activate/deactivate Categories on a per-Mode basis
* set the UI ordering of Categories on per-Mode basis

Create one Master UI entry for each Tag Category per Mode to make available in client UI.  This adds Tag Categories to the get_tags request response so that clients can display them in their GUI.  For example, if you have three Tag Categories in your project (Question, Age, Gender) and are utilizing both Listen and Speak Modes, you will want to set up a total of 6 Master UIs:

* Listen:Question
* Listen:Age
* Listen:Gender
* Speak:Question
* Speak:Age
* Speak:Gender

### Fields

<table class="table table-striped table-bordered mr-types">
    <thead>
        <tr>
            <th>Parameter</th>
            <th>Format/Units</th>
            <th>Definition</th>
            <th>Notes</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Name</td>
            <td>string</td>
            <td>arbitrary name for Master UI</td>
            <td>usually helpful to be descriptive, including Project and Category info</td>
        </tr>
        <tr>
            <td>UI Mode</td>
            <td>string</td>
            <td>assign UI Mode</td>
            <td>Listen and Speak are currently the only available Modes</td>
        </tr>
        <tr>
            <td>Tag Category</td>
            <td>picklist</td>
            <td>assign Tag Category</td>
            <td></td>
        </tr>
        <tr>
            <td>Select</td>
            <td>picklist</td>
            <td>choose which type of selector to be used on client:
            	<strong>single</strong> (only one can be selected at a time)
            	<strong>multi</strong> (any number can be selected at once, including none)
            	<strong>multi_at_least_one</strong> (any number, but at least one must be selected at all times)</td>
            <td>typically Listen selections are multiple and Speak are single</td>
        </tr>
        <tr>
            <td>Active</td>
            <td>boolean</td>
            <td>turns availability of Master UI in client on and off</td>
            <td>useful for removing Tag Categories from Modes to change what displays on the client without deleting anything</td>
        </tr>
        <tr>
            <td>Index</td>
            <td>integer</td>
            <td>assign the order of the Master UIs for display on client</td>
            <td></td>
        </tr>
        <tr>
            <td>Project</td>
            <td>picklist</td>
            <td>associate with project</td>
            <td>tags and tag categories can be used on multiple projects as needed</td>
        </tr>
        <tr>
            <td>Header Text Loc</td>
            <td>string</td>
            <td>localized text to be displayed on clients as the header for the selections	ie. “What voices do you want to hear?” or “What question do you want to respond to?”</td>
            <td></td>
        </tr>
    </tbody>
</table>

## 3. add localized Tag names to localized strings table

* add one entry for each language you are offering for each tag name
* these strings are assigned to the actual Tags in the next step

## 4. create Tags and assign to Tag Categories

* this is done in the Tags table

### Fields

<table class="table table-striped table-bordered mr-types">
    <thead>
        <tr>
            <th>Parameter</th>
            <th>Format/Units</th>
            <th>Definition</th>
            <th>Notes</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Tag Category</td>
            <td>picklist</td>
            <td>assigned tag category</td>
            <td></td>
        </tr>
        <tr>
            <td>Value</td>
            <td>string</td>
            <td>not sure what we are going to use this for, but we probably had a good idea at some point for it</td>
            <td></td>
        </tr>
        <tr>
            <td>Localized Description</td>
            <td>picklist</td>
            <td>name of tag itself</td>
            <td>choose one value for each localization implemented</td>
        </tr>
    </tbody>
</table>

## 5. organize Tags into Tag Categories and Modes via UI Mappings

* assign individual tags to Modes via Master UI
* assign Tag defaults for Categories
* set UI ordering of Tags within Category
* activate/deactivate Tags on per-Mode basis

Create one UI Mapping entry for each Tag per Mode.  This adds Tags to the get_tags request response so that clients can display them in their GUI.

### Fields

<table class="table table-striped table-bordered mr-types">
    <thead>
        <tr>
            <th>Parameter</th>
            <th>Format/Units</th>
            <th>Definition</th>
            <th>Notes</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Master UI</td>
            <td>picklist</td>
            <td>this lets you assign each Tag to the proper Master UI combination of Tag Category and Mode</td>
            <td></td>
        </tr>
        <tr>
            <td>Index</td>
            <td>integer</td>
            <td>assign the order of the Tags within each Tag Category for display on client</td>
            <td></td>
        </tr>
        <tr>
            <td>Tag</td>
            <td>picklist</td>
            <td>assign Tag</td>
            <td></td>
        </tr>
        <tr>
            <td>Default</td>
            <td>boolean</td>
            <td>assign default values for each Tag Category on per-Mode basis</td>
            <td>request_stream will generate streams using the default values, so typically all Tags are assigned as Listen Mode defaults.  Speak Mode would normally have no Tags assigned as defaults.</td>
        </tr>
        <tr>
            <td>Active</td>
            <td>boolean</td>
            <td>turns availability of Tag in client on and off	useful for deactivating a Tag if it is no longer needed for future use, but is wanted to be retained for assets already tagged.</td>
            <td></td>
        </tr>
        <tr>
            <td>Tag Category</td>
            <td>picklist</td>
            <td>assigned tag category</td>
            <td></td>
        </tr>
    </tbody>
</table>

### Phew, you're done!

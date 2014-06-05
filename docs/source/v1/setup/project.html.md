---
page_title: "Project"
sidebar_current: "setup-project"
---


# Project

<div class="alert alert-block alert-info">
    <p>
        <strong>DEFINITION:</strong> The highest level of segmentation/grouping for all RW data.  One RW instance can run many projects simultaneously, governed by CPU, bandwidth and memory resources.
    </p>
</div>


## Fields

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
			<td>name</td>
			<td>string</td>
			<td>full name of project</td>
			<td></td>
		</tr>
		<tr>
			<td>latitude/longitude</td>
			<td>float</td>
			<td>defines the central physical location of the project</td>
			<td>used for things like centering a map display of all voices in a project</td>
		</tr>
		<tr>
			<td>Date published</td>
			<td>datetime</td>
			<td>indicates when project was created in the database</td>
			<td></td>
		</tr>
		<tr>
			<td>Audio format</td>
			<td>string (mp3, ogg)</td>
			<td>default audio format of streams generated for project</td>
			<td>stream format can be changed on a case-by-case basis by the client including the ‘audio_format’ parameter for request_stream</td>
		</tr>
		<tr>
			<td>Auto submit</td>
			<td>boolean</td>
			<td>default behavior for incoming assets</td>
			<td>If Y, assets are assigned submitted=Y automatically, if N, submitted=N.  This is related to geography so that if an asset is out of range, it will not be submitted automatically regardless of this setting.  Also, the submitted parameter in add_asset_to_envelope will override this default</td>
		</tr>
		<tr>
			<td>Max recording length</td>
			<td>integer/seconds</td>
			<td>max time participant can record for in single recording</td>
			<td>typically fed to recording countdown display on client</td>
		</tr>
		<tr>
			<td>Listen questions dynamic</td>
			<td>boolean</td>
			<td>whether or not Listen questions will change based on location of speaker</td>
			<td></td>
		</tr>
		<tr>
			<td>Speak questions dynamic</td>
			<td>boolean</td>
			<td>whether or not Speak questions will change based on location of speaker</td>
			<td></td>
		</tr>
		<tr>
			<td>Out of range url</td>
			<td>string/url</td>
			<td>mountpoint for static stream to be played by client if client is out of range</td>
			<td>only applicable when geo_listen enabled</td>
		</tr>
		<tr>
			<td>Recording radius</td>
			<td>integer/meters</td>
			<td>radius of circular area around asset lat/lon within which recording is active ie can be heard</td>
			<td>eventually this will be over-ridden for individual assets by the ‘radius’ field in the asset table</td>
		</tr>
		<tr>
			<td>Listen enabled</td>
			<td>boolean</td>
			<td>does project allow for clients to listen to streamed audio from server?</td>
			<td></td>
		</tr>
		<tr>
			<td>Geo listen enabled</td>
			<td>boolean</td>
			<td>does audio stream from server change based on location of client?</td>
			<td></td>
		</tr>
		<tr>
			<td>Speak enabled</td>
			<td>boolean</td>
			<td>does project allow for clients to capture audio from participants and upload to server?</td>
			<td></td>
		</tr>
		<tr>
			<td>Geo speak enabled</td>
			<td>boolean</td>
			<td>does project require lat/lon values for each asset submitted?</td>
			<td></td>
		</tr>
		<tr>
			<td>Reset tag defaults on startup</td>
			<td>boolean</td>
			<td>determines whether or not the client will reset all tag selections for the default values (received in get_tags) each time the app is started.  If N, clients will store the most recent tag selections and re-present those upon startup</td>
			<td></td>
		</tr>
		<tr>
			<td>Repeat mode</td>
			<td>picklist</td>
			<td><strong>stop:</strong> after playing all available recordings (round robin) in audio stream, no more recordings will play
				<strong>continuous:</strong> after playing all available recordings, server will start over and randomly play all available recordings again (round robin)<br>
				We will add more repeat modes in the future to give more options.</td>
			<td></td>
		</tr>
		<tr>
			<td>Sharing message loc</td>
			<td>string</td>
			<td>localized versions of the message used by the social sharing mechanism on the clients.	Typically, this message will end with the url to the asset sharing page and the client will append the asset_id of the asset being shared</td>
			<td></td>
		</tr>
		<tr>
			<td>Out of range message loc</td>
			<td>string</td>
			<td>localized versions of the message sent to the client when a user tries to access the system from out of range.
				Typically will outline the differences in client behavior based on being out of range (ie. “you will hear a static stream of audio rather than a dynamic stream”)</td>
			<td></td>
		</tr>
		<tr>
			<td>Legal agreement loc</td>
			<td>string</td>
			<td>localized version of the legal agreement participants must click through in order to make and upload assets to the system</td>
			<td></td>
		</tr>
    </tbody>
</table>



<!-- | Left-Aligned  | Center Aligned  | Right Aligned |
| :------------ |:---------------:| -----:|
| col 3 is      | some wordy text | $1600 |
| col 2 is      | centered        |   $12 |
| zebra stripes | are neat        |    $1 | 

{:.table-striped}
First Header  | Second header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell

-->
---
page_title: "Settings"
sidebar_current: "setup-settings"
---


# Settings

Django is configured using a settings file which we store in `~/roundware-server/roundware/settings/common.py`.  We have consolidated Roundware-specific settings into this file as well to keep them all together.  It is highly recommended that you create a local settings file `~/roundware-server/roundware/settings/local.py` in which to store settings specific to your environment, passwords, etc.

Here is a list of the most critical settings parameters that are specific to Roundware:

## Roundware-specific Settings

<table class="table table-striped table-bordered mr-types">
    <thead>
        <tr>
            <th>Parameter</th>
            <th>Default Value</th>
            <th>Notes</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>ICECAST_PORT</td>
            <td>8000</td>
            <td>set to port which Icecast uses to broadcast streams; must correspond to the <code>listen-socket</code> port in <code>/etc/icecast2/icecast.xml</code></td>
        </tr>
        <tr>
            <td>ICECAST_HOST</td>
            <td>localhost</td>
            <td>set to host address where Icecast streams will be accessible to the RW clients</td>
        </tr>
        <tr>
            <td>ICECAST_USERNAME</td>
            <td>admin</td>
            <td>must correspond to username setup in <code>/etc/icecast2/icecast.xml</code></td>
        </tr>
        <tr>
            <td>ICECAST_PASSWORD</td>
            <td>roundice</td>
            <td>must correspond to password setup in <code>/etc/icecast2/icecast.xml</code></td>
        </tr>
        <tr>
            <td>MASTER_VOLUME</td>
            <td>3.0</td>
            <td>overall stream volume attenuation</td>
        </tr>
        <tr>
            <td>HEARTBEAT_TIMEOUT</td>
            <td>200</td>
            <td>number of seconds after which a stream will be destroyed and cleaned up if it hasn't received a heartbeat or other message</td>
        </tr>
        <tr>
            <td>EXTERNAL_HOST_NAME_ WITHOUT_PORT</td>
            <td>localhost</td>
            <td>host for client access to Icecast streams</td>
        </tr>
        <tr>
            <td>DEMO_STREAM_CPU_LIMIT</td>
            <td>50.0</td>
            <td>When cpu usage on machine rises above this value, new clients receive the demo stream instead of a new unique stream.  This helps prevent performance degradation in times of significant usage.</td>
        </tr>
        <tr>
            <td>ALLOWED_AUDIO_MIME_TYPES</td>
            <td>'audio/x-wav', 'audio/wav', 'audio/mpeg', 'audio/mp4a-latm', 'audio/x-caf', 'audio/mp3'</td>
            <td>audio file types allowed for upload</td>
        </tr>
        <tr>
            <td>ALLOWED_IMAGE_MIME_TYPES</td>
            <td>'image/jpeg', 'image/gif', 'image/png', 'image/pjpeg'</td>
            <td>image file types allowed for upload</td>
        </tr>
        <tr>
            <td>ALLOWED_TEXT_MIME_TYPES</td>
            <td>'text/plain', 'text/html', 'application/xml'</td>
            <td>text file types allowed for upload</td>
        </tr>
        <tr>
            <td>DEFAULT_SESSION_ID</td>
            <td>-10</td>
            <td>session_id assigned to any assets uploaded via the admin interface.  Session with this id must exist in the session table.</td>
        </tr>
        <tr>
            <td>ANONYMOUS_USER_ID</td>
            <td>1</td>
            <td>id of anonymous user for use by Django Guardian</td>
        </tr>
        <tr>
            <td>EMAIL_HOST</td>
            <td>smtp.example.com</td>
            <td>SMTP server of email used for notifications</td>
        </tr>
        <tr>
            <td>EMAIL_HOST_USER</td>
            <td>email@example.com</td>
            <td>username of email used for notifications</td>
        </tr>
        <tr>
            <td>EMAIL_HOST_PASSWORD</td>
            <td>password</td>
            <td>passwork of email used for notifications</td>
        </tr>
        <tr>
            <td>EMAIL_PORT</td>
            <td>587</td>
            <td></td>
        </tr>
        <tr>
            <td>EMAIL_USE_TLS</td>
            <td>True</td>
            <td></td>
        </tr>
        <tr>
            <td>DATABASES: NAME</td>
            <td>roundware</td>
            <td>name of the roundware database</td>
        </tr>
        <tr>
            <td>DATABASES: USER</td>
            <td>round</td>
            <td>main database user</td>
        </tr>
        <tr>
            <td>DATABASES: PASSWORD</td>
            <td>round</td>
            <td></td>
        </tr>
        <tr>
            <td>ALLOWED_HOSTS</td>
            <td>*</td>
            <td>hosts from which users can login; should be restricted on production systems</td>
        </tr>
    </tbody>
</table>

## Django Settings

Other settings found in the default settings file are primarily Django-specific and can be adjusted as needed, referring to the [Django documentation](http://djangoproject.org/docs).
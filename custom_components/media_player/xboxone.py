"""
Support for functionality to interact with the Xbox One gaming console via SmartGlass protocol.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.xboxone/

CREDITS:
- This module is based on media_player.firetv component, initially created by @happyleavesaoc
- Original code: https://github.com/home-assistant/home-assistant/blob/dev/homeassistant/components/media_player/firetv.py
"""
import logging

import requests
import voluptuous as vol
from urllib.parse import urljoin

from homeassistant.components.media_player import (
    SUPPORT_NEXT_TRACK, SUPPORT_PAUSE, SUPPORT_PREVIOUS_TRACK, PLATFORM_SCHEMA,
    SUPPORT_SELECT_SOURCE, SUPPORT_TURN_OFF, SUPPORT_TURN_ON,
    SUPPORT_VOLUME_SET, SUPPORT_PLAY, MediaPlayerDevice,
    MEDIA_TYPE_MUSIC, MEDIA_TYPE_VIDEO, MEDIA_TYPE_TVSHOW, MEDIA_TYPE_CHANNEL)
from homeassistant.const import (
    STATE_IDLE, STATE_OFF, STATE_PAUSED, STATE_PLAYING, STATE_STANDBY,
    STATE_UNKNOWN, STATE_UNAVAILABLE, STATE_ON,
    CONF_HOST, CONF_PORT, CONF_SSL, CONF_NAME, CONF_DEVICE, CONF_DEVICES)
import homeassistant.util.dt as dt_util
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

SUPPORT_XBOXONE = SUPPORT_PAUSE | \
    SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_PREVIOUS_TRACK | \
    SUPPORT_NEXT_TRACK | SUPPORT_SELECT_SOURCE | SUPPORT_PLAY
    # SUPPORT_VOLUME_SET

DEFAULT_SSL = False
DEFAULT_HOST = 'localhost'
DEFAULT_NAME = 'Xbox One SmartGlass'
DEFAULT_PORT = 5557

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_DEVICE): cv.string,
    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Xbox One platform."""
    name = config.get(CONF_NAME)
    ssl = config.get(CONF_SSL)
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    liveid = config.get(CONF_DEVICE)

    proto = 'https' if ssl else 'http'
    base_url = '{0}://{1}:{2}'.format(proto, host, port)

    add_devices([XboxOneDevice(base_url, liveid, name)])


class XboxOne:
    def __init__(self, base_url, liveid):
        self.base_url = base_url
        self.liveid = liveid
        self._available = False
        self._connected = False
        self._media_status = None
        self._console_status = None

    def get(self, endpoint, *args, **kwargs):
        endpoint = endpoint.replace('<liveid>', self.liveid)
        full_url = urljoin(self.base_url, endpoint)
        return requests.get(full_url, *args, **kwargs)

    @property
    def available(self):
        return self._available

    @property
    def connected(self):
        return self._connected

    @property
    def console_status(self):
        return self._console_status

    @property
    def media_status(self):
        return self._media_status

    @property
    def media_playback_state(self):
        if self.media_status:
            return self.media_status.get('playback_status')

    @property
    def media_type(self):
        if self.media_status:
            return self.media_status.get('media_type')

    @property
    def media_position(self):
        if self.media_status:
            position = self.media_status.get('position')
            # Convert from nanoseconds
            if isinstance(position, int) and position >= 10000000:
                return position / 10000000

    @property
    def media_duration(self):
        if self.media_status:
            media_end = self.media_status.get('media_end')
            # Convert from nanoseconds
            if isinstance(media_end, int) and media_end >= 10000000:
                return media_end / 10000000

    @property
    def media_title(self):
        if self.media_status:
            return self.media_status.get('metadata', {}).get('title')

    @property
    def active_app(self):
        if self.console_status:
            active_titles = self.console_status.get('active_titles')
            app = [a.get('aum') for a in active_titles if a.get('has_focus')]
            if len(app):
                return app[0]

    @property
    def all_running_apps(self):
        if self.console_status:
            active_titles = self.console_status.get('active_titles')
            return [a.get('aum') for a in active_titles]

    def _check_authentication(self):
        try:
            response = self.get('/authentication').json()
            if response.get('authenticated'):
                return True

            response = self.get('/authentication/refresh').json()
            if response.get('success'):
                return True

        except requests.exceptions.RequestException:
            _LOGGER.error('Unreachable /authentication endpoint')
            return False

        _LOGGER.error('Refreshing authentication tokens failed!')
        return False

    def _refresh_devicelist(self):
        self.get('/devices')

    def _connect(self):
        if not self._check_authentication():
            return False
        try:
            response = self.get('/devices/<liveid>/connect').json()
            if not response.get('success'):
                _LOGGER.error('Failed to connect to console {0}: {1}'.format(self.liveid, str(response)))
                return False
        except requests.exceptions.RequestException:
            _LOGGER.error('Unreachable /connect endpoint')
            return False

        return True

    def _get_device_info(self):
        try:
            response = self.get('/devices/<liveid>').json()
            if not response.get('success'):
                _LOGGER.error('Console {0} not available'.format(self.liveid))
                return None
        except requests.exceptions.RequestException:
            _LOGGER.error('Unreachable device info /<liveid> endpoint')
            return None

        return response['device']

    def _get_console_status(self):
        try:
            response = self.get('/devices/<liveid>/console_status').json()
            if not response.get('success'):
                _LOGGER.error('Console {0} not available'.format(self.liveid))
                return None
        except requests.exceptions.RequestException:
            _LOGGER.error('Unreachable /console_status endpoint')
            return None

        return response['console_status']

    def _get_media_status(self):
        try:
            response = self.get('/devices/<liveid>/media_status').json()
            if not response.get('success'):
                _LOGGER.error('Console {0} not available'.format(self.liveid))
                return None
        except requests.exceptions.RequestException:
            _LOGGER.error('Unreachable /media_status endpoint')
            return None

        return response['media_status']

    def poweron(self):
        try:
            response = self.get('/devices/<liveid>/poweron').json()
            if not response.get('success'):
                _LOGGER.error('Failed to poweron {0}'.format(self.liveid))
                return None
        except requests.exceptions.RequestException:
            _LOGGER.error('Unreachable /poweron endpoint')
            return None

        return response

    def poweroff(self):
        try:
            response = self.get('/devices/<liveid>/poweroff').json()
            if not response.get('success'):
                _LOGGER.error('Failed to poweroff {0}'.format(self.liveid))
                return None
        except requests.exceptions.RequestException:
            _LOGGER.error('Failed to call poweroff for {0}'.format(self.liveid))
            return None

        return response

    def media_command(self, command):
        try:
            response = self.get('/devices/<liveid>/media').json()
            if not response.get('success'):
                return None
        except requests.exceptions.RequestException:
            _LOGGER.error('Failed to get enabled media commands for {0}'.format(self.liveid))
            return None

        enabled_commands = response.get('commands')
        if command not in enabled_commands:
            _LOGGER.error('Provided command {0} not enabled for current media'.format(command))
            return None

        try:
            response = self.get('/devices/<liveid>/media/{0}'.format(command)).json()
            if not response.get('success'):
                return None
        except requests.exceptions.RequestException:
            _LOGGER.error('Failed to get enabled media commands for {0}'.format(self.liveid))
            return None

        return response

    def launch_title(self, launch_uri):
        try:
            response = self.get('/devices/<liveid>/launch/{0}'.format(launch_uri)).json()
            if not response.get('success'):
                return None
        except requests.exceptions.RequestException:
            _LOGGER.error('Failed to launch title \'{0}\' for {1}'.format(launch_uri, self.liveid))
            return None

        return response

    def refresh(self):
        """
        Enumerate devices and refresh status info
        """
        self._refresh_devicelist()

        device_info = self._get_device_info()
        if not device_info or device_info.get('device_status') == 'Unavailable':
            self._available = False
            self._connected = False
        else:
            self._available = True

            connection_state = device_info.get('connection_state')
            if connection_state == 'Connected':
                self._connected = True
            else:
                success = self._connect()
                if not success:
                    _LOGGER.error('Failed to connect to {0}'.format(self.liveid))
                    self._connected = False
                else:
                    self._connected = True

        if self.available and self.connected:
            self._console_status = self._get_console_status()
            self._media_status = self._get_media_status()


class XboxOneDevice(MediaPlayerDevice):
    """Representation of an Xbox One device on the network."""

    def __init__(self, base_url, liveid, name):
        """Initialize the Xbox One device."""
        self._xboxone = XboxOne(base_url, liveid)
        self._name = name
        self._liveid = liveid
        self._state = STATE_UNKNOWN
        self._running_apps = None
        self._current_app = None

    @property
    def name(self):
        """Return the device name."""
        return self._name

    @property
    def unique_id(self):
        """Console Live ID"""
        return self._liveid

    @property
    def should_poll(self):
        """Device should be polled."""
        return True

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_XBOXONE

    @property
    def state(self):
        """Return the state of the player."""
        playback_state = {
            'Closed': STATE_IDLE,
            'Changing': STATE_IDLE,
            'Stopped': STATE_IDLE,
            'Playing': STATE_PLAYING,
            'Paused': STATE_PAUSED
        }.get(self._xboxone.media_playback_state)

        if playback_state:
            state = playback_state
        elif self._xboxone.connected or self._xboxone.available:
            state = STATE_IDLE
        else:
            state = STATE_OFF

        return state

    @property
    def media_content_type(self):
        """Media content type"""
        if self.state in [STATE_PLAYING, STATE_PAUSED]:
            return {
                'Music': MEDIA_TYPE_MUSIC,
                'Video': MEDIA_TYPE_VIDEO
            }.get(self._xboxone.media_type)

    @property
    def media_duration(self):
        """Duration in seconds"""
        if self.state in [STATE_PLAYING, STATE_PAUSED]:
            return self._xboxone.media_duration

    @property
    def media_position(self):
        """Position in seconds"""
        if self.state in [STATE_PLAYING, STATE_PAUSED]:
            return self._xboxone.media_position

    @property
    def media_position_updated_at(self):
        """Last valid time of media position"""
        if self.state in [STATE_PLAYING, STATE_PAUSED]:
            return dt_util.utcnow()

    @property
    def media_title(self):
        """When media is playing, print title (if any) - otherwise, print app name"""
        if self.state in [STATE_PLAYING, STATE_PAUSED]:
            return self._xboxone.media_title

        return self._xboxone.active_app

    @property
    def source(self):
        """Return the current app."""
        return self._xboxone.active_app

    @property
    def source_list(self):
        """Return a list of running apps."""
        return self._xboxone.all_running_apps

    def update(self):
        """Get the latest date and update device state."""
        self._xboxone.refresh()

    def turn_on(self):
        """Turn on the device."""
        self._xboxone.poweron()

    def turn_off(self):
        """Turn off the device."""
        self._xboxone.poweroff()

    def media_play(self):
        """Send play command."""
        self._xboxone.media_command('Play')

    def media_pause(self):
        """Send pause command."""
        self._xboxone.media_command('Pause')

    def media_stop(self):
        self._xboxone.media_command('Stop')

    def media_play_pause(self):
        """Send play/pause command."""
        self._xboxone.media_command('PlayPauseToggle')

    def media_previous_track(self):
        """Send previous track command."""
        self._xboxone.media_command('PreviousTrack')

    def media_next_track(self):
        """Send next track command."""
        self._xboxone.media_command('NextTrack')

    def select_source(self, source):
        """Select input source."""
        self._xboxone.launch_title(source)
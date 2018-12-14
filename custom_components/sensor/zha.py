"""
Sensors on Zigbee Home Automation networks.

For more details on this platform, please refer to the documentation
at https://home-assistant.io/components/sensor.zha/
"""
import logging

from homeassistant.components.sensor import DOMAIN
from homeassistant.components.zha import helpers
from homeassistant.components.zha.const import (
    DATA_ZHA, DATA_ZHA_DISPATCHERS, ZHA_DISCOVERY_NEW)
from homeassistant.components.zha.entities import ZhaEntity
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util.temperature import convert as convert_temperature

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['zha']


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Old way of setting up Zigbee Home Automation sensors."""
    pass


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Zigbee Home Automation sensor from config entry."""
    async def async_discover(discovery_info):
        await _async_setup_entities(hass, config_entry, async_add_entities,
                                    [discovery_info])

    unsub = async_dispatcher_connect(
        hass, ZHA_DISCOVERY_NEW.format(DOMAIN), async_discover)
    hass.data[DATA_ZHA][DATA_ZHA_DISPATCHERS].append(unsub)

    sensors = hass.data.get(DATA_ZHA, {}).get(DOMAIN)
    if sensors is not None:
        await _async_setup_entities(hass, config_entry, async_add_entities,
                                    sensors.values())
        del hass.data[DATA_ZHA][DOMAIN]


async def _async_setup_entities(hass, config_entry, async_add_entities,
                                discovery_infos):
    """Set up the ZHA sensors."""
    entities = []
    for discovery_info in discovery_infos:
        entities.append(await make_sensor(discovery_info))

    async_add_entities(entities, update_before_add=True)


async def make_sensor(discovery_info):
    """Create ZHA sensors factory."""
    from zigpy.zcl.clusters.measurement import (
        RelativeHumidity, TemperatureMeasurement, IlluminanceMeasurement
    )
    from zigpy.zcl.clusters.general import PowerConfiguration
    from zigpy.zcl.clusters.smartenergy import Metering
    from zigpy.zcl.clusters.homeautomation import ElectricalMeasurement
    in_clusters = discovery_info['in_clusters']
    if 'sub_component' in discovery_info:
        sensor = discovery_info['sub_component'](**discovery_info)
    elif RelativeHumidity.cluster_id in in_clusters:
        sensor = RelativeHumiditySensor(**discovery_info)
    elif TemperatureMeasurement.cluster_id in in_clusters:
        sensor = TemperatureSensor(**discovery_info)
    elif PowerConfiguration.cluster_id in in_clusters \
            and discovery_info['manufacturer'] == 'CentraLite':
        sensor = CentraliteBatterySensor(**discovery_info)
    elif Metering.cluster_id in in_clusters:
        sensor = MeteringSensor(**discovery_info)
    elif IlluminanceMeasurement.cluster_id in in_clusters:
        sensor = IlluminanceMeasurementSensor(**discovery_info)
    elif ElectricalMeasurement.cluster_id in in_clusters:
        sensor = ElectricalMeasurementSensor(**discovery_info)
        return sensor
    else:
        sensor = Sensor(**discovery_info)

    if discovery_info['new_join']:
        cluster = list(in_clusters.values())[0]
        await helpers.configure_reporting(
            sensor.entity_id, cluster, sensor.value_attribute,
            reportable_change=sensor.min_reportable_change
        )

    return sensor


class Sensor(ZhaEntity):
    """Base ZHA sensor."""

    _domain = DOMAIN
    value_attribute = 0
    min_reportable_change = 1

    @property
    def state(self) -> str:
        """Return the state of the entity."""
        if isinstance(self._state, float):
            return str(round(self._state, 2))
        return self._state

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state.

        False if entity pushes its state to HA.
        """
        return False

    def attribute_updated(self, attribute, value):
        """Handle attribute update from device."""
        _LOGGER.debug("Attribute updated: %s %s %s", self, attribute, value)
        if attribute == self.value_attribute:
            self._state = value
            self.async_schedule_update_ha_state()

    async def async_update(self):
        """Retrieve latest state."""
        result = await helpers.safe_read(
            list(self._in_clusters.values())[0],
            [self.value_attribute],
            allow_cache=False,
            only_cache=(not self._initialized)
        )
        self._state = result.get(self.value_attribute, self._state)

class TemperatureSensor(Sensor):
    """ZHA temperature sensor."""

    min_reportable_change = 50  # 0.5'C

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return self.hass.config.units.temperature_unit

    @property
    def state(self):
        """Return the state of the entity."""
        if self._state is None:
            return None
        celsius = self._state / 100
        return round(convert_temperature(celsius,
                                         TEMP_CELSIUS,
                                         self.unit_of_measurement),
                     1)


class RelativeHumiditySensor(Sensor):
    """ZHA relative humidity sensor."""

    min_reportable_change = 50  # 0.5%

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return '%'

    @property
    def state(self):
        """Return the state of the entity."""
        if self._state is None:
            return None

        return round(float(self._state) / 100, 1)

class PressureSensor(Sensor):
    """ZHA pressure sensor."""

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return 'hPa'

    @property
    def state(self):
        """Return the state of the entity."""
        if self._state is None:
            return None

        return round(float(self._state))

class GenericBatterySensor(Sensor):
    """ZHA generic battery sensor."""

    value_attribute = 32
    battery_sizes = {
        0: 'No battery',
        1: 'Built in',
        2: 'Other',
        3: 'AA',
        4: 'AAA',
        5: 'C',
        6: 'D',
        7: 'CR2',
        8: 'CR123A',
        255: 'Unknown'
    }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return '%'

    #@asyncio.coroutine
    async def async_update(self):
        """Retrieve latest state."""
        _LOGGER.debug("%s async_update", self.entity_id)

        result = await helpers.safe_read(
            self._endpoint.power,
            ['battery_size', 'battery_quantity', 'battery_voltage']
        )
        self._device_state_attributes['battery_size'] = \
            self.battery_sizes.get(
                result.get('battery_size', 255),
                'Unknown'
            )
        self._device_state_attributes['battery_quantity'] = result.get(
            'battery_quantity', 'Unknown')
        self._state = result.get('battery_voltage', self._state)


class CentraliteBatterySensor(GenericBatterySensor):
    """ZHA battery sensor."""

    # currently restricted to centralite sensors because the value
    # conversion is specific to centralite sensors.

    minVolts = 15
    maxVolts = 28
    values = {
        28: 100,
        27: 100,
        26: 100,
        25: 90,
        24: 90,
        23: 70,
        22: 70,
        21: 50,
        20: 50,
        19: 30,
        18: 30,
        17: 15,
        16: 1,
        15: 0
    }

    @property
    def state(self):
        """Return the state of the entity."""
        if self._state == 'unknown':
            return 'unknown'

        if self._state < self.minVolts:
            self._state = self.minVolts
        elif self._state > self.maxVolts:
            self._state = self.maxVolts

        return self.values.get(self._state, 'unknown')

    @property
    def icon(self):
        """Return battery icon."""
        return 'mdi:battery'

class MeteringSensor(Sensor):
    """ZHA Metering sensor."""

    value_attribute = 1024

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return 'W'

    @property
    def state(self):
        """Return the state of the entity."""
        if self._state is None:
            return None

        return round(float(self._state))


class ElectricalMeasurementSensor(Sensor):
    """ZHA Electrical Measurement sensor."""

    value_attribute = 1291

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return 'W'

    @property
    def force_update(self) -> bool:
        """Force update this entity."""
        return True

    @property
    def state(self):
        """Return the state of the entity."""
        if self._state is None:
            return None

        return round(float(self._state) / 10, 1)

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state.

        False if entity pushes its state to HA.
        """
        return True

    #@asyncio.coroutine
    async def async_update(self):
        """Retrieve latest state."""
        _LOGGER.debug("%s async_update", self.entity_id)

        result = await helpers.safe_read(
            self._endpoint.electrical_measurement, ['active_power'],
            allow_cache=False, only_cache=(not self._initialized))
        self._state = result.get('active_power', self._state)


class IlluminanceMeasurementSensor(Sensor):
    """ZHA lux sensor."""

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return 'lux'

    @property
    def state(self):
        """Return the state of the entity."""
        if self._state == 'unknown':
            return 'unknown'

        return self._state

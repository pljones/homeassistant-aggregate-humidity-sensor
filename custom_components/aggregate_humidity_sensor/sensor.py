"""
        HomeAssistant: Custom Aggregate Humidity Sensor Component
        Copyright (C) 2025 Peter L Jones

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU Affero General Public License as
        published by the Free Software Foundation, either version 3 of the
        License, or (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU Affero General Public License for more details.

        You should have received a copy of the GNU Affero General Public License
        along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)

DOMAIN = "aggregate_humidity_sensor"
DEFAULT_THRESHOLD = 70

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    panel = AggregateHumiditySensor(hass)
    await panel.async_load_threshold()
    async_add_entities([panel], True)
    async def set_threshold_service(call):
        threshold = call.data.get("threshold")
        if threshold is not None:
            await panel.async_set_threshold(threshold)
    hass.services.async_register(DOMAIN, "set_threshold", set_threshold_service)

class AggregateHumiditySensor(Entity):
    def __init__(self, hass):
        self._hass = hass
        self._state = "off"
        self._matching_sensors = []
        self._sensor_values = {}
        self._over_threshold_sensors = {}
        self._any_over_threshold = False
        self._threshold = DEFAULT_THRESHOLD
        self._store = Store(hass, 1, f"{DOMAIN}_threshold.json")

    @property
    def name(self):
        return "Humidity Panel"

    @property
    def state(self):
        return "on" if self._any_over_threshold else "off"

    @property
    def extra_state_attributes(self):
        return {
            "matching_sensors": self._matching_sensors,
            "sensor_values": self._sensor_values,
            "over_threshold_sensors": self._over_threshold_sensors,
            "any_over_threshold": self._any_over_threshold,
            "threshold": self._threshold,
        }

    async def async_load_threshold(self):
        data = await self._store.async_load()
        if data and "threshold" in data:
            try:
                self._threshold = float(data["threshold"])
            except (ValueError, TypeError):
                self._threshold = DEFAULT_THRESHOLD

    async def async_set_threshold(self, threshold):
        try:
            self._threshold = float(threshold)
            await self._store.async_save({"threshold": self._threshold})
            _LOGGER.info("AggregateHumiditySensor threshold set to %s", self._threshold)
            await self.async_update_ha_state(True)
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid threshold value: %s", threshold)

    async def async_update(self):
        sensors = [
            entity_id for entity_id in self._hass.states.async_entity_ids("sensor")
            if "humidity" in entity_id
        ]
        self._matching_sensors = sensors
        self._sensor_values = {}
        self._over_threshold_sensors = {}
        self._any_over_threshold = False
        for entity_id in sensors:
            state = self._hass.states.get(entity_id)
            try:
                value = float(state.state)
                self._sensor_values[entity_id] = value
                if value > self._threshold:
                    self._over_threshold_sensors[entity_id] = value
                    self._any_over_threshold = True
            except (ValueError, AttributeError):
                continue
        self._state = "on" if self._any_over_threshold else "off"

# Home Assistant Aggregate Humidity Sensor

A [Home Assistant](https://www.home-assistant.io/) custom integration that creates a **virtual aggregate humidity sensor**.
It dynamically discovers all humidity sensors (matching `sensor.*humidity*`), tracks their current values, and exposes:

- A binary state (`on` if any humidity exceeds a configurable threshold, otherwise `off`)
- A persistent, user-changeable threshold (default: 70)
- A list of all humidity sensors and their current values
- A list of sensors currently over threshold (with values)

**Includes:**
- Example Lovelace dashboard panel (`example/dashboard-panel.yaml`)
- Automation blueprint for handling state changes (`blueprints/automation/aggregate_humidity_sensor_state_change.yaml`)

---

## Features

- **Automatic discovery**: Tracks all humidity sensors matching `sensor.*humidity*`
- **Efficient**: Polls on a configurable interval (default: 30s)
- **User-configurable threshold**: Adjustable via service call; persists across restarts
- **Automation-friendly**: Blueprint for reacting to state changes, with access to which sensors exceeded threshold

---

## Installation

### Manual

1. Copy the `custom_components/aggregate_humidity_sensor/` directory to your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Add to your `configuration.yaml`:
    ```yaml
    sensor:
      - platform: aggregate_humidity_sensor
    ```
4. (Optional) Copy `example/aggregate-dashboard-sensor.yaml` into your Lovelace dashboard.

### HACS (Recommended)

1. In Home Assistant, go to **HACS > Integrations > Custom repositories**.
2. Add this repo URL as a custom repository of type **Integration**.
3. Install the **Humidity Panel** integration from HACS.
4. Restart Home Assistant.
5. Add to `configuration.yaml` as above.

---

## Usage

- The integration creates a sensor called `sensor.aggregate_humidity_sensor`.
- The sensor’s state is `"on"` if any discovered humidity sensor is above the threshold, `"off"` otherwise.
- The following attributes are available:
    - `matching_sensors`: List of all matched humidity sensors (`entity_id`s)
    - `sensor_values`: Dictionary of `entity_id` → value (float)
    - `over_threshold_sensors`: Dictionary of `entity_id` → value for sensors currently over threshold
    - `any_over_threshold`: Boolean (same as sensor state)
    - `threshold`: The currently applied threshold

### Changing the threshold

After some AI-assisted research, I recommend 70% RH as the point at which to concentrate effort
on reducing humidity rather than raising temperature to remain warm.  Above this level, damp reduces
the effectiveness of clothing and heating and it is more cost-effective in domestic situations to
spend resources on reducing humidity.  You may want to choose a lower value, as that's better for
long term health.  Going below 40% is not recommended.

Call the service:

```yaml
service: aggregate_humidity_sensor.set_threshold
data:
  threshold: 65  # Set your desired value
```

---

## Example Dashboard Panel

The `example/dashboard-panel.yaml` file provides:

- An auto-entities card showing all humidity sensors, sorted by value, using the sensor list discovered by the integration.
- A "Humidity" button that turns red if any sensor is over threshold.

To use:
1. Install [auto-entities card](https://github.com/thomasloven/lovelace-auto-entities) and [button-card](https://github.com/custom-cards/button-card) via HACS.
2. Copy-paste the contents of `example/dashboard-panel.yaml` into your Lovelace dashboard (YAML mode or as a manual card).

---

## Automation Blueprint

Included at:
`blueprints/automation/aggregate_humidity_sensor_state_change.yaml`

This blueprint triggers on **any state change** of `sensor.aggregate_humidity_sensor` and exposes the new and old state as variables in your actions.
You can use this to, for example, start a timer to leave a dehumidifier running for an hour after humidity drops below threshold.

**Example usage:**

```yaml
use_blueprint:
  path: pljones/aggregate_humidity_sensor/aggregate_humidity_sensor_state_change.yaml
  input:
    aggregate_humidity_sensor_sensor: sensor.aggregate_humidity_sensor
    actions:
      - choose:
          - conditions: "{{ new_state == 'off' and old_state == 'on' }}"
            sequence:
              - service: timer.start
                target:
                  entity_id: timer.dehumidifier_off
          - conditions: "{{ new_state == 'on' and old_state == 'off' }}"
            sequence:
              - service: switch.turn_on
                target:
                  entity_id: switch.dehumidifier
```

Use `state_attr('sensor.aggregate_humidity_sensor', 'over_threshold_sensors')` in your actions to get the dictionary of sensors currently over threshold.

---

## Development & Support

- This integration is custom and not affiliated with Home Assistant core.
- For issues or feature requests, please open an issue on GitHub.

---

## Copyright

Custom Aggregate Humidity Sensor Component -- Copyright (C) 2025 Peter L Jones

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

---

## License

GNU Affero 3.0 - see [LICENCE.md](LICENCE.md) or https://www.gnu.org/licenses/agpl-3.0.html

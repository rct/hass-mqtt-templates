# hass-mqtt-templates

Proof of concept (PoC) for generating Home Assistant YAML configuration files for 
rtl_433 MQTT entities using Jinja2.

This PoC focuses on Honeywell Security sensors. Autodiscovery can't do a 
complete job for these devices, because the device messages don't contain all of
the information needed. There are tradeoffs for both manual configuration and 
autodiscovery. Discussion on static YAML config vs. autodiscovery via
JSON and MQTT will be provided on the GitHub repo.  

See [FAQ and Motivation](FAQ_and_Motivation.md) for more background.

## How this works

A sensor definition YAML file defines the sensor details such as the Channel/ID
sent by rtl_433 as well as other configuration information not available from
rtl_433 such as type: window/door/motion, etc. and suggested area. Sensors are
grouped under a name/key "honewell_security".

### sensors-example.yaml -- Source configuration information for sensors
```yaml
honeywell_security:
- esn: 123456
  name: "Front Door"
  type: "door"
  model: "Honeywell 5800mini"
  area: "Foyer"
  description: "Main Entrance Active Door"
  model_comment: "4th 5800mini"
  zone: 1


- esn: 654321
  name: "Guest Bedroom Window"
  type: "Window"
  model: "Versa Mini"
  manufacturer: "Versa"
  area: "Guest Bedroom"
  description: "Guest Bedroom East Window"
  model_comment: "Versa Mini, 1st from 2nd batch"
  channel: 10
  rtl_433_contact_field: "reed_open"
  zone: 18
```

A template mapping file, lists the Jinja2 template(s) that should be applied for
each sensor defined under a given key like "honeywell_security".

### sensor_type_mapping.yaml -- mapping from sansor names to templates

```yaml
sensor_templates:
    honeywell_security:
      - "honeywell_security_contact.j2"
      - "generic_battery_ok.j2"
      - "generic_rssi_snr_noise.j2"
```

See the directory `out-example` for the generated sensor configuration files:

* [Honeywell 5800mini used as a door sensor](out-example/rtlmqtt_front_door_sensor.yaml)
* [Versa/2Gig Mini used as a window sensor](out-example/rtlmqtt_guest_bedroom_window_sensor.yaml)

These two examples show:

* Starting with the desired name for the device so it can be used consistently throughout.
* Defining the correct Home Assistant device class `door` vs `window` so the icons and text match the way the device is used.
* Making device specific model and manufacturer available to Home Assistant.
* Two very similar but slightly different sensors (Honeywell 5800mini vs Versa/2Gig mini). rtl_433 decodes both as `Honeywell-Security`. The only difference in the message is that all Honeywell devices use `channel = 8`, where the Versa Mini's use `channel = 10`. This isn't actually an identifier for the sensor but rather than manufacturer.
 

## Adding the generated files to Home Assistant.

These files are intended to be placed in a packages directory under your 
Home Assistant Configuration directory (typically `config`).  

There should be `packages:` block under `homeassistant:` in your
`configuration.yaml`.

```yaml
homeassistant:
  # load packages
  packages: !include_dir_named integrations
```

For more info see thedocumentation and other guidance (some from Frenck) and 
others about _splitting your Home Assistant configuration file_

## Running

This is a simple Python CLI script. It can be run anywhere you have a recent
version of Python 3 installed along with the Python YAML and Jinja2 modules -- 
`pip install PyYAML Jinja2` 

You should be able to run this on your Home Assistant installation under the
_Advanced SSH and Web Terminal Add On_  (Frenk's community add-on, not the core
add-on which is more limited.)

In that environment, PyYAML is already installed but you need to add Jinja2 by running:

`apk add py3-jinja2`

## Who this is for

At this stage this is only intended to be a proof of concept for exploration
of alternatives to autodiscovery. This won't be a full fledged app or add-on.

It is intended for people who have a lot of devices, are comfortable with YAML,
Home Assistant Templates (aka Jinja2), and using CLIs, particularly Linux.

## Comments, Feedback, etc.

This PoC is at the point where "it is useful for me". I wanted to make it
available to others for discussion, feedback, and hopefully some etter ideas
from the community.


# hass-mqtt-templates

Proof of concept for generating Home Assistant YAML configuration files for 
rtl_433 MQTT entities using Jinja2.

This PoC focuses on Honeywell Security sensors. Autodiscovery can't do a 
complete job for these devices, because the device messages don't contain all of
the information needed. There are tradeoffs for both manual configuration and 
autodiscovery. Discussion on static YAML config vs. autodiscovery via
JSON and MQTT will be provided on the GitHub repo.

## How this works

A sensor definition YAML file defines the sensor details such as the Channel/ID
sent by rtl_433 as well as other configuration information not available from
rtl_433 such as type: window/door/motion, etc. and suggested area. Sensors are
grouped under a name/key "honewell_security".

### sensor_type_mapping.yaml -- mapping from sansor names to templates

```yaml
sensor_templates:
    honeywell_security:
      - "test_honeywell2.j2"
      - "generic_battery_ok.j2"
      - "generic_rssi_snr_noise.j2"
```

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
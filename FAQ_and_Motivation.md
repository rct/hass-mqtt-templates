# Motivation and FAQ

## Goals for this project/Proof of Concept (PoC)

1. Use *automation* for creating and maintaining MQTT sensor configuration files
where there are considerable number of devices/entities to be brought into Home
Assistant.
1. Reduce the number of places configuration is stored.
1. Bring configuration under source code control.
1. Allow "bulk edits" with "familiar" tools such as your favorite editor/IDE and CLI tools
1. Enable single source configuration for things outside of Home Assistant
 (like alarm panel and central station communication)
1. Simplify where possible with a Small learning curve, ideally using familiar technologies.

Finally, YAML and Home Assistant templates (aka Jinja2 templates) are the way that
most intermediate to advanced work is done in Home Assistant, whether it is 
configuration, automation, or scripts. 

## Why not use auto discovery? 

Auto discovery when it recognizes your device correctly and you don't have to do 
much additional configuration is great. If you have a small number 
of devices or are just starting out with Home Assistant auto discovery seems the 
right way to go.

Auto discovery works well for Zigbee2MQTT and ZwaveJS (UI). If there was a full-fledged GUI application like Zigbee2MQTT with persistent configuration storage for rtl_433 and other MQTT devices that would most likely be the way to go. 

If you have dozens of devices there are a number of downsides of auto discovery:

. Default names are created using device identifiers. Many RF ISM band devices available through rtl_433 do not have permanent identifiers. When batteries are changed, they will show up as a new device. It can be cumbersome to correct the names and reconnect previous history.
. Customizations such as renaming devices to friendly names are stored separately in Home Assistant's `.storage/config*json` files. The data in those files is intended to be private to Home Assistant and not accessed by other code. The only supported way to move that configuration to another Home Assistant installation is via a full restore of Home Assistant's configuration direction. You could edit the configuration in MQTT using something like MQTT Explorer, but then persistance/reliability of that configuration becomes a problem.
. You wind up with an additional collection of configuration information stored in MQTT as retained messages. How do you backup, restore, or version control that information? You could re-run auto discovery again, but you've got to wait for all devices to transmit again. Some devices may only transmit once every 1-2 hours to conserve battery life. There are devices (Govee water sensors) that don't transmit for days or weeks.
. Auto discovery configuration is in JSON, which makes sense for sending over MQTT. However, User-accessible configuration in Home Assistant is in YAML. For the most part the formats can be converted to the other, but it can be cumbersome and confusing. Home Assistant configuration documentation primarily covers YAML.

## Why use Jinja2 templates?

The templates used in Home Assistant configuration are implemented using Jinja2. Most Home Assistant users, who go beyond the basics, learn some amount of Home Assistant template basics at some point. 

Jinja2 is also used in the Python Flask web framework and in the Ansible automation system. I use Ansible for configuration and system management of my personal systems.

## Why running the rtl_433_mqtt_hass.py auto discovery full time doesn't make sense?

There are several reasons why it doesn't make sense to always leave the auto discovery script running

* Devices usually aren't added very often. The Zigbee2MQTT web app has a button for enabling auto join. The auto discovery should be similar. Turn it on when needed, then disable it.
* Retained storage for the config topics is needed if you want devices to be available soon after restarting Home Assistant and/or your MQTT broker.
* Phantom devices get created for a number of reasons. There isn't currently a process to approve newly discovered devices. Cleaning up after them can be cumbersome in both MQTT (retained messages) and Home Assistant.

## Why not fix some of the existing problems in rtl_433_mqtt_hass.py auto discovery script?

The current script works well for some devices but it isn't a very robust solution and has a number of shortcomings the way it is currently built. Improving things would require some significant changes.

For example, currently the script works only at the data field level. There is currently no way to define how a specific device (model or protocol in rtl_433's terms) should be handled.

The way the script currently works is that if there is a field in a rtl_433 message, such as `temperature_C` or `humidity` and a JSON template exists for in in the script,  It will create a Home Assistant entity for that piece of information. That works well for things like temperature and humidity where the handling is very common across all devices.

Where this becomes a problem is when devices have different intepreatations of  `state` or `contact_open`. It is complicated for cases (some security devices) where the way a device is used determines which fields should be used. 

## Why are there two sets of variable names such as `name` and `device_name_pretty`? 

Currently there is a level of indirection in the script that turns YAML names from the source file into longer more processed names that the generated Home Assistant config template uses. For example, the value of `name:` gets mapped into a Jinja2 variable called `device_name_pretty`.

This is an area that needs more thought. But the reasons I implemented it this way are:

* The ability to drive more than just Home Assistant configuration.
* Recognizing that some target system specific processing might be needed.
* Avoiding redundancy in the source data to get pretty and YAML safe names `Front Door` vs `front_door` 

For the PoC this is implmeneted in a quick and dirty function `process_honeywell`.

This needs more thought about generalizing this but not turning this into too much of it's own DSL, etc.


(@todo)


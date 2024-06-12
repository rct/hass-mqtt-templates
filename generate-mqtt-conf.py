#!/opt/pyvenvs/ansible-py312/bin/python
# coding=utf-8

AP_DESCRIPTION="""
Proof of concept for generating Home Assistant YAML configuration files for 
MQTT entities via rtl_433 -> MQTT using Jinja2.

This PoC focuses on Honeywell Security sensors. Autodiscovery can't do a 
complete job for these devices, because the device messages don't contain all of
the information needed. There are tradeoffs for both manual configuration and 
autodiscovery. Discussion on static YAML config vs. autodiscovery via
JSON and MQTT will be provided on the GitHub repo.

How this works

A sensor definition YAML file defines the sensor details such as the Channel/ID
sent by rtl_433 as well as other configuration information not available from
rtl_433 such as type: window/door/motion, etc. and suggested area. Sensors are
grouped under a name/key "honewell_security".

A template mapping file, lists the Jinja2 template(s) that should be applied for
each sensor defined under a given key like "honeywell_security".
"""

AP_EPILOG="""
For more info and discussion see https://github.com/rct/hass-mqtt-templates
(or possibly a discussion to be created on merbanan/rtl_433.)
"""

import sys, os, argparse, time, datetime, logging
import yaml
import jinja2
import typing

# XXX fix quick hack for dev
log = logging.getLogger("")

def yaml_sanitize(text: str) -> str:
    """make string YAML/MQTT safe"""

    return(text
           .lower()
           .replace(" ", "_")
           .replace("/", "_")
           .replace(".", "_")
    )

def parse_definitions(yamlstr):
    """Parse sensor definitions"""

    try:
        sensors = yaml.safe_load(yamlstr)

    except yaml.YAMLError as exc:
            print("Error parsing YAML file")
            print(exc)
            # XXX @todo bettern error handling, and shouldn't exit
            sys.exit(-1)
    
    return(sensors)

def process_honeywell(sd: dict[str]):
    """
    Process one honeywell sensor
    
    The majority of the mappings take place here. 
    Many of these are straight forward maping one key name to another
    However there is some logic to deal with defaults, case, etc.

    There are a number of better ways to do this rather than a hardcoded
    function. Most of the manipulation done in this function could be
    done in Jinja2 itself.
    """

    jv: dict[str] = {} # Variables to pass to Jinja

    dev_name: str = sd['name']
    dev_name_safe: str = yaml_sanitize(dev_name) 
    dev_manufacturer = sd.get("manufacturer", "Honeywell") # XXX @todo fix 
    dev_rtl_model = sd.get("rtl_433_model", "Honeywell-Security")
    dev_channel = sd.get("channel", "8")
    dev_esn = sd['esn']
    dev_rtl_contact_field = sd.get("rtl_433_contact_field", "contact_open")
    dev_unique_id = f"rtl_433_{dev_manufacturer.lower()}" + \
        f"_{dev_channel}_{dev_esn}"
    dev_topic = f"rtl_433/+/devices/{dev_rtl_model}/{dev_channel}/{dev_esn}"
    dev_unavailable_seconds = sd.get("unavailable_timeout", 7200)

    jv['device_name_pretty'] = f"{dev_name} Sensor"    # "Front Door Sensor"
    jv['device_name_safe'] = dev_name_safe + "_sensor" # "front_door_sensor"
    jv['contact_short_name'] = sd['type']    # "Door"
    jv['device_primary_class'] = sd['type'].lower()
    jv['device_model'] = sd['model']                  # "Honeywell 5800mini"
    jv['device_manufacturer'] = dev_manufacturer           
    jv['device_area'] = sd['area']                    # "Foyer" "Main Entrance"
    jv['device_unique_id'] = dev_unique_id   # "rtl_433_honeywell_8_123456"
    jv['device_topic'] = dev_topic 
    jv['contact_sub_topic'] = dev_rtl_contact_field
    jv['device_unavailable_seconds'] = dev_unavailable_seconds

    return(jv)


def main():

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, 
        description=AP_DESCRIPTION, epilog=AP_EPILOG)
    parser.add_argument('-s', '--sensor_file', dest='sensor_file',
                        type=argparse.FileType('rt'),
                        default='sensors-example.yaml')
    parser.add_argument('--template_path', dest='template_path', 
                        default='./templates',
                        help='Path for Jinja2 templates')
    parser.add_argument('-m', '--model_templates', dest='sensor_map_file',
                        type=argparse.FileType('rt'),
                        default='sensor_type_mapping.yaml',
                        help='Sensor type to template map')
    parser.add_argument('-o', '--output_dir', dest='output_dir', 
                        default="./out-example", 
                        help='Directory to hold outputfiles')
    parser.add_argument('--sensor_key', dest='sensor_key',
                        default='honeywell_sensors',
                        help='Name/key for YAML block defining sensors')
    parser.add_argument('-d', '--debug', dest='debug', default=False,
                        action='store_true', help='Debug output')
    parser.add_argument('--dryrun', dest='dryrun', action='store_true',
                        help="Output to STDOUTT, do not write output files")

    output_directory = "./out"

    args = parser.parse_args()

    # log = logging.getLogger("")
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s " + "[%(module)s:%(lineno)d] %(message)s"
    )
    # setup console logging
    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    log.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    ch.setFormatter(formatter)
    log.addHandler(ch)

    sensors = parse_definitions(args.sensor_file)
    sensor_templates_config = parse_definitions(args.sensor_map_file)
    sensor_templates = sensor_templates_config['sensor_templates'] # pull out the one key for now, maybe more later

    log.debug(f"Template Source Directory: {args.template_path}, Output Directory: {args.output_dir}")
    log.debug(f"Source Sensor Data: {args.sensor_file}, Template Mapping File: {args.sensor_map_file}")


    # Create Jinja2 environment
    jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=args.template_path),
                              trim_blocks=True,
                              lstrip_blocks=True)
    

    for sensor_group in sensors:
        template_list = sensor_templates[sensor_group]
        log.info(f"Processing sensor group: {sensor_group} with {template_list}")


        

    for sensor in sensors[sensor_group]:

        jv = process_honeywell(sensor) # Load & convert sensor definition into Jinja ready vars

        out = ""

        for template_file in template_list:
            template = jenv.get_template(template_file)

            log.debug(f"Processing sensor {sensor} with {template_file}")

            out_yaml = template.render(jv)

            out += out_yaml

        if not args.dryrun: 
            output_filename = os.path.join(args.output_dir, f"rtlmqtt_{jv['device_name_safe']}.yaml")

            log.info(f"Writing {output_filename}")

            of = open(output_filename, "wt")
            of.write(out)
            of.close()
        else:
            print()
            print("=" * 76)
            print(f"rtlmqtt_{jv['device_name_safe']}.yaml")
            print("=" * 76)

            print(out)
            print()



if __name__ == "__main__":
    main()



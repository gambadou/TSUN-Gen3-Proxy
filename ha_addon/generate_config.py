#!/usr/bin/with-contenv bashio
# ==============================================================================
# TSUN Gen3 Proxy Add-on - Configuration Generator
# Generates config.toml from Home Assistant add-on options
# ==============================================================================

import json
import os
from pathlib import Path
import bashio

def generate_config():
    """Generate config.toml from Home Assistant add-on options."""
    
    # Get options from Home Assistant
    mqtt_host = bashio.config('mqtt_host')
    mqtt_port = bashio.config('mqtt_port')
    mqtt_user = bashio.config('mqtt_user')
    mqtt_password = bashio.config('mqtt_password')
    tsun_cloud_enabled = bashio.config('tsun_cloud_enabled')
    solarman_cloud_enabled = bashio.config('solarman_cloud_enabled', True)
    log_level = bashio.config('log_level', 'info')
    inverters = bashio.config('inverters', [])
    batteries = bashio.config('batteries', [])
    
    # Prepare config content
    config_content = f"""##########################################################################################
###
###          T S U N  -  G E N 3  -   P R O X Y
###
###   Home Assistant Add-on Configuration
###   Generated automatically from add-on options
###
##########################################################################################

##########################################################################################
##
## MQTT broker configuration
##
mqtt.host    = '{mqtt_host}'
mqtt.port    = {mqtt_port}
mqtt.user    = '{mqtt_user}'
mqtt.passwd  = '{mqtt_password}'

##########################################################################################
##
## HOME ASSISTANT
##
ha.auto_conf_prefix = 'homeassistant'
ha.discovery_prefix = 'homeassistant'
ha.entity_prefix    = 'tsun'
ha.proxy_node_id    = 'proxy'
ha.proxy_unique_id  = 'P170000000000001'

##########################################################################################
##
## GEN3 Proxy Mode Configuration
##
tsun.enabled = {str(tsun_cloud_enabled).lower()}
tsun.host    = 'logger.talent-monitoring.com'
tsun.port    = 5005

##########################################################################################
##
## GEN3PLUS Proxy Mode Configuration
##
solarman.enabled = {str(solarman_cloud_enabled).lower()}
solarman.host    = 'iot.talent-monitoring.com'
solarman.port    = 10000

##########################################################################################
##
## Inverter Definitions
##
inverters.allow_all = false
"""

    # Add inverters configuration
    for inverter in inverters:
        serial = inverter.get('serial', '')
        node_id = inverter.get('node_id', 'inv_1')
        monitor_sn = inverter.get('monitor_sn')
        suggested_area = inverter.get('suggested_area', '')
        modbus_polling = inverter.get('modbus_polling', False)
        client_mode_host = inverter.get('client_mode_host')
        client_mode_port = inverter.get('client_mode_port', 8899)
        
        config_content += f"\n[inverters.\"{serial}\"]\n"
        config_content += f"node_id = '{node_id}'\n"
        if suggested_area:
            config_content += f"suggested_area = '{suggested_area}'\n"
        if monitor_sn:
            config_content += f"monitor_sn = {monitor_sn}\n"
        config_content += f"modbus_polling = {str(modbus_polling).lower()}\n"
        
        if client_mode_host:
            config_content += f"client_mode = {{host = '{client_mode_host}', port = {client_mode_port}, forward = true}}\n"
        
        # Add PV modules if specified
        for i in range(1, 5):
            pv_type = inverter.get(f'pv{i}_type')
            pv_manufacturer = inverter.get(f'pv{i}_manufacturer')
            if pv_type and pv_manufacturer:
                config_content += f"pv{i} = {{type = '{pv_type}', manufacturer = '{pv_manufacturer}'}}\n"
    
    # Add batteries configuration
    for battery in batteries:
        serial = battery.get('serial', '')
        node_id = battery.get('node_id', 'bat_1')
        monitor_sn = battery.get('monitor_sn')
        suggested_area = battery.get('suggested_area', '')
        modbus_polling = battery.get('modbus_polling', True)
        client_mode_host = battery.get('client_mode_host')
        client_mode_port = battery.get('client_mode_port', 8899)
        
        config_content += f"\n[batteries.\"{serial}\"]\n"
        config_content += f"node_id = '{node_id}'\n"
        if suggested_area:
            config_content += f"suggested_area = '{suggested_area}'\n"
        config_content += f"monitor_sn = {monitor_sn}\n"
        config_content += f"modbus_polling = {str(modbus_polling).lower()}\n"
        
        if client_mode_host:
            config_content += f"client_mode = {{host = '{client_mode_host}', port = {client_mode_port}, forward = true}}\n"
        
        # Add PV modules if specified
        for i in range(1, 3):
            pv_type = battery.get(f'pv{i}_type')
            pv_manufacturer = battery.get(f'pv{i}_manufacturer')
            if pv_type and pv_manufacturer:
                config_content += f"pv{i} = {{type = '{pv_type}', manufacturer = '{pv_manufacturer}'}}\n"
    
    # Add AT command filters
    config_content += """

##########################################################################################
##
## AT+ Command Access Control (GEN3PLUS only)
##
[gen3plus.at_acl]
tsun.allow = ['AT+Z', 'AT+UPURL', 'AT+SUPDATE']
tsun.block = []
mqtt.allow = ['AT+']
mqtt.block = []
"""
    
    # Write config file
    config_path = Path('/config/tsun-proxy/config.toml')
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    bashio.log.info(f"Configuration file generated: {config_path}")

if __name__ == '__main__':
    generate_config()
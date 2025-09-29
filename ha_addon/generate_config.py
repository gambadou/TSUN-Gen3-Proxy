#!/usr/bin/env python3
# ==============================================================================
# TSUN Gen3 Proxy Add-on - Configuration Generator
# Generates config.toml from Home Assistant add-on options
# ==============================================================================

import json
import os
import sys
from pathlib import Path

def get_addon_options():
    """Récupère les options de l'add-on depuis le fichier d'options HA"""
    options_file = '/data/options.json'
    if os.path.exists(options_file):
        with open(options_file, 'r') as f:
            return json.load(f)
    
    # Options par défaut si fichier non trouvé
    return {
        'mqtt_host': 'core-mosquitto',
        'mqtt_port': 1883,
        'mqtt_user': '',
        'mqtt_password': '',
        'tsun_cloud_enabled': True,
        'solarman_cloud_enabled': True,
        'log_level': 'info',
        'inverters': [],
        'batteries': []
    }

def generate_config():
    """Generate config.toml from Home Assistant add-on options."""
    
    # Get options from Home Assistant
    options = get_addon_options()
    
    mqtt_host = options.get('mqtt_host', 'core-mosquitto')
    mqtt_port = options.get('mqtt_port', 1883)
    mqtt_user = options.get('mqtt_user', '')
    mqtt_password = options.get('mqtt_password', '')
    tsun_cloud_enabled = options.get('tsun_cloud_enabled', True)
    solarman_cloud_enabled = options.get('solarman_cloud_enabled', True)
    log_level = options.get('log_level', 'info')
    inverters = options.get('inverters', [])
    batteries = options.get('batteries', [])
    
    print(f"Génération de la configuration avec MQTT: {mqtt_host}:{mqtt_port}")
    
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
    
    print(f"Configuration file generated: {config_path}")
    return True

if __name__ == '__main__':
    try:
        generate_config()
        print("Configuration générée avec succès")
    except Exception as e:
        print(f"Erreur lors de la génération de configuration: {e}")
        sys.exit(1)
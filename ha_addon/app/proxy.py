#!/usr/bin/env python3
"""
TSUN Gen3 Proxy for Home Assistant Add-on
Adapté du projet original s-allius/tsun-gen3-proxy
"""

import asyncio
import logging
import os
import sys
import socket
import struct
import time
from pathlib import Path
import toml
import aiomqtt
from datetime import datetime, timezone
import json
import signal

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TsunProxy:
    """Proxy principal pour les onduleurs TSUN"""
    
    def __init__(self, config_path='/config/tsun-proxy/config.toml'):
        self.config_path = config_path
        self.config = None
        self.mqtt_client = None
        self.servers = []
        self.running = False
        self.load_config()
        
    def load_config(self):
        """Charge la configuration depuis le fichier TOML"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = toml.load(f)
            logger.info(f"Configuration chargée depuis {self.config_path}")
        except FileNotFoundError:
            logger.error(f"Fichier de configuration non trouvé: {self.config_path}")
            # Configuration par défaut
            self.config = self._default_config()
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            self.config = self._default_config()
    
    def _default_config(self):
        """Configuration par défaut"""
        return {
            'mqtt': {
                'host': 'core-mosquitto',
                'port': 1883,
                'user': '',
                'passwd': ''
            },
            'ha': {
                'auto_conf_prefix': 'homeassistant',
                'discovery_prefix': 'homeassistant',
                'entity_prefix': 'tsun',
                'proxy_node_id': 'proxy',
                'proxy_unique_id': 'P170000000000001'
            },
            'tsun': {
                'enabled': True,
                'host': 'logger.talent-monitoring.com',
                'port': 5005
            },
            'solarman': {
                'enabled': True,
                'host': 'iot.talent-monitoring.com',
                'port': 10000
            },
            'inverters': {
                'allow_all': False
            }
        }
    
    async def setup_mqtt(self):
        """Configure la connexion MQTT"""
        try:
            mqtt_config = self.config.get('mqtt', {})
            self.mqtt_client = aiomqtt.Client(
                hostname=mqtt_config.get('host', 'core-mosquitto'),
                port=mqtt_config.get('port', 1883),
                username=mqtt_config.get('user') if mqtt_config.get('user') else None,
                password=mqtt_config.get('passwd') if mqtt_config.get('passwd') else None
            )
            logger.info(f"Connexion MQTT configurée: {mqtt_config.get('host')}:{mqtt_config.get('port')}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la configuration MQTT: {e}")
            return False
    
    async def publish_ha_discovery(self, device_type, serial, device_data):
        """Publie la configuration de découverte automatique pour Home Assistant"""
        if not self.mqtt_client:
            return
        
        ha_config = self.config.get('ha', {})
        discovery_prefix = ha_config.get('discovery_prefix', 'homeassistant')
        entity_prefix = ha_config.get('entity_prefix', 'tsun')
        
        # Configuration de base du device
        device_info = {
            "identifiers": [serial],
            "manufacturer": "TSUN",
            "model": device_type,
            "name": f"TSUN {device_type} {serial}",
            "sw_version": "1.0.0"
        }
        
        # Sensors pour un onduleur
        sensors = [
            {"key": "power", "name": "Power", "unit": "W", "device_class": "power", "state_class": "measurement"},
            {"key": "energy_today", "name": "Energy Today", "unit": "kWh", "device_class": "energy", "state_class": "total_increasing"},
            {"key": "energy_total", "name": "Energy Total", "unit": "kWh", "device_class": "energy", "state_class": "total_increasing"},
            {"key": "voltage", "name": "Voltage", "unit": "V", "device_class": "voltage", "state_class": "measurement"},
            {"key": "current", "name": "Current", "unit": "A", "device_class": "current", "state_class": "measurement"},
            {"key": "temperature", "name": "Temperature", "unit": "°C", "device_class": "temperature", "state_class": "measurement"}
        ]
        
        for sensor in sensors:
            config_topic = f"{discovery_prefix}/sensor/{entity_prefix}_{serial}_{sensor['key']}/config"
            state_topic = f"{entity_prefix}/{serial}/{sensor['key']}"
            
            config_payload = {
                "name": sensor['name'],
                "unique_id": f"{entity_prefix}_{serial}_{sensor['key']}",
                "state_topic": state_topic,
                "unit_of_measurement": sensor['unit'],
                "device_class": sensor['device_class'],
                "state_class": sensor['state_class'],
                "device": device_info
            }
            
            try:
                await self.mqtt_client.publish(config_topic, json.dumps(config_payload), retain=True)
                logger.debug(f"Configuration Home Assistant publiée: {config_topic}")
            except Exception as e:
                logger.error(f"Erreur lors de la publication de la configuration HA: {e}")
    
    async def publish_sensor_data(self, serial, sensor_key, value):
        """Publie les données de capteur vers MQTT"""
        if not self.mqtt_client:
            return
            
        ha_config = self.config.get('ha', {})
        entity_prefix = ha_config.get('entity_prefix', 'tsun')
        topic = f"{entity_prefix}/{serial}/{sensor_key}"
        
        try:
            await self.mqtt_client.publish(topic, str(value))
            logger.debug(f"Données publiées: {topic} = {value}")
        except Exception as e:
            logger.error(f"Erreur lors de la publication des données: {e}")
    
    def parse_tsun_data(self, data):
        """Parse les données reçues des onduleurs TSUN"""
        try:
            # Exemple de parsing basique - à adapter selon le protocole TSUN réel
            if len(data) < 20:
                return None
            
            # Extraction basique des données (à adapter selon le protocole réel)
            parsed_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'power': struct.unpack('<I', data[8:12])[0] / 10.0,  # Exemple
                'voltage': struct.unpack('<H', data[12:14])[0] / 10.0,
                'current': struct.unpack('<H', data[14:16])[0] / 100.0,
                'temperature': struct.unpack('<h', data[16:18])[0] / 10.0,
                'energy_today': struct.unpack('<I', data[18:22])[0] / 100.0 if len(data) >= 22 else 0,
                'energy_total': struct.unpack('<I', data[22:26])[0] / 100.0 if len(data) >= 26 else 0
            }
            
            return parsed_data
        except Exception as e:
            logger.error(f"Erreur lors du parsing des données: {e}")
            return None
    
    async def handle_inverter_connection(self, reader, writer, port):
        """Gère une connexion d'onduleur"""
        client_addr = writer.get_extra_info('peername')
        logger.info(f"Nouvelle connexion onduleur depuis {client_addr} sur port {port}")
        
        # Connexion au cloud TSUN si activée
        tsun_writer = None
        if port == 5005 and self.config.get('tsun', {}).get('enabled', True):
            try:
                tsun_reader, tsun_writer = await asyncio.open_connection(
                    self.config['tsun']['host'],
                    self.config['tsun']['port']
                )
                logger.info(f"Connexion au cloud TSUN établie: {self.config['tsun']['host']}")
            except Exception as e:
                logger.warning(f"Impossible de se connecter au cloud TSUN: {e}")
        
        # Connexion au cloud Solarman si activée
        solarman_writer = None
        if port == 10000 and self.config.get('solarman', {}).get('enabled', True):
            try:
                solarman_reader, solarman_writer = await asyncio.open_connection(
                    self.config['solarman']['host'],
                    self.config['solarman']['port']
                )
                logger.info(f"Connexion au cloud Solarman établie: {self.config['solarman']['host']}")
            except Exception as e:
                logger.warning(f"Impossible de se connecter au cloud Solarman: {e}")
        
        try:
            while self.running:
                # Lecture des données de l'onduleur
                data = await reader.read(1024)
                if not data:
                    break
                
                logger.debug(f"Données reçues de {client_addr}: {len(data)} bytes")
                
                # Parse des données
                parsed_data = self.parse_tsun_data(data)
                if parsed_data:
                    # Détermination du serial number (basique)
                    serial = f"R17{int(time.time()) % 1000000000000:012d}"  # Serial factice
                    
                    # Publication vers MQTT
                    if self.mqtt_client:
                        await self.publish_ha_discovery("Inverter", serial, parsed_data)
                        for key, value in parsed_data.items():
                            if key != 'timestamp':
                                await self.publish_sensor_data(serial, key, value)
                
                # Transfert vers le cloud si connecté
                if tsun_writer:
                    try:
                        tsun_writer.write(data)
                        await tsun_writer.drain()
                    except Exception as e:
                        logger.error(f"Erreur lors du transfert vers TSUN: {e}")
                
                if solarman_writer:
                    try:
                        solarman_writer.write(data)
                        await solarman_writer.drain()
                    except Exception as e:
                        logger.error(f"Erreur lors du transfert vers Solarman: {e}")
        
        except Exception as e:
            logger.error(f"Erreur lors de la gestion de la connexion: {e}")
        
        finally:
            writer.close()
            if tsun_writer:
                tsun_writer.close()
            if solarman_writer:
                solarman_writer.close()
            logger.info(f"Connexion fermée avec {client_addr}")
    
    async def start_server(self, port):
        """Démarre un serveur sur le port spécifié"""
        try:
            server = await asyncio.start_server(
                lambda r, w: self.handle_inverter_connection(r, w, port),
                '0.0.0.0',
                port
            )
            
            self.servers.append(server)
            logger.info(f"Serveur démarré sur port {port}")
            
            async with server:
                await server.serve_forever()
        
        except Exception as e:
            logger.error(f"Erreur lors du démarrage du serveur sur port {port}: {e}")
    
    async def start_web_ui(self):
        """Démarre l'interface web (basique)"""
        from aiohttp import web
        
        async def status_handler(request):
            status = {
                'proxy': 'running',
                'mqtt_connected': self.mqtt_client is not None,
                'servers': len(self.servers),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            return web.json_response(status)
        
        async def config_handler(request):
            # Masquer les mots de passe dans la réponse
            safe_config = dict(self.config)
            if 'mqtt' in safe_config and 'passwd' in safe_config['mqtt']:
                safe_config['mqtt']['passwd'] = '***'
            return web.json_response(safe_config)
        
        app = web.Application()
        app.router.add_get('/api/status', status_handler)
        app.router.add_get('/api/config', config_handler)
        
        try:
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', 8080)
            await site.start()
            logger.info("Interface web démarrée sur port 8080")
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de l'interface web: {e}")
    
    async def run(self):
        """Lance le proxy principal"""
        logger.info("Démarrage du TSUN Gen3 Proxy")
        self.running = True
        
        # Configuration MQTT
        mqtt_ready = await self.setup_mqtt()
        if mqtt_ready:
            # Connexion MQTT
            try:
                await self.mqtt_client.__aenter__()
                logger.info("Connexion MQTT établie")
            except Exception as e:
                logger.error(f"Erreur de connexion MQTT: {e}")
                self.mqtt_client = None
        
        # Création des tâches
        tasks = []
        
        # Serveurs TCP
        tasks.append(asyncio.create_task(self.start_server(5005)))  # GEN3
        tasks.append(asyncio.create_task(self.start_server(10000))) # GEN3PLUS
        
        # Interface web
        tasks.append(asyncio.create_task(self.start_web_ui()))
        
        try:
            # Attendre que toutes les tâches se terminent
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Arrêt demandé par l'utilisateur")
        except Exception as e:
            logger.error(f"Erreur durant l'exécution: {e}")
        finally:
            self.running = False
            # Nettoyage
            for server in self.servers:
                server.close()
                await server.wait_closed()
            
            if self.mqtt_client:
                try:
                    await self.mqtt_client.__aexit__(None, None, None)
                except:
                    pass
            
            logger.info("Proxy arrêté")


def signal_handler(signum, frame):
    """Gestionnaire de signal pour arrêt propre"""
    logger.info(f"Signal {signum} reçu, arrêt du proxy...")
    sys.exit(0)


def main():
    """Point d'entrée principal"""
    # Gestion des signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Configuration du niveau de log
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.getLogger().setLevel(getattr(logging, log_level, logging.INFO))
    
    # Démarrage du proxy
    proxy = TsunProxy()
    
    try:
        asyncio.run(proxy.run())
    except KeyboardInterrupt:
        logger.info("Arrêt par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
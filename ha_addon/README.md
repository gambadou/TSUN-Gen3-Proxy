# TSUN Gen3 Proxy Home Assistant Add-on

![Logo](logo.png)

Cet add-on vous permet d'intégrer facilement vos onduleurs et batteries TSUN de troisième génération dans Home Assistant via MQTT.

## À propos

Le TSUN Gen3 Proxy est un proxy qui permet une connexion fiable entre les onduleurs TSUN de troisième génération (ex. TSOL MS600, MS800, MS2000, MS3000), les batteries (TSOL DC1000) et un broker MQTT afin de les intégrer dans des systèmes domotiques typiques.

## Installation

1. Ajoutez le repository d'add-ons à votre Home Assistant :
   - Allez dans **Supervisor** → **Add-on Store**
   - Cliquez sur le menu (⋮) en haut à droite
   - Sélectionnez **Repositories**
   - Ajoutez cette URL : `https://github.com/votre-username/tsun-gen3-proxy-addon`

2. Trouvez l'add-on "TSUN Gen3 Proxy" et cliquez sur **Install**

3. Configurez l'add-on selon vos besoins

4. Démarrez l'add-on

## Configuration

### Options de base

| Option | Description | Défaut |
|--------|-------------|---------|
| `mqtt_host` | Adresse du broker MQTT | `core-mosquitto` |
| `mqtt_port` | Port du broker MQTT | `1883` |
| `mqtt_user` | Nom d'utilisateur MQTT (optionnel) | `""` |
| `mqtt_password` | Mot de passe MQTT (optionnel) | `""` |
| `tsun_cloud_enabled` | Activer la connexion au cloud TSUN | `true` |
| `log_level` | Niveau de log | `info` |

### Configuration des onduleurs

Pour chaque onduleur, vous devez ajouter une entrée dans la section `inverters` :

```yaml
inverters:
  - serial: "R17xxxxxxxxxxxx1"  # Numéro de série de l'onduleur
    node_id: "inv_1"             # ID unique pour MQTT
    suggested_area: "roof"       # Zone suggérée dans HA
    modbus_polling: false        # Polling MODBUS (GEN3)
    pv1_type: "RSM40-8-395M"     # Type de panneau PV1 (optionnel)
    pv1_manufacturer: "Risen"    # Fabricant PV1 (optionnel)
```

### Configuration des batteries

Pour les batteries GEN3PLUS :

```yaml
batteries:
  - serial: "4100000000000001"   # Numéro de série de la batterie
    monitor_sn: 3000000000       # SN de monitoring
    node_id: "bat_1"             # ID unique pour MQTT
    suggested_area: "garage"     # Zone suggérée dans HA
    modbus_polling: true         # Polling MODBUS recommandé
```

## Compatibilité

### Onduleurs GEN3 supportés
- MS300, MS350, MS400, MS600, MS700, MS800, MS3000
- Numéros de série commençant par `R17` ou `R47`

### Onduleurs GEN3PLUS supportés
- MS1600, MS1800, MS2000
- Numéros de série commençant par `Y17` ou `Y47`

### Batteries GEN3PLUS supportées
- TSOL DC1000
- Numéros de série commençant par `410`

## Configuration réseau requise

**Important :** Pour que le proxy fonctionne, vous devez rediriger le trafic DNS de vos onduleurs vers le proxy. Cela peut se faire de plusieurs façons :

### Méthode 1 : Pi-hole ou AdGuard
Ajoutez ces enregistrements DNS locaux :
- `logger.talent-monitoring.com` → Adresse IP de votre Home Assistant
- `iot.talent-monitoring.com` → Adresse IP de votre Home Assistant

### Méthode 2 : Configuration du routeur
Modifiez les enregistrements DNS dans votre routeur pour pointer vers votre Home Assistant.

### Méthode 3 : Règles de firewall
Utilisez des règles iptables pour rediriger le trafic.

## Ports utilisés

- **5005** : Connexion des onduleurs GEN3
- **10000** : Connexion des onduleurs GEN3PLUS et batteries
- **8080** : Interface web de statut

## Interface web

Une interface web simple est disponible sur le port 8080 pour vérifier le statut du proxy :
- `http://homeassistant.local:8080/api/status` : Statut du proxy
- `http://homeassistant.local:8080/api/config` : Configuration actuelle

## Intégration Home Assistant

L'add-on configure automatiquement la découverte MQTT dans Home Assistant. Vos onduleurs et batteries apparaîtront automatiquement comme nouveaux appareils avec leurs capteurs correspondants :

- Puissance instantanée (W)
- Énergie du jour (kWh)
- Énergie totale (kWh)
- Tension (V)
- Courant (A)
- Température (°C)

## Dépannage

### L'onduleur ne se connecte pas
1. Vérifiez la configuration DNS
2. Assurez-vous que les ports 5005 et 10000 sont ouverts
3. Vérifiez les logs de l'add-on

### Pas de données dans Home Assistant
1. Vérifiez que le broker MQTT fonctionne
2. Vérifiez la configuration MQTT de l'add-on
3. Regardez les logs pour les erreurs de connexion MQTT

### Problèmes de certificat SSL (GEN3PLUS)
Si votre onduleur utilise SSL (port 10443), utilisez le mode client :

```yaml
inverters:
  - serial: "Y17xxxxxxxxxxxx1"
    client_mode_host: "192.168.1.100"  # IP fixe de l'onduleur
    client_mode_port: 8899
```

## Support

Pour obtenir de l'aide :
1. Consultez les logs de l'add-on
2. Vérifiez la documentation du projet original : https://github.com/s-allius/tsun-gen3-proxy
3. Ouvrez une issue sur GitHub

## Licence

Cet add-on est basé sur le projet tsun-gen3-proxy de Stefan Allius, sous licence BSD-3-Clause.
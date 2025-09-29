# TSUN Gen3 Proxy - Add-on Home Assistant

![Logo TSUN](ha_addon/logo.png)

Cet add-on Home Assistant vous permet d'intégrer facilement vos onduleurs et batteries TSUN de troisième génération dans Home Assistant via MQTT.

## 🚀 Installation Rapide

### 1. Ajout du Repository

Ajoutez ce repository à votre Home Assistant :

[![Open your Home Assistant instance and show the add add-on repository dialog with the repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A//github.com/votre-username/tsun-gen3-proxy-addon)

Ou manuellement :
1. Accédez à **Supervisor** → **Add-on Store**
2. Cliquez sur ⋮ (menu) en haut à droite
3. Sélectionnez **Repositories**
4. Ajoutez : `https://github.com/votre-username/tsun-gen3-proxy-addon`

### 2. Installation de l'Add-on

1. Rafraîchissez la page Add-on Store
2. Trouvez "TSUN Gen3 Proxy" et cliquez sur **Install**
3. Attendez la fin de l'installation

### 3. Configuration Réseau **OBLIGATOIRE**

⚠️ **ÉTAPE CRITIQUE** : Vous devez rediriger le DNS de vos onduleurs vers votre Home Assistant.

#### Option A : Pi-hole (Recommandé)

Si vous utilisez Pi-hole :
1. Allez dans **Pi-hole Admin** → **Local DNS** → **DNS Records**
2. Ajoutez :
   - `logger.talent-monitoring.com` → `IP_DE_VOTRE_HOME_ASSISTANT`
   - `iot.talent-monitoring.com` → `IP_DE_VOTRE_HOME_ASSISTANT`

#### Option B : AdGuard Home

Si vous utilisez l'add-on AdGuard Home :
1. Allez dans **AdGuard Home** → **DNS rewrites**
2. Ajoutez les mêmes redirections que pour Pi-hole

#### Option C : Configuration Routeur

Dans votre routeur (interface varie selon le modèle) :
1. Trouvez la section DNS local/Host entries
2. Ajoutez les redirections vers votre Home Assistant

### 4. Configuration de l'Add-on

#### Configuration MQTT
```yaml
mqtt_host: "core-mosquitto"  # Ou l'adresse de votre broker MQTT
mqtt_port: 1883
mqtt_user: ""               # Optionnel
mqtt_password: ""           # Optionnel
```

#### Configuration des Onduleurs

**Pour un onduleur GEN3 :**
```yaml
inverters:
  - serial: "R17000000000001"        # Votre numéro de série réel
    node_id: "inv_salon"             # ID unique pour MQTT
    suggested_area: "salon"          # Zone dans Home Assistant
    modbus_polling: false            # Recommandé false pour GEN3
    pv1_type: "Votre-Panel-Type"     # Optionnel
    pv1_manufacturer: "Fabricant"    # Optionnel
```

**Pour un onduleur GEN3PLUS :**
```yaml
inverters:
  - serial: "Y17000000000001"        # Numéro de série Y17/Y47
    monitor_sn: 2000000000           # SN de monitoring (étiquette)
    node_id: "inv_garage"            # ID unique
    suggested_area: "garage"
    modbus_polling: true             # Recommandé true pour GEN3PLUS
```

**Pour une batterie GEN3PLUS :**
```yaml
batteries:
  - serial: "4100000000000001"       # Numéro de série 410*
    monitor_sn: 3000000000           # SN de monitoring
    node_id: "battery_garage"
    suggested_area: "garage"
    modbus_polling: true
```

### 5. Démarrage

1. Sauvegardez votre configuration
2. Démarrez l'add-on
3. Activez "Start on boot" pour un démarrage automatique
4. Vérifiez les logs pour s'assurer que tout fonctionne

## 🔧 Vérification du Fonctionnement

### Interface Web

Accédez à : `http://homeassistant.local:8080/api/status`

Vous devriez voir :
```json
{
  "proxy": "running",
  "mqtt_connected": true,
  "servers": 2,
  "timestamp": "2025-01-01T12:00:00+00:00"
}
```

### Home Assistant

1. Allez dans **Paramètres** → **Appareils et services** → **MQTT**
2. Vous devriez voir apparaître automatiquement vos appareils TSUN
3. Les capteurs incluent :
   - Puissance instantanée (W)
   - Énergie du jour (kWh)
   - Énergie totale (kWh)
   - Tension (V)
   - Courant (A)
   - Température (°C)

## 🔍 Identification des Modèles

### Comment trouver votre numéro de série ?

#### GEN3 (R17/R47)
- Regardez l'étiquette sur l'onduleur
- Commence par `R17` ou `R47`
- Exemple : `R17012345678901`

#### GEN3PLUS (Y17/Y47/410)
- **Onduleurs** : Série commence par `Y17` ou `Y47`
- **Batteries** : Série commence par `410`
- **Monitoring SN** : Numéro sur l'étiquette jointe (ex: 2000000000)

### Modèles Supportés

| Type | Modèles | Série |
|------|---------|-------|
| **GEN3** | MS300, MS350, MS400, MS600, MS700, MS800, MS3000 | R17*, R47* |
| **GEN3PLUS** | MS1600, MS1800, MS2000 | Y17*, Y47* |
| **Batteries** | TSOL DC1000 | 410* |

## 🛠️ Dépannage

### L'onduleur ne se connecte pas

1. **Vérifiez la redirection DNS** :
   ```bash
   # Testez depuis votre réseau
   nslookup logger.talent-monitoring.com
   # Doit retourner l'IP de votre Home Assistant
   ```

2. **Vérifiez les logs de l'add-on** :
   - Cherchez des messages de connexion
   - Vérifiez les erreurs de réseau

3. **Vérifiez les ports** :
   - Port 5005 ouvert pour GEN3
   - Port 10000 ouvert pour GEN3PLUS

### Pas de données MQTT

1. **Broker MQTT** :
   - Vérifiez que Mosquitto Broker est démarré
   - Testez la connexion MQTT

2. **Configuration** :
   - Vérifiez les identifiants MQTT
   - Regardez les logs pour les erreurs de connexion

3. **Topics MQTT** :
   - Utilisez MQTT Explorer pour voir les topics `tsun/`

### Problèmes SSL (GEN3PLUS)

Si votre onduleur utilise le port 10443 (SSL) :

```yaml
inverters:
  - serial: "Y17000000000001"
    monitor_sn: 2000000000
    client_mode_host: "192.168.1.100"  # IP FIXE de l'onduleur
    client_mode_port: 8899
    # NE PAS changer l'URL dans l'onduleur !
```

### Messages d'erreur courants

#### "Configuration DNS requise"
- Vous n'avez pas configuré la redirection DNS
- Suivez la section "Configuration Réseau"

#### "MQTT connection failed"
- Vérifiez que le broker MQTT fonctionne
- Vérifiez les identifiants dans la configuration

#### "No data received from inverter"
- L'onduleur n'arrive pas à joindre le proxy
- Problème de redirection DNS
- Firewall bloquant les connexions

## 📋 Configuration Complète Exemple

```yaml
# Configuration MQTT
mqtt_host: "core-mosquitto"
mqtt_port: 1883
mqtt_user: ""
mqtt_password: ""

# Options cloud
tsun_cloud_enabled: true         # Garde la connexion au cloud TSUN
solarman_cloud_enabled: true     # Garde la connexion Solarman

# Niveau de log
log_level: "info"                # debug, info, warning, error

# Onduleurs
inverters:
  # GEN3 - Onduleur salon
  - serial: "R17012345678901"
    node_id: "inv_salon"
    suggested_area: "salon"
    modbus_polling: false
    pv1_type: "Longi-LR5-72HPH-540M"
    pv1_manufacturer: "Longi"
    pv2_type: "Longi-LR5-72HPH-540M" 
    pv2_manufacturer: "Longi"
    
  # GEN3PLUS - Onduleur garage
  - serial: "Y17987654321098"
    monitor_sn: 2000000001
    node_id: "inv_garage"
    suggested_area: "garage"
    modbus_polling: true
    pv1_type: "JA-Solar-JAM72S30-540/MR"
    pv1_manufacturer: "JA Solar"

# Batteries
batteries:
  - serial: "4100000000000001"
    monitor_sn: 3000000001
    node_id: "battery_garage"
    suggested_area: "garage"
    modbus_polling: true
```

## 🔗 Liens Utiles

- **Documentation complète** : [GitHub tsun-gen3-proxy](https://github.com/s-allius/tsun-gen3-proxy)
- **Documentation HA** : [s-allius.github.io](https://s-allius.github.io/tsun-gen3-proxy/)
- **Community Home Assistant** : [Forum TSUN](https://community.home-assistant.io/t/tsun-proxy-now-as-add-on/870131)

## ⚖️ Licence

Cet add-on est basé sur le travail de Stefan Allius sous licence BSD-3-Clause.

---

**Support** : Pour obtenir de l'aide, consultez les issues sur GitHub ou le forum Home Assistant.
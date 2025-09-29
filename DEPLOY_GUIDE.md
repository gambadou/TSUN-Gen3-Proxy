# Instructions de Déploiement - TSUN Gen3 Proxy Add-on

## 📋 Résumé

Vous avez maintenant un add-on Home Assistant complet pour intégrer les onduleurs TSUN !

## 📁 Structure Créée

```
/app/
├── ha_addon/                    # 📦 Add-on Home Assistant complet
│   ├── config.yaml              # ⚙️  Configuration de l'add-on
│   ├── build.yaml               # 🏗️  Instructions de build
│   ├── Dockerfile               # 🐳 Image Docker
│   ├── requirements.txt         # 📚 Dépendances Python
│   ├── generate_config.py       # 🛠️  Générateur de configuration
│   ├── README.md               # 📖 Documentation
│   ├── DOCS.md                 # 📄 Documentation courte
│   ├── CHANGELOG.md            # 📝 Historique versions
│   ├── app/                    # 🐍 Code Python principal
│   │   └── proxy.py            # 🚀 Proxy TSUN principal
│   ├── rootfs/                 # 🏠 Système de fichiers add-on
│   │   └── etc/services.d/tsun-proxy/run  # 🎯 Script de démarrage
│   ├── translations/           # 🌍 Traductions
│   │   ├── en.json            # 🇺🇸 Anglais
│   │   └── fr.json            # 🇫🇷 Français
│   └── data/                   # 🔧 Configuration test
│       └── options.json        # 📋 Exemple configuration
├── INSTALLATION_FR.md           # 📖 Guide installation complet
├── README_ADDON.md             # 📄 README repository
├── repository.yaml             # 🏷️  Métadonnées repository
└── test_addon.sh              # 🧪 Script de test
```

## 🚀 Étapes de Déploiement

### 1. Création du Repository GitHub

```bash
# Sur votre machine locale
git init
git add .
git commit -m "Initial commit - TSUN Gen3 Proxy Add-on"
git branch -M main
git remote add origin https://github.com/VOTRE-USERNAME/tsun-gen3-proxy-addon.git
git push -u origin main
```

### 2. Personnalisation

**Modifiez ces fichiers avec vos informations :**

- `README_ADDON.md` : Remplacez `votre-username` par votre nom GitHub
- `repository.yaml` : Ajoutez vos informations de contact
- `ha_addon/config.yaml` : Modifiez l'image Docker si nécessaire

### 3. Test Local (Optionnel)

```bash
# Test de build Docker
cd ha_addon
docker build -t tsun-proxy-test .

# Test de fonctionnement
docker run -p 8080:8080 -p 5005:5005 -p 10000:10000 tsun-proxy-test
```

### 4. Installation dans Home Assistant

#### Méthode 1 : Lien Direct

[![Open your Home Assistant instance](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A//github.com/VOTRE-USERNAME/tsun-gen3-proxy-addon)

#### Méthode 2 : Manuelle

1. **Home Assistant** → **Supervisor** → **Add-on Store**
2. Menu (⋮) → **Repositories**
3. Ajouter : `https://github.com/VOTRE-USERNAME/tsun-gen3-proxy-addon`
4. Chercher "TSUN Gen3 Proxy" → **Install**

## ⚙️ Configuration Requise

### Configuration DNS (OBLIGATOIRE)

**Vous DEVEZ rediriger ces domaines vers votre Home Assistant :**

```bash
# Pour GEN3
logger.talent-monitoring.com → IP_HOME_ASSISTANT

# Pour GEN3PLUS  
iot.talent-monitoring.com → IP_HOME_ASSISTANT
```

**Comment faire :**

1. **Pi-hole** : DNS Records → Local DNS
2. **AdGuard** : DNS rewrites
3. **Routeur** : Host entries / DNS local
4. **OPNsense/pfSense** : Host overrides

### Broker MQTT

Installez l'add-on **Mosquitto broker** si pas déjà fait.

## 🔧 Configuration de l'Add-on

### Configuration Basique

```yaml
mqtt_host: "core-mosquitto"
mqtt_port: 1883
mqtt_user: ""
mqtt_password: ""
tsun_cloud_enabled: true
log_level: "info"
```

### Ajout d'un Onduleur GEN3

```yaml
inverters:
  - serial: "R17012345678901"    # Votre série réelle
    node_id: "inv_toiture"
    suggested_area: "salon"
    modbus_polling: false
    pv1_type: "Longi-540W"
    pv1_manufacturer: "Longi"
```

### Ajout d'un Onduleur GEN3PLUS

```yaml
inverters:
  - serial: "Y17987654321098"    # Votre série Y17/Y47
    monitor_sn: 2000000001       # Sur étiquette fournie
    node_id: "inv_garage"
    suggested_area: "garage"
    modbus_polling: true
```

### Ajout d'une Batterie

```yaml
batteries:
  - serial: "4100000000000001"   # Série commence par 410
    monitor_sn: 3000000001
    node_id: "battery_main"
    suggested_area: "garage"
    modbus_polling: true
```

## 🐛 Dépannage

### Problèmes Courants

#### 1. "Onduleur ne se connecte pas"
```bash
# Test DNS
nslookup logger.talent-monitoring.com
# Doit retourner l'IP de votre HA
```

#### 2. "Pas de données MQTT"
- Vérifiez Mosquitto Broker
- Vérifiez les logs de l'add-on
- Testez avec MQTT Explorer

#### 3. "SSL Certificate Error" (GEN3PLUS)
Utilisez le mode client :
```yaml
client_mode_host: "192.168.1.100"  # IP fixe onduleur
client_mode_port: 8899
```

### Vérification du Statut

```bash
# API de statut
curl http://homeassistant.local:8080/api/status

# Logs de l'add-on
# Dans HA : Supervisor → TSUN Gen3 Proxy → Logs
```

## 📊 Capteurs Home Assistant Créés

Pour chaque onduleur/batterie :

- `sensor.tsun_[node_id]_power` - Puissance instantanée (W)
- `sensor.tsun_[node_id]_energy_today` - Énergie du jour (kWh) 
- `sensor.tsun_[node_id]_energy_total` - Énergie totale (kWh)
- `sensor.tsun_[node_id]_voltage` - Tension (V)
- `sensor.tsun_[node_id]_current` - Courant (A)
- `sensor.tsun_[node_id]_temperature` - Température (°C)

## 🎯 Fonctionnalités

✅ **Support GEN3** (R17/R47) - MS300, MS400, MS600, MS800, MS3000  
✅ **Support GEN3PLUS** (Y17/Y47) - MS1600, MS1800, MS2000  
✅ **Support Batteries** (410) - TSOL DC1000  
✅ **Multi-onduleurs** - Plusieurs onduleurs simultanés  
✅ **MQTT Auto-discovery** - Apparition automatique dans HA  
✅ **Connexion cloud optionnelle** - Garde les fonctions Tsun App  
✅ **Interface web** - Monitoring sur port 8080  
✅ **Mode client SSL** - Support onduleurs récents  
✅ **Configuration via UI** - Pas de fichier TOML manuel  

## 🔗 Ressources

- **Projet original** : [s-allius/tsun-gen3-proxy](https://github.com/s-allius/tsun-gen3-proxy)
- **Documentation** : [s-allius.github.io](https://s-allius.github.io/tsun-gen3-proxy/)
- **Forum HA** : [Community Thread](https://community.home-assistant.io/t/tsun-proxy-now-as-add-on/870131)

## ✅ Validation

Votre add-on est prêt ! Les tests automatiques ont validé :

- ✅ Structure des fichiers  
- ✅ Syntaxe Python  
- ✅ Génération de configuration  
- ✅ Dépendances  
- ✅ Configuration YAML  

**Prochaine étape** : Créez votre repository GitHub et testez l'installation !

---

*Basé sur le fantastique travail de Stefan Allius - tsun-gen3-proxy*
# Installation

Cet add-on permet d'intégrer vos onduleurs et batteries TSUN dans Home Assistant.

## Avant de commencer

⚠️ **Configuration réseau requise** : Vous devez rediriger le DNS de vos onduleurs vers votre Home Assistant :

### Avec Pi-hole ou AdGuard :
- Ajoutez : `logger.talent-monitoring.com` → IP de votre Home Assistant
- Ajoutez : `iot.talent-monitoring.com` → IP de votre Home Assistant  

### Avec votre routeur :
Modifiez les enregistrements DNS dans votre routeur.

## Configuration

1. **MQTT** : Configurez votre broker MQTT (généralement `core-mosquitto`)
2. **Onduleurs** : Ajoutez vos onduleurs avec leurs numéros de série
3. **Batteries** : Ajoutez vos batteries si applicable

## Numéros de série
- **GEN3** : Commencent par `R17` ou `R47`
- **GEN3PLUS** : Commencent par `Y17`, `Y47` ou `410`

## Ports utilisés
- **5005** : Onduleurs GEN3
- **10000** : Onduleurs/batteries GEN3PLUS  
- **8080** : Interface web
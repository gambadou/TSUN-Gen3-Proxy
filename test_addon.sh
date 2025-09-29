#!/bin/bash
# Script de test pour l'add-on TSUN Gen3 Proxy

echo "🧪 Test de l'add-on TSUN Gen3 Proxy"
echo "=================================="

cd /app/ha_addon

echo "✅ Test 1: Vérification de la structure des fichiers..."
required_files=(
    "config.yaml"
    "build.yaml" 
    "Dockerfile"
    "requirements.txt"
    "README.md"
    "DOCS.md"
    "CHANGELOG.md"
    "app/proxy.py"
    "generate_config.py"
    "rootfs/etc/services.d/tsun-proxy/run"
    "translations/en.json"
    "translations/fr.json"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file MANQUANT"
        exit 1
    fi
done

echo ""
echo "✅ Test 2: Validation de la syntaxe Python..."
python3 -m py_compile app/proxy.py
python3 -m py_compile generate_config.py

echo "✅ Test 3: Test de génération de configuration..."
mkdir -p /tmp/test-config /tmp/test-data
echo '{"mqtt_host": "test-mqtt", "mqtt_port": 1883, "inverters": [], "batteries": []}' > /tmp/test-data/options.json

# Modifier temporairement le chemin de données pour les tests
sed -i 's|/data/options.json|/tmp/test-data/options.json|g' /app/ha_addon/generate_config.py
sed -i 's|/config/tsun-proxy/config.toml|/tmp/test-config/config.toml|g' /app/ha_addon/generate_config.py

cd /app/ha_addon && python3 generate_config.py

# Restaurer les chemins originaux
sed -i 's|/tmp/test-data/options.json|/data/options.json|g' /app/ha_addon/generate_config.py  
sed -i 's|/tmp/test-config/config.toml|/config/tsun-proxy/config.toml|g' /app/ha_addon/generate_config.py

if [ -f "/tmp/test-config/config.toml" ]; then
    echo "  ✅ Configuration générée avec succès"
    head -5 /tmp/test-config/config.toml
else
    echo "  ❌ Erreur génération configuration"
    exit 1
fi

echo ""
echo "✅ Test 4: Vérification des dépendances..."
cd /app/ha_addon
pip3 install -r requirements.txt >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ Toutes les dépendances sont installables"
else
    echo "  ❌ Erreur dans les dépendances"
    exit 1
fi

echo ""
echo "✅ Test 5: Vérification de la configuration YAML..."
python3 -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print(f'  ✅ Add-on: {config[\"name\"]} v{config[\"version\"]}')
    print(f'  ✅ Architectures: {config[\"arch\"]}')
    print(f'  ✅ Ports: {config[\"ports\"]}')
"

echo ""
echo "🎉 Tous les tests sont passés avec succès!"
echo ""
echo "📝 Prochaines étapes:"
echo "1. Modifiez les URLs dans README_ADDON.md avec votre repository GitHub"
echo "2. Ajustez le fichier repository.yaml avec vos informations" 
echo "3. Créez un repository GitHub et uploadez les fichiers"
echo "4. Ajoutez le repository dans Home Assistant"
echo "5. Testez l'installation de l'add-on"
echo ""
echo "🔧 Pour tester localement:"
echo "   docker build -t tsun-proxy-addon ./ha_addon"
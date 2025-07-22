#!/bin/bash

echo "🔧 Labyrinth Game Service Installation"
echo "======================================"

# Mache das Start-Script ausführbar
chmod +x start_delayed.sh
echo "✅ Start-Script ausführbar gemacht"

# Kopiere den Service in systemd Verzeichnis
sudo cp labyrinth-game.service /etc/systemd/system/
echo "✅ Service-Datei kopiert"

# Lade systemd neu
sudo systemctl daemon-reload
echo "✅ Systemd neu geladen"

# Aktiviere den Service
sudo systemctl enable labyrinth-game.service
echo "✅ Service aktiviert"

# Starte den Service
sudo systemctl start labyrinth-game.service
echo "✅ Service gestartet"

echo ""
echo "🎮 Labyrinth Game Service ist installiert!"
echo "📋 Status prüfen mit: sudo systemctl status labyrinth-game.service"
echo "📋 Logs anzeigen mit: sudo journalctl -u labyrinth-game.service -f"
echo "🛑 Service stoppen mit: sudo systemctl stop labyrinth-game.service"
echo "▶️  Service starten mit: sudo systemctl start labyrinth-game.service" 
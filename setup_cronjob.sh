#!/bin/bash

echo "⏰ Cronjob Setup für Labyrinth Game"
echo "==================================="

# Mache das Start-Script ausführbar
chmod +x start_delayed.sh
echo "✅ Start-Script ausführbar gemacht"

# Füge Cronjob hinzu
(crontab -l 2>/dev/null; echo "@reboot /home/pi/Labyrinth-Game-main/start_delayed.sh") | crontab -
echo "✅ Cronjob hinzugefügt"

echo ""
echo "🎮 Cronjob ist eingerichtet!"
echo "📋 Cronjobs anzeigen mit: crontab -l"
echo "🛑 Cronjob entfernen mit: crontab -r"
echo "🔄 System neu starten zum Testen" 
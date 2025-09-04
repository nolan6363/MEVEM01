MEVEM - Mesure de la verse du maïs
=====================================
Centre de recherche de Chappes (CRC) Limagrain

Instructions d'installation Linux:
1. Assurez-vous d'avoir les permissions pour accéder aux ports série
   sudo usermod -a -G dialout $USER
   (puis redémarrez votre session)

Instructions d'utilisation:
1. Connectez votre capteur USB série
2. Lancez ./mevem ou ./start_mevem.sh
3. L'interface web s'ouvrira automatiquement dans votre navigateur
4. Suivez les instructions à l'écran pour calibrer puis mesurer

Résolution de problèmes:
- Si l'interface ne s'ouvre pas, allez sur http://127.0.0.1:5000
- Vérifiez les permissions série: ls -l /dev/ttyUSB*
- Utilisez make check-permissions pour diagnostiquer les problèmes
- Assurez-vous que votre capteur est reconnu: dmesg | grep tty

Fonctionnalités:
- Moyennage configurable (1-100 valeurs)
- Export Excel personnalisé
- Calibration interactive
- Interface temps réel

Version: $(date +%Y-%m-%d)

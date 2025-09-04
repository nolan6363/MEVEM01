MEVEM - Mesure de la verse du maïs
=====================================

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
- Assurez-vous que votre capteur est reconnu: dmesg | grep tty

Support: https://github.com/votre-repo/mevem

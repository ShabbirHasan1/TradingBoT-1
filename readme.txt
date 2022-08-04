https://cloudstrata.io/install-ta-lib-on-ubuntu-server/
============================
- clean logs
- dates config
- refresh token
- check test mod on
- open crons
- crontab -e
- service cron restart
============================
*/1 15 * * 1-5  cd ~/Web/TradingBoT/ && python3 windup.py  > logs/windup/`date +\%H:\%M`.log 2>&1
*/1 10,11,12,13,14 * * 1-5  cd ~/Web/TradingBoT/ && python3 cleaner.py  > logs/cleaner/`date +\%H:\%M`.log 2>&1
*/2 10,11,12,13,14 * * 1-5  cd ~/Web/TradingBoT/ && python3 scanner.py  > logs/scanner/`date +\%H:\%M`.log 2>&1
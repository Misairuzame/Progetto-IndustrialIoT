# Progetto Industrial Internet of Things

## Prerequisiti per far funzionare il progetto:

Programmi che vanno installati:
  - python3
  - Mosquitto
  - Filebeat
  - Apache Kafka
  - Logstash
  - Elasticsearch
  - Kibana

Il file di configurazione di Filebeat si può trovare nella cartella `config-files`,
e va copiato in /etc/filebeat/filebeat.yml. I file di configurazione per gli altri
programmi non sono stati inseriti, in quanto si è mantenuta la configurazione predefinita.
Il file contenente la specifica della pipeline di Logstash è `logstash-config.cfg`.

### Dipendenze python3 (pip3)
  - paho-mqtt (Client MQTT)
  - matplotlib (Per i grafici)
  - numpy (Per i grafici)
  - shapely (Per generare coordinate casuali all'interno di uno stato)
  - requests (Per contattare facilmente Elasticsearch e l'API per il meteo)

## Far partire il progetto
1. Se la si vuole cambiare, impostare la durata di una giornata simulata nel file `time_scaling.py`
(spiegazione all'interno di quel file)
2. Far partire Filebeat, Kafka, Logstash, Elasticsearch e Kibana `sh start-everything.sh`
3. Creare i topic su Kafka: `/usr/local/kafka/bin/kafka-topics.sh --create --topic telemetry --bootstrap-server localhost:9092`
`/usr/local/kafka/bin/kafka-topics.sh --create --topic clientinfo --bootstrap-server localhost:9092`
4. Creare gli indici su Elasticsearch: `sh create_indexes.sh`
5. Creare gli index pattern `telemetry`, `clientinfo` ed `elaboration` su Kibana (Menu > Stack Management > Index Patterns)
6. Importare la dashboard su Kibana: https://www.elastic.co/guide/en/kibana/current/dashboard-import-api.html (Il file contenente il json
che descrive la dashboard è `kibana-dashboard.txt`)
7. Far partire una o più case da simulare:
   - Se si vuole generare solamente una casa, `sh house.sh [porta-mosquitto]`
   - Se si vogliono generare più case, `bash many-houses.sh [porta-mosquitto]`, poi si può riutilizzare lo stesso comando
   incrementando la porta almeno di 10 (Ogni casa ha il suo broker Mosquitto, in questa simulazione i broker devono girare su
   porte diverse per evitare conflitti)
8. Se si vogliono generare le bollette per gli utenti, eseguire il file `elaboration.py`, il quale crea subito una bolletta, poi ne continua a produrre periodicamente al passaggio di una settimana simulata (Se la variabile `time_scale` del file `time_scaling.py` è 300, `elaboration.py` creerà una bolletta ogni 300*7 secondi, ossia ogni 35 minuti)
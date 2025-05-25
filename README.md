# Progetto Industrial Internet of Things
Questo progetto, originariamente creato per l'esame di Industrial Internet of Things, simula un sistema per il monitoraggio energetico di abitazioni, includendo componenti IoT, analisi dati e visualizzazione tramite ELK stack. Il sistema si compone di vari moduli containerizzati che interagiscono attraverso MQTT, Kafka ed Elasticsearch.

## Struttura del progetto
```
├── altro/              # Script ausiliari e strumenti di test/simulazione
├── elaboration/        # Elaborazione dati per generazione bollette
├── elastic/            # Container Elasticsearch con configurazioni
├── house/              # Simulazione casa e suoi componenti
├── kibana/             # Container Kibana e dashboard
├── logstash/           # Configurazione per Logstash
├── .env                # Variabili d'ambiente
├── docker-compose.yml  # Definizione dei servizi Docker
└── README.md           # Documentazione del progetto
```

### Simulazione delle case
Spiegazione dei componenti e del funzionamento delle case...

# Leer je Sensor Data Platform begrijpen

**Doel:** uitleggen hoe sensoren geregistreerd worden, metingen veranderen in
analyseerbare rijen en kwaliteit zichtbaar wordt. Je leert ook onderscheid maken
tussen de verschillende routes die in deze repo bestaan.

Afgestemd op code op 11 oktober 2026. Er is bij het schrijven geen live tenant
of productieomgeving opnieuw getest.

## Je route

1. [Codewandeling: asset, meting, opslag en rapport](codewandeling.md).
2. [Begrippen: data engineering en BI in gewone taal](begrippen.md).
3. [Oefeningen met antwoorden](oefeningen.md).
4. [Herhaalkaarten, leerplan en AI als begeleider](onthouden.md).
5. [Eigen leerlogboek](leerlogboek.md).

## De belangrijkste afbakening

De repo bevat code voor ThingsBoard-integratie, PostgreSQL-ingestie, analytics,
een API, rapporten en een dashboard. Dat betekent niet dat ieder scherm automatisch
van ThingsBoard via PostgreSQL wordt gevoed. De lokale rapport-, dashboard- en
API-route lezen hier gegenereerde CSV's. De database- en ThingsBoard-routes zijn
aparte codepaden. De README bevat eerder vastgelegde cloudvoorbeelden; die zijn
geen actuele beschikbaarheidscontrole.

## Vaardighedenkaart

| Vaardigheid | Concreet bestand | Zelf kunnen aantonen |
|---|---|---|
| Python en transformaties | [processor.py](../../src/sensor_platform/ingestion/processor.py) | Wide naar long met drie rijen uitleggen |
| ETL/database | [pipeline.py](../../src/sensor_platform/ingestion/pipeline.py) | Verklaar sleutel en herhaalde ingestie |
| Modellen | [schema.py](../../src/sensor_platform/db/schema.py) | Formuleer de grain van een meting |
| CSV-inname | [csv_importer.py](../../src/sensor_platform/imports/csv_importer.py) | Leg chunks, dubbele ID's en importuitkomsten uit |
| Integraties | [client.py](../../src/sensor_platform/integrations/thingsboard/client.py) | Onderscheid tijdelijke fout en autorisatiefout |
| Idempotentie | [devices.py](../../src/sensor_platform/integrations/thingsboard/devices.py) | Verklaar created, updated en unchanged |
| Datakwaliteit | [quality.py](../../src/sensor_platform/analytics/quality.py) | Controleer wat de KPI daadwerkelijk meet |
| Statistiek | [aggregation.py](../../src/sensor_platform/analytics/aggregation.py) | Leg groepering per sensor, metriek en uur uit |
| Rapportering | [reports.py](../../src/sensor_platform/reporting/reports.py) | Traceer een samenvatting naar de bron |
| API en caching | [api/data.py](../../src/sensor_platform/api/data.py) | Leg hergebruik en verversing uit |
| Testen | [tests](../../tests) | Onderscheid mocks en echte integratietests |
| Performance | Chunking en database-write | Benoem wat wel en niet in batches gebeurt |
| Governance | Projecttoegang, metadata en betekenis van metingen | Maak een expliciete afspraak en test die |
| Power BI/Fabric | Niet geïmplementeerd in deze repo | Andere praktische oefening nodig |

## Andere projecten

- [Mobility ETL](https://github.com/phlppgdfry/belgium-mobility-weather-etl/tree/main/docs/leren)
- [Sales Analytics](https://github.com/phlppgdfry/python-data-analytics-project/tree/main/docs/leren)
- [Fabric Lottery](https://github.com/phlppgdfry/fabric-lottery-data-platform/tree/main/docs/leren)

[Terug naar de project-README](../../README.md)

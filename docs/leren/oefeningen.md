# Sensorplatform: praktische oefeningen

[Leerroute](README.md) · [Codewandeling](codewandeling.md)

Begin zonder AI-antwoord. Gebruik synthetische gegevens; provisioning naar een
live tenant is niet nodig voor deze begripsopdrachten. Voor lokale uitvoering
volg je de [README](../../README.md).

## 1. Tel de juiste dingen

Je hebt twee sensoren, ieder op drie tijdstippen gemeten, met temperatuur en
vochtigheid op ieder moment. Er ontbreekt niets. Hoeveel brede rijen en hoeveel
long-meetrijen verwacht je?

<details><summary>Antwoord</summary>

**6 brede rijen**, **12 long-meetrijen**, **2 sensoren** en **3 gezamenlijke
tijdstippen**. De telling hangt af van wat je telt. “12 readings” betekent geen
12 apparaten. Bij een ontbrekende metriek vervalt die long-waarde in deze code.

</details>

## 2. Exact dubbel versus conflict

Rij A: S1, 08:00, temperatuur 20. Rij B is exact gelijk. Rij C: S1, 08:00,
temperatuur 21. Hoeveel rijen blijven na de huidige brede deduplicatie over?
Waarom kan database-opslag een ander resultaatbeeld geven?

<details><summary>Antwoord</summary>

**Twee**: A of B plus C. De deduplicatie vergelijkt alle waarden; 20 en 21
verschillen. De database-ID gebruikt sensor, tijd en metriek, zodat beide waarden
dezelfde meetsleutel krijgen. De huidige write kan een eerdere waarde bijwerken;
directe CSV-analyse kan beide meetrijen behouden. Een conflictregel ontbreekt
als expliciete, eenduidige regel over alle routes.

</details>

## 3. Ontmasker een verkeerd KPI-label

Er worden 200 metingen verwacht. Er komen 100 binnen, waarvan 10 buiten bereik.
Wat geeft de huidige `completeness_pct`? Wat is de ontvangstvolledigheid?

<details><summary>Antwoord</summary>

De code geeft **90%**: 100 × (1 − 10/100). Ontvangstvolledigheid is **50%**:
100 ontvangen / 200 verwacht. Als je “bruikbare ontvangen waarden tegenover
verwacht” wilt meten, is dat 90/200 = 45%. Dit zijn drie verschillende KPI's.
De business moet bepalen welke vraag elk getal beantwoordt.

</details>

## 4. Offline zonder lage uptime?

Een sensor levert elke 15 minuten tussen 08:00 en 09:00, en daarna niets tot
het einde van de afgesproken meetdag. Waarom kan de huidige uptime-inschatting
toch hoog zijn?

<details><summary>Antwoord</summary>

De berekening gebruikt de eerste en laatste **ontvangen** tijd, niet het volledige
afgesproken venster. De uren na 09:00 vallen buiten de noemer. Ontwerp een KPI
met expliciet begin/einde, verwachte intervallen en afspraken over inclusieve
eindpunten, onderhoud en nog niet geïnstalleerde sensoren.

</details>

## 5. SQL voor een uuroverzicht

Welke groepering voorkomt dat temperatuur en vochtigheid door elkaar worden
gemiddeld? Leg onderstaande PostgreSQL-query uit.

```sql
SELECT sensor_id, metric, DATE_TRUNC('hour', timestamp) AS hour,
       AVG(value) AS mean_value, COUNT(*) AS readings
FROM telemetry
GROUP BY sensor_id, metric, DATE_TRUNC('hour', timestamp);
```

<details><summary>Antwoord</summary>

De combinatie sensor + metriek + uur vormt een groep. `metric` is noodzakelijk:
graden Celsius en procenten samen middelen heeft geen zin. Controleer ook
meeteenheden binnen een metriek en de tijdzone waarmee het uur wordt afgebakend.
Deze query is een leervoorbeeld; het lokale dashboard gebruikt zijn Python-route.

</details>

## 6. Wordt de hele import in chunks verwerkt?

Een collega zegt: “Onze import gebruikt chunks van 5.000, dus elk onderdeel kan
zonder extra geheugen miljoenen meetwaarden verwerken.” Wat klopt daar niet aan?

<details><summary>Antwoord</summary>

Chunking zit in de assetimport. De telemetrie-ingestie leest een CSV in en maakt
een lijst records voor schrijven. Ook groeit de asset-set van geziene ID's.
Meet geheugengebruik en runtime van ieder apart pad voordat je een schaalclaim doet.

</details>

## 7. Een kleine kwaliteitswijziging

Ontwerp op papier een apart veld `received_completeness_pct` met een expliciet
verwacht aantal. Welke uitkomsten verwacht je bij 90/100, 0/100 en 0/0?

<details><summary>Mogelijk ontwerp</summary>

90/100 = **90%**, 0/100 = **0%**. Bij 0/0 is de ratio ongedefinieerd: toon
bijvoorbeeld “niet van toepassing” met reden, geen schijnzekere 100%.
Leg die keuze vast. Een test moet juist ook de lege gevallen afdekken.
Dit ontwerp is nog geen wijziging aan de bestaande implementatie.

</details>

## 8. Nieuw bestand, oude API-response

Je vervangt de gegenereerde telemetrie-CSV op hetzelfde pad. De API geeft nog
het oude resultaat. Welk bestand inspecteer je? Is de database hierbij de eerste verdachte?

<details><summary>Antwoord</summary>

`src/sensor_platform/api/data.py`: de gecachte functie gebruikt paden als sleutel.
Bestandsinhoud wijzigen verandert die sleutel niet. Onderzoek cacheverversing
en de werkelijk gekozen bron. De bestaande API-route leest CSV; beginnen met
database-debugging zou hier de verkeerde datastroom volgen.

</details>

## 9. Leg een afwijking uit

De grafiek toont een grote piek. Geef drie mogelijke oorzaken en één manier om
iedere oorzaak te onderzoeken.

<details><summary>Voorbeeldantwoord</summary>

- Echte gebeurtenis: vergelijk nabijgelegen sensoren en tijdstippen.
- Sensorfout: controleer kalibratie, onderhoud en ruwe apparaatmetingen.
- Verwerkingsfout: controleer eenheid, dubbele meetsleutels en aggregatie.

Een anomalievlag bepaalt niet automatisch welke oorzaak waar is.

</details>

## Eindproef

Teken de afzonderlijke routes. Leg één long-meetrij uit, voorspel een dubbele
invoer en verbeter op papier één KPI-definitie. Noteer wat je zelf kon en waar
je hulp bij nodig had in je [leerlogboek](leerlogboek.md).

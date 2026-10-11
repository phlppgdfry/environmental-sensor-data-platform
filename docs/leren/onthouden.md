# Leren, onthouden en AI verstandig gebruiken

[Terug naar de leerroute](README.md)

## Je dagelijkse sessie: 30 tot 45 minuten

1. **5 minuten ophalen:** sluit de uitleg en teken de datastroom uit je hoofd.
2. **10 minuten lezen:** volg één functie en schrijf invoer, bewerking en uitvoer op.
3. **10 minuten toepassen:** voorspel een klein voorbeeld, voer het uit en vergelijk.
4. **5 minuten uitleggen:** vertel hardop waarom deze oplossing gekozen is.
5. **5 minuten vastleggen:** noteer een fout, het bewijs en je volgende stap in het leerlogboek.

Dit is een voorgestelde routine, geen belofte dat je na een vast aantal dagen
werkbekwaam bent. Herhaal moeilijke onderdelen tot je ze ook op nieuwe voorbeelden
kunt toepassen.

## Vier niveaus, zonder jezelf iets wijs te maken

| Niveau | Wat je werkelijk kunt | Eerlijk bewijs |
|---|---|---|
| 0 — herkennen | Je kent het woord wanneer je het leest | Je wijst het aan in code |
| 1 — uitleggen | Je legt het uit in eigen woorden | Je voorspelt drie voorbeeldrijen |
| 2 — aanpassen | Je verandert een regel en controleert het resultaat | Kleine wijziging plus verwacht/werkelijk resultaat |
| 3 — onderzoeken | Je vindt een fout en verdedigt een oplossing | Diagnose, bewijs, herstel en beperking |

Scoor per vaardigheid. Iemand kan SQL op niveau 2 beheersen en Fabric nog op niveau
0. Een README, certificaat of gegenereerd project vult die score niet automatisch in.
Zelfstandig betekent dat jij redeneert en controleert; documentatie raadplegen mag.

## Een leerroute van twee weken

| Sessie | Actie | Tastbaar resultaat |
|---|---|---|
| 1 | Lees de projectroute en teken de bestaande keten | Tekening met echte bestandsnamen |
| 2 | Traceer één record | Voor/na-tabel met uitleg |
| 3 | Onderzoek types, nulls en dubbele records | Drie randgevallen met verwachte uitkomst |
| 4 | Leg grain en sleutels uit | Eén zin per tabel |
| 5 | Bereken een KPI met de hand | Rekensom die je aan code koppelt |
| 6 | Onderzoek een join of groepering | Aantallen vóór en na |
| 7 | Herhaal sessies 1–6 zonder uitleg | Lijst van wat je nog niet zelfstandig kunt |
| 8 | Maak oefening 1 uit deze repo | Antwoord vóór je de oplossing opent |
| 9 | Maak de foutzoekoefening | Hypothese, controle, conclusie |
| 10 | Bespreek kwaliteit en actualiteit | Eén kwaliteitsregel en één tekortkoming |
| 11 | Bespreek performance en herstel | Eén meetplan en één herstartscenario |
| 12 | Vertaal een zakelijke vraag | KPI-afspraak met acceptatievoorbeeld |
| 13 | Geef een demo van vijf minuten | Vertelling met bron, verwerking, resultaat en beperking |
| 14 | Herhaal de zelftest op een nieuw voorbeeld | Nieuwe score met bewijs |

## AI als begeleider

Gebruik bijvoorbeeld deze prompts:

> “Stel één vraag over deze functie. Geef nog geen antwoord. Wacht op mijn uitleg
> en wijs daarna precies aan wat ik verkeerd begrepen heb.”

> “Geef drie kleine invoerrijen en laat mij de uitvoer voorspellen. Toon de
> oplossing pas nadat ik mijn voorspelling heb gegeven.”

> “Ik denk dat deze join de omzet verdubbelt door dubbele dimensiesleutels.
> Welke controle kan die hypothese weerleggen? Schrijf nog geen fix.”

> “Beoordeel mijn uitleg aan de hand van de code. Scheid wat aantoonbaar is van
> wat ik aanneem. Stel een vervolgvraag als mijn antwoord te vaag is.”

Gebruik bij voorkeur synthetische voorbeelden. Plak geen credentials of echte
klantgegevens in een prompt. Wanneer AI een oplossing geeft: voorspel eerst het
effect, bekijk het verschil en controleer een normaal én een foutscenario.

## Herhaalkaarten

Dek de rechterkolom af en antwoord hardop. Herhaal bijvoorbeeld de volgende dag,
na drie dagen en na een week. Varieer de voorbeelden.

| Vraag | Kernantwoord |
|---|---|
| Wat is grain? | De exacte betekenis van één rij |
| Wat maakt een record dubbel? | De afgesproken logische sleutel, niet alleen gelijke waarden |
| Waarom een raw-laag? | Herkomst bewaren en verwerking opnieuw kunnen uitvoeren |
| ETL versus ELT? | Transformeren vóór of na laden in de beoogde dataomgeving |
| Upsert versus snapshot? | Huidige waarde bijwerken versus toestanden over tijd bewaren |
| Wat is idempotent? | Dezelfde logische invoer veroorzaakt geen extra effect bij herhaling |
| Waarom kan een join omzet verdubbelen? | Meerdere matches per feit vermenigvuldigen resultaatrijen |
| WHERE versus HAVING? | Rijen filteren versus groepen filteren |
| Waarom is NULL geen nul? | Onbekend is iets anders dan een gemeten nul |
| Feit versus dimensie? | Gebeurtenis/meting versus beschrijvende context |
| Wat is een semantisch model? | Zakelijke betekenis via tabellen, relaties en berekeningen |
| Wat zegt een groen CI-vinkje? | Dat de uitgevoerde controles slaagden; controleer skips |
| Wat meet actualiteit? | Leeftijd van bruikbare brondata, niet alleen de laatste jobstart |
| Waarom een cache onderzoeken? | De getoonde waarde kan ouder zijn dan de opgeslagen waarde |
| Waarom een holdout? | Voorspellingen beoordelen op data die niet voor training zijn gebruikt |
| Hoe controleer je een KPI? | Definitie, handmatig voorbeeld, bron/doelvergelijking en randgevallen |
| Wat is lineage? | Herkomst en bewerkingspad van een resultaat |
| Hoe bewijs je een vaardigheid? | Uitleg plus toepassen, controleren en beperkingen benoemen |

## Een project in vijf minuten uitleggen

1. **Probleem:** voor wie is dit en welke beslissing ondersteunt het?
2. **Bron:** waar komen gegevens vandaan; zijn ze synthetisch, live of historisch?
3. **Verwerking:** neem één record door de echte functies mee.
4. **Model en KPI:** wat stelt een rij voor en hoe ontstaat het getal?
5. **Betrouwbaarheid:** welke fout wordt tegengehouden en welke nog niet?
6. **Grens:** wat ontbreekt en welke volgende controle zou je uitvoeren?

Zeg bij AI-ondersteund werk precies wat klopt, bijvoorbeeld:
“De code is met AI-ondersteuning gebouwd. Ik heb deze berekening zelf nagerekend
en dit foutscenario onderzocht.” Zeg dit alleen wanneer je dat daadwerkelijk deed.

## Zelftest voordat je een vaardigheid claimt

- [ ] Ik leg het uit zonder tekst voor te lezen.
- [ ] Ik vind de relevante functie of query terug.
- [ ] Ik voorspel een normaal voorbeeld én een randgeval.
- [ ] Ik pas een kleine bedrijfsregel aan en controleer het gevolg.
- [ ] Ik herken minstens één beperking in de bestaande code.
- [ ] Ik kan aangeven wat AI deed en wat ik zelf heb gecontroleerd.

Voor een zelfstandige productierol komen daar beheer, incidenten, toegangsrechten,
performance en samenwerking bij. Deze leermap is oefenmateriaal, geen vervanging
voor aangetoonde praktijkervaring.

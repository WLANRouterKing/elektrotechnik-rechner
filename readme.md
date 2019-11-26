# Cryption CMS

Hier entsteht ein neues [Content-Management-System](https://de.wikipedia.org/wiki/Content-Management-System) basierend auf Python ([Flask](https://www.palletsprojects.com/))

Die Projektstruktur kann sich im laufe der Entwicklung möglicherweise mehrmals ändern.

# Geplanter Release

1 - 2. Quartal 2020

# Features

Standardmäßige Verschlüsselung sensibler Inhalte mit Hilfe von [PyNacl](https://pypi.org/project/PyNaCl/)

Abdeckung der [OWASP Top 10](https://www.owasp.org/index.php/Germany/Projekte/Top_10) und mehr...

Eine API-Schnittstelle mit möglichkeit der [asynchronen Verschlüsselung](https://de.wikipedia.org/wiki/Asymmetrisches_Kryptosystem).
So können sensible Daten sicher an Clients übertragen werden (Die Daten können nur vom Client selbst entschlüsselt werden)

Die Hauptmodule (Backend,Frontend,API) können bei Bedarf in den Einstellungen auf Sub-Domains umgestellt werden:
- api.example.com
- backend.example.com
- frontend.example.com

Standardmäßige implementierung von häufig benötigten Seitenelementen und Modulen wie zum Beispiel:

- News-Meldungen
- Termine
- Stellenanzeigen
- Mehrsprachigkeit
- SEO Optimierung
- ...

Ein internes [Web-Analytics](https://de.wikipedia.org/wiki/Web_Analytics) zur Auswertung von Webseiten Besuchen und Besucherverhalten.
Zur Datenaufbereitung und Auswertung wird [Machine Learning](https://de.wikipedia.org/wiki/Maschinelles_Lernen) eingesetzt.

Flask wird (hoffentlich) in Zukunft die Unterstützung von [ASGI](https://asgi.readthedocs.io/en/latest/) bereitstellen.
So können aufwendige Tasks asynchron abgearbeitet werden was die Performance einer Webanwendung enorm steigert.

# Plugins

Dieses CMS wird keine Möglichkeit für sogenannte Plugins bereitstellen.
Es sind in der Vergangenheit bei anderen CMS Systemen, die dieses Konzept anbieten,
immer wieder Sicherheitslücken aufgetreten, die genau mit diesem System vermieden werden sollen.
Wer die Funktionalität dieses Systems erweitern möchte muss das Plugin selbst Programmieren. Die Funktionalität des Remote-Update-Systems wird dadurch nicht beeinträchtigt werden insofern der Programmierer nicht in den Kern der Anwendung eingreift.










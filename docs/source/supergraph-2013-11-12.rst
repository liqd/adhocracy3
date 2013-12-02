Concept: The Supergraph - Summary 2013-11-12
==============================================


chronologisch
-------------

 - vor 12 monaten:
    - essenzkanten und sonst nicht viel
    - pseudocode-algorithmus gibt's in irgendeinem etherpad

 - jüngere geschichte:
    - komplexeres / flexibleres konzept
    - references (think json: "{content-type: ..., path: ...}")
    - wenn objekt aktualisiert wird, müssen eingehende referenzen benachrichtigt werden.
    - welche event handler gibt es?  -> hängt vom typ ab.

zum aktuellen verständnis:
--------------------------

 - dokument zeigt auf absätze.

 - watchlist: wenn sich was updatet, gibt's eine email.

 - category: either reference all DAGs or all versions.  (latter case:
   some versions fall into a category, some don't.)

 - zentraler use-case für essenz-ding: dokumente können aufgesplittet
   werden, aber es gibt trotzdem eindeutige versionen.  essenz-kanten
   will man vielleicht als eine variante von handlern.

 - vorschlag joscha: auf property-sheet-ebene essenzeigenschaft
   definieren: ein property-sheet ist entweder essentiell oder nicht.
   das macht es vielleicht einfacher, einen essenzbaum eines objekts
   zu bauen.

 - zyklen sind grundsätzlich erlaubt.

 - batch-updates sind eine optimierung einer folge von http posts /
   puts, haben aber die gleiche semantik.  ausnahme: event propagation
   findet nur einmal pro batchlauf statt.  (vielleicht kann man
   beweisen, dass das die gleiche semantik ist?  nicht im strengen
   sinn, weil weniger knoten angelegt werden: man will für mehrerer
   änderungen in einem batch nur eine neue version der beteiligten
   objekte anlegen.)

 - essenzkanten können keine zyklen bilden, weil objekten in einem
   essenzbaum nicht destruktiv kanten wachsen können.

 - einfache muster:

     - objekt hat lineare history, und ein objekt referenziert immer
       den head.

     - objekt referenziert immer genau eine version

     - objektreferenz wird immer dem user gegeben, wenn das
       referenzierte objekt ein update bekommt.  der user muss
       entscheiden.

     - user A ist auf watchlist von user B.  wenn user B eine neue
       email-adresse bekommt, will user A eine nachricht bekommen,
       aber nichts entscheiden: die referenz auf der watchlist wird
       mitgezogen.  (das ist ein komisches beispiel, weil man
       eigentlich eine nicht-versionierte user-id watchen möchte und
       nicht das user-metadata-objekt, aber vielleicht gibt es
       irgendwo ein besseres beispiel für das selbe muster.)

 - propagation muss für jeden schritt ausprogrammiert werden: objekt X
   schickt update events an referierendes objekt Y; objekt Y
   entscheidet, ob es an objekt Z, das objekt Y referiert, ein eigenes
   event schickt.

 - generell wird es spannend zu sehen, wie teuer die event-lawinen
   werden.

 - es gibt pyramid-events: (event-typ, geändertes objekt, interface
   des geänderten objekts).  diese events kann man subscriben.  der
   event-typ enthält (von hand programmiert) die information über die
   natur der änderung (z.b. welche attribute etc.).

 - dieses system kann man benutzen, um events über die referenzkanten
   zu propagieren.  die frage ist, ob man über den
   referenz-event-propagation-mechanismus alles abdecken kann, oder ob
   es noch andere eventhandler geben soll.



versionables
------------

lineare objekthistorie
~~~~~~~~~~~~~~~~~~~~~~

bedingungen:
 - kein merge (immer höchstens ein vorgänger)
 - kein fork (voränger muss immer aktueller head sein)
 - eine version ohne vorgänger darf nur einmal auf dem leeren DAG angelegt werden.

api ist gleich wie bei den anderen versionables.  (dag-versionables
und linear-versionbles sind spezialisierungen voneinander.)

implementierungsfrage / UI-frage: wie lockt man den head, falls
mehrere user bearbeiten?  natürlicher default: fehlermeldung bei
konflikt.  alles, was eleganter und mächtiger ist, will man vielleicht
auf DAGs bauen, nicht auf linearen versionen.



variants
~~~~~~~~

fork-graph, mit der einschränkung (im UI), dass nur von master
gebrancht werden kann.

varianten sind immer varianten einer norm.  man kann sie man
gegeneinander diffen.

A2: varianten einer norm sind relevant im kontext eines proposals und
können dort bewertet werden.  ein beteiligungsprozess entscheidet,
welche variante zur originalversion der nächsten version werden.
gibt's jetzt auch bei absatzweisem kommentieren.

speziell für varianten: wir brauchen ein tag, das den head markiert,
so dass die erzeugung von varianten durch forks den head nicht
verschiebt.  werden tags von paragraphs an die enthaltenden proposals
vererbt?  wie?

zwei modi: "edit" (tag weiterschleifen), "fork" (neues tag anlegen).

sönke findet spannend: ich habe mehrere versionen, die möglicherweise
inhaltlich auch gar nicht konkurrieren, und will jetzt in einem
demokratischen prozess einen merge daraus erstellen.  prozesse
determinieren wann welches tag wohin verschoben wird.  (achtung!  UI
*einfach* halten!)

es gibt update-metadaten wie z.b. "typo" und "inhalt".  ein like auf
einem objekt kann man als user so konfigurieren, dass es typo-updates
automatisch liked, bei inhalt-updates aber auf der alten version
sitzen bleibt.  (das ist ein beispiel für eine viel allgemeinere
klasse von anforderungen.  die lösung sollte möglichst flexibel sein.
oft will man einen moderator haben, dem man vertraut, die metadaten zu
pflegen und dabei nicht zu lügen.)

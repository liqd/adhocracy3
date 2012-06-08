
Software architecture
=====================


.. blockdiag::

   diagram {

     G [label = "Graph API"];
     SG [label = "Supergraph API \n(references, versioning, relations)"];

     H [label = "hirarchy\n (permissions, workflows, URL to object mapping)"];
     A [label = "abilities\n (rateable, commentable,..)"];
     W [label = "workflow\n (permissions, status, transition scripts)"];
     M [label = "domain model\n (paper, statement, project instance,..)"];

     VL [label = "View logic"];
     VJ [label = "JSON"];
     VH [label = "HTML"];
     VHS [label = "HTML snipplet"];
  
     G -> SG -> A -> M -> VL -> VH;
          SG -> H -> M;   VL -> VJ;
                W -> M;   VL -> VHS;

     group data {
      G; SG;
      color = "DarkBlue";
      label="data persistence";
     }
     group model {
      H; A; M; W;
      color = "Orange";
      label="aplication logic, domain model";
     }
     group presentation {
      VL; VH; VJ; VHS;
      color = "Green";
      label="presentation";
     }

     orientation = portrait;
   }


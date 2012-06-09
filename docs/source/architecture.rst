
Software architecture
=====================


.. blockdiag::

   diagram {

     G [label = "Graph API"];
     SG [label = "Supergraph API \n(references,\n versioning, relations)"];

     H [label = "hirarchy\n (local permissions,\n URL to object mapping)"];
     A [label = "abilities\n (rateable,\n commentable,..)"];
     W [label = "workflow\n (change permissions / status, transition scripts)"];
     M [label = "domain model\n (like paper, \n statement,\n project instance,..)"];

     VL [label = "View logic\n (check permissions)"];
     VJ [label = "JSON"];
     VH [label = "HTML page"];
     VHS [label = "HTML snippet \n (can be included in \n pages)"];

     browser1 [shape = actor label = "HTML client"]
     browser2 [shape = actor label = "HTML client"]
     js [shape = actor label = "Javascript client"]

     G -> SG -> A -> M -> H, W;
                        H -> W;
                  M, H, W -> VL;
                                VL -> VH;
                                VL -> VHS;
                                VL -> VJ;
     VH -> browser1;
     VHS -> browser2;
     VJ -> js;


     group data {
       G; SG;
       color = "DarkBlue";
       label="data persistence";
       orientation = portrait;
     }
     group model {
       H; A; M; W;
       color = "Orange";
       label="aplication logic, domain model";
       orientation = portrait;
     }
     group presentation {
       VL; VH; VJ; VHS; browser1; browser2; js;
       color = "Green";
       label="presentation";
       orientation = portrait;
     }

   }


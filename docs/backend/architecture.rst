Architecture
============

Software packages
-----------------

The backend and frontend is released with the following python packages:

adhocracy_core
   framework and generic rest api, admin frontend

adhocracy_sample
   examples how to customize resource/sheet types

adhocracy_frontend
   framework for the javascript frontend

adhocracy_xyz
   Backend extensions for project specific application

xyz
   projects specific application with javascript frontend


Frontend Technical Admin Interface (substanced)
-----------------------------------------------

.. blockdiag::

   diagram {

    browser -> cooky_auth -> html_sdi -> registry, resource;

    group clients {
      label = "Clients"
      browser;
      }
    group backend_server {
      group views {
        label = "Views"
        html_sdi;cooky_auth;
      }
      group resource_handling {
        label = "Resource Handling"
        registry;resource;
      }

    }

    browser [
        label = "Webbrowser",
        shape = actor
    ];
    cooky_auth [label = "authentication\ncookies"];
    html_sdi [label = "HTML\nadmin interface"];
    resource [stacked];
   }


====================    =============
====================    =============
HTML Admin interface    Technical admin interface (serverside rendering)
Authentication Cooky    Authentication based on cookies and session id.
====================    =============


Frontend Javascript (Single Page Application)
---------------------------------------------

.. blockdiag::
   :desctable:

   diagram {

    browser -- frontend -> cache -> token_auth -> rest -> registry, resource;
    browser -> html -> registry;
    frontend <- websockets <- websockets_client [class = "dotted"];
    cache <- purging [class = "dotted"];
    purging, websockets_client -> registry;

    class dotted [style = dotted];

    group clients {
      label = "Clients"
      browser; frontend;
      }
    group backend_server {
      group views {
        label = "Views"
        group {rest;html;token_auth;headers}
        group {purging;websockets_client;}
      }
      group resource_handling {
        label = "Resource Handling"
        registry;resource;
      }

    }

    browser [label = "Webbrowser", shape = actor];
    frontend [label = "Javascript\n Frontend"];
    cache [label = "Cache\ Reverse Proxy Server"];
    headers[label = "Cache Headers"]
    websockets [label = "Websockets\nServer"];
    token_auth [label = "Authentication\nToken"];
    rest [label = "JSON \n REST API"];
    html [label = "HTML\n Frontend"];
    purging [label = "cache purging"];
    websockets_client [label = "Websockets\nClient"];
    resource [stacked];
   }


====================    =============
====================    =============
Javscript Frontend      Single Page Application (client side rendering)
Cache Proxy             Proxy to cache http requests (varnish)
Cache Headers           Set http caching headers, compute etag)
Cache Purging           Send purge request to Cache server when resources are updated
Authentication Token    Authentication based on request header token.
REST API                JSON representation of resources to Create/Read/Update/Delete.
HTML Frontend           HTML representation of resources (only root, serves javascript/settings/routings)
Websockets client       Send notification mesages to the websockets server when resources are updated
====================    =============

Backend Resource Handling
-------------------------

.. blockdiag::

   diagram {

    registry -> factory, settings, metadata, changelog;
        changelog -> audit -> persistence_audit;
    resource -> hierarchy, permissions, sheet, etags;
        sheet -> search -> references;
        sheet -> schema -> data, references -> persistence;
        sheet -> workflow -> persistence;

    class dotted [style = dotted];

    group  {
      label = "Resource Handling"
      factory;registry;search;sheet;schema;workflow;settings;changelog;events;metadata;references;data;audit;messaging;
      group data_model {
          style = dashed;
          shape = line;
          color = "#FF0000";
          resource;etags;sheet;hierarchy;permissions;
      }
    }
    group {style = dashed;
           shape = line;
           color = "#FF0000";
           persistence;
           }
    group {style = dashed;
           shape = line;
           color = "#FF0000";
           persistence_audit;
           }

    resource [label = "Resource", stacked];
    factory [label = "Create Resource,\nGet sheets"];
    settings [label = "Configuration"];
    metadata [label = "Metadata\nResource/Sheet/\nWorkflowType"];
    sheet [label = "Resource Sheet", stacked];
    persistence [label = "Storage Main", shape = "flowchart.database"];
    persistence_audit [label = "Storage Audit", shape = "flowchart.database"];
   }


The red line groups responsibility for persistence data storage (Note: all
perstence data access should be done with the sheets). For further explenations
see :doc:`modules`.

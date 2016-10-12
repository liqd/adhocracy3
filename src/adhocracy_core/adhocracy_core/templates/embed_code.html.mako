<%page args="sdk_url='',
             frontend_url='',
             path='',
             widget='',
             autoresize='false',
             locale='en',
             autourl='false',
             initial_url='',
             nocenter='true',
             noheader='true',
             style='',
             "/>
<script src="${sdk_url}"></script>
<script> adhocracy.init('${frontend_url}',
                        function(adhocracy) {adhocracy.embed('.adhocracy_marker');
                        });
</script>
<div class="adhocracy_marker"
     data-path="${path}"
     data-widget="${widget}"
     data-autoresize="${autoresize}"
     data-locale="${locale}"
     data-autourl="${autourl}"
     data-initial-url="${initial_url}"
     %if nocenter!="false":
     data-nocenter="${nocenter}"
     %endif
     %if noheader!="false":
     data-noheader="${noheader}"
     %endif
     style="${style}">
</div>

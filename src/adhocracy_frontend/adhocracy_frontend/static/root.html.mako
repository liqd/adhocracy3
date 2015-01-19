<!doctype html>
<html>
    <head>
        <title>adhocracy root page</title>
        <meta charset="utf-8">
        % for url in css:
            <link rel="stylesheet" href="${url}"/>
        % endfor
        <base href="/" />
    </head>
    <body>

        <adh-view></adh-view>
        % for url in js:
            <script type="text/javascript" src="${url}"></script>
        % endfor

        <script type="text/javascript">
            require(["text!/config.json"], function(config_string) {
                var config = JSON.parse(config_string);

                require(["Adhocracy", "text!" + "${meta_api}"], function(Adh, meta_api_string) {
                    var meta_api = JSON.parse(meta_api_string);
                    $(document).ready(function() {
                        Adh.init(config, meta_api);
                    });
                });
            });
        </script>
    </body>
</html>

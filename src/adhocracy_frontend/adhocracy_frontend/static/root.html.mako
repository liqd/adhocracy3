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
        <!--[if lt IE 10]>
        <div class="unsupported-browser">
            <img src="/static/icons/png/attention.png"/>
            <div>
                <h1>Non-supported browser!</h1>
                <p>FIXME: Needs real text. Lorem Ipsum ist in der Industrie bereits der Standard Demo-Text seit 1500, als ein unbekannter Schriftsteller eine Hand voll Wörter nahm und diese durcheinander warf um ein
                Musterbuch zu erstellen.</p>
            </div>
        </div>
        <![endif]-->
        <!--[if gt IE 9]><!-->
        <adh-view></adh-view>
        % for url in js:
            <script type="text/javascript" src="${url}"></script>
        % endfor

        <script type="text/javascript">
            require(["Adhocracy", "text!${config}", "text!${meta_api}"], function(Adh, config_string, meta_api_string) {
                var config = JSON.parse(config_string);
                var meta_api = JSON.parse(meta_api_string);
                $(document).ready(function() {
                    Adh.init(config, meta_api);
                });
            });
        </script>
        <!--<![endif]-->
    </body>
</html>

vcl 4.0;
backend default {
  .host = "127.0.0.1";
  .port = "6541";
}

acl purge {
    "localhost";
}

sub vcl_recv {

    # purge purge requests if from localhost
    # Allow to purge regular expressioǹs with header
    # X-Purge-Regex and host name with X-Purge-Host.
    if (req.method == "PURGE") {
       if (!client.ip ~ purge) {
          return(synth(405, "Not allowed."));
       }
       ban("req.http.host == " + req.http.X-Purge-Host +
           " && req.url ~ " + req.url + req.http.X-Purge-Regex);
       return(synth(200, "Purged"));
    }

    /* pipe (ignore) non GET and HEAD and OPTIONS  requests*/
    if (req.method != "GET" &&
        req.method != "HEAD" &&
        req.method != "OPTIONS") {
        return(pipe);
    }
}

sub vcl_backend_response {
    if (beresp.http.content-type ~ "application/json") {
        set beresp.do_gzip = true;
    }
}

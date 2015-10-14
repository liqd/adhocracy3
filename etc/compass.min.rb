http_path = "/"
css_dir = "src/current/current/build/stylesheets/min"
sass_dir = "src/current/current/build/stylesheets/scss"
fonts_dir = "src/current/current/build/fonts"
http_fonts_path = "../../fonts"
images_dir = "src/current/current/build/images"
javascripts_dir = "src/current/current/build/js"
environment = :production
sourcemap = true
add_import_path "src/current/current/build/stylesheets/scss"
Sass::Script::Number.precision = 8
asset_cache_buster do |path, file|
    if file
        hash = Digest::MD5.file(file.path).hexdigest
        "_=%s" % hash
    else
        ""
    end
end

(function() {
    var fr_FR = obviel.i18n.translationSource(
        {'Hello world!': 'Bonjour monde!'});
    obviel.i18n.registerTranslation('fr_FR', fr_FR);

    var _ = obviel.i18n.translate();
    
    $(document).ready(function() {    
        // will not be translated as no locale has yet been set
        $('#untranslated').text(_("Hello world!"));
        
        // now set the locale to French
        obviel.i18n.setLocale('fr_FR');
        
        // this will be translated
        $('#translated').text(_("Hello world!"));
    });
}());

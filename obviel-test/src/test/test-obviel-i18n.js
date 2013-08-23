/*global obviel:false buster:false sinon:false */

var assert = buster.assert;

var i18n = obviel.i18n;

var setupTranslations = function() {
    var en_US = i18n.emptyTranslationSource();
    var fr_FR = i18n.translationSource({'Hello world!':
                                        'Bonjour monde!'});
    var nl_NL = i18n.translationSource({'Hello world!':
                                        'Hallo wereld!'});
    i18n.registerTranslation('en_US', en_US, 'i18ntest');
    i18n.registerTranslation('fr_FR', fr_FR, 'i18ntest');
    i18n.registerTranslation('nl_NL', nl_NL, 'i18ntest');
};

var setupTranslationsDefaultDomain = function() {
    var en_US = i18n.emptyTranslationSource();
    var fr_FR = i18n.translationSource({'Hello world!':
                                        'Bonjour monde!'});
    var nl_NL = i18n.translationSource({'Hello world!':
                                        'Hallo wereld!'});
    i18n.registerTranslation('en_US', en_US);
    i18n.registerTranslation('fr_FR', fr_FR);
    i18n.registerTranslation('nl_NL', nl_NL);
};

var setupTranslationsMultiDomains = function() {
    var en_US = i18n.emptyTranslationSource();
    var fr_FR = i18n.translationSource({'Hello world!':
                                        'Bonjour monde!'});
    var nl_NL = i18n.translationSource({'Hello world!':
                                        'Hallo wereld!'});
    i18n.registerTranslation('en_US', en_US, 'i18ntest');
    i18n.registerTranslation('fr_FR', fr_FR, 'i18ntest');
    i18n.registerTranslation('nl_NL', nl_NL, 'i18ntest');

    // now register second domain called 'other'
    en_US = i18n.emptyTranslationSource();
    fr_FR = i18n.translationSource({'Bye world!':
                                    'Au revoir monde!'});
    nl_NL = i18n.translationSource({'Bye world!':
                                    'Tot ziens wereld!'});
    i18n.registerTranslation('en_US', en_US, 'other');
    i18n.registerTranslation('fr_FR', fr_FR, 'other');
    i18n.registerTranslation('nl_NL', nl_NL, 'other');
};

var setupPluralTranslations = function() {
    var en_US = i18n.emptyTranslationSource();
    var nl_NL = i18n.translationSource({'1 elephant.':
                                        ['{count} elephants.',
                                         '1 olifant.',
                                         '{count} olifanten.']});
    i18n.registerTranslation('en_US', en_US, 'i18ntest');
    i18n.registerTranslation('nl_NL', nl_NL, 'i18ntest');
};

var i18nTestCase = buster.testCase('i18n tests', {
    setUp: function() {
        this.server = sinon.fakeServer.create();
        this.server.autoRespond = true;

        // XXX would be nice to be able to register this centrally
        this.mockJson = function(url, json) {
            var getResponse;
            if ($.isFunction(json)) {
                getResponse = json;
            } else {
                getResponse = function() {
                    return json;
                };
            }
            var response = function(request) {
                request.respond(200, { 'Content-Type': 'application/json'},
                                JSON.stringify(getResponse()));
            };
            this.server.respondWith('GET', url, response);
        };
        
    },
    tearDown: function() {
        obviel.i18n.clearTranslations();
        obviel.i18n.clearLocale();
        this.server.restore();
    },


    'no locale set': function() {
        setupTranslations();

        var _ = i18n.translate('i18ntest');
        
        assert.equals(_('Hello world!'), 'Hello world!');
    },

    'non-translating en_US locale': function() {
        setupTranslations();

        i18n.setLocale('en_US');

        var _ = i18n.translate('i18ntest');
        
        assert.equals(_('Hello world!'), 'Hello world!');
    },

    'fr_FR locale': function() {
        setupTranslations();

        i18n.setLocale('fr_FR');

        var _ = i18n.translate('i18ntest');
        
        assert.equals(_('Hello world!'), 'Bonjour monde!');
    },

    'switch locale from not set to fr_FR': function() {
        setupTranslations();
        
        var _ = i18n.translate('i18ntest');

        assert.equals(_('Hello world!'), 'Hello world!');

        i18n.setLocale('fr_FR');
        
        assert.equals(_('Hello world!'), 'Bonjour monde!');
    },

    'switch locale from fr_FR to not set': function() {
        setupTranslations();
        
        i18n.setLocale('fr_FR');
        
        var _ = i18n.translate('i18ntest');

        assert.equals(_('Hello world!'), 'Bonjour monde!');

        i18n.clearLocale();
        
        assert.equals(_('Hello world!'), 'Hello world!');
    },

    'switch locale from non-translating en_US to translating fr_FR': function() {
        setupTranslations();

        i18n.setLocale('en_US');

        var _ = i18n.translate('i18ntest');
        
        assert.equals(_('Hello world!'), 'Hello world!');

        i18n.setLocale('fr_FR');
        
        assert.equals(_('Hello world!'), 'Bonjour monde!');
    },


    'switch locale from translating fr_FR to non-translating enEN': function() {
        setupTranslations();

        i18n.setLocale('fr_FR');

        var _ = i18n.translate('i18ntest');

        assert.equals(_('Hello world!'), 'Bonjour monde!');

        i18n.setLocale('en_US');
        
        assert.equals(_('Hello world!'), 'Hello world!');
    },

    'switch locale from translating fr_FR to translating nl_NL': function() {
        setupTranslations();

        i18n.setLocale('fr_FR');

        var _ = i18n.translate('i18ntest');

        assert.equals(_('Hello world!'), 'Bonjour monde!');

        i18n.setLocale('nl_NL');
        
        assert.equals(_('Hello world!'), 'Hallo wereld!');
    },

    'switch domain, non-translating en_US locale': function() {
        setupTranslationsMultiDomains();

        i18n.setLocale('en_US');
        
        var _ = i18n.translate('i18ntest');
        
        assert.equals(_('Hello world!'), 'Hello world!');

        assert.equals(_('Bye world!'), 'Bye world!');

        _ = i18n.translate('other');
        
        assert.equals(_('Hello world!'), 'Hello world!');

        assert.equals(_('Bye world!'), 'Bye world!');
    },

    'switch domain, translating fr_Fr locale': function() {
        setupTranslationsMultiDomains();

        i18n.setLocale('fr_FR');

        var _ = i18n.translate('i18ntest');
        
        assert.equals(_('Hello world!'), 'Bonjour monde!');

        assert.equals(_('Bye world!'), 'Bye world!');

        _ = i18n.translate('other');
        
        assert.equals(_('Hello world!'), 'Hello world!');

        assert.equals(_('Bye world!'), 'Au revoir monde!');
    },

    "default domain should not pick up from non-default": function() {
        var nl_NL = i18n.translationSource({'This is foo.':
                                            'Dit is foo.'});
        
        i18n.registerTranslation('nl_NL', nl_NL, 'other');

        var _ = obviel.i18n.translate();

        obviel.i18n.setLocale('nl_NL');

        var t = _("This is foo.");
        
        assert.equals(t, 'This is foo.');
    },

    "default domain": function() {
        setupTranslationsDefaultDomain();

        i18n.setLocale('fr_FR');

        var _ = i18n.translate('default');
        
        assert.equals(_("Hello world!"), 'Bonjour monde!');
    },

    "default domain no parameters": function() {
        setupTranslationsDefaultDomain();

        i18n.setLocale('fr_FR');

        var _ = i18n.translate();
        
        assert.equals(_("Hello world!"), 'Bonjour monde!');
    },

    'getLocale without locale set': function() {
        assert.equals(i18n.getLocale(), null);
    },

    'getLocale with locale set': function() {
        setupTranslationsMultiDomains();

        i18n.setLocale('fr_FR', 'i18ntest');

        assert.equals(i18n.getLocale(), 'fr_FR');
    },

    'getLocale after locale change': function() {
        setupTranslationsMultiDomains();

        i18n.setLocale('fr_FR');
        i18n.setLocale('nl_NL');
        
        assert.equals(i18n.getLocale(), 'nl_NL');
    },

    'use unknown locale': function() {
        setupTranslations();

        assert.exception(function() {
            i18n.setLocale('unknown');
        }, 'I18nError');
    },

    'set unknown domain': function() {
        setupTranslations();

        var translate = i18n.translate('unknown');
        translate("foo");
        assert(true); // we expect this to pass without errors
    },

    'pluralize without translation': function() {
        setupPluralTranslations();

        var ngettext = i18n.pluralize('i18ntest');

        assert.equals(i18n.variables(ngettext('1 elephant.', '{count} elephants.', 1),
                                     {count: 1}), '1 elephant.');
        assert.equals(i18n.variables(ngettext('1 elephant.', '{count} elephants.', 2),
                                     {count: 2}), '2 elephants.');
    },


    'pluralize with translation': function() {
        setupPluralTranslations();

        var ngettext = i18n.pluralize('i18ntest');

        i18n.setLocale('nl_NL');
        
        assert.equals(i18n.variables(ngettext('1 elephant.', '{count} elephants.', 1),
                                     {count: 1}), '1 olifant.');
        assert.equals(i18n.variables(ngettext('1 elephant.', '{count} elephants.', 2),
                                     {count: 2}), '2 olifanten.');
    },

    'complex pluralization rule': function() {
        var en_US = i18n.emptyTranslationSource();
        var pl_PL = i18n.translationSource({
            '': {
                'Plural-Forms': 'nplurals=3; plural=(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
            },
            '1 file.':
            ['{count} file.',
             '1 plik.',
             '{count} pliki.',
             "{count} pliko'w."]});
        i18n.registerTranslation('en_US', en_US, 'i18ntest');
        i18n.registerTranslation('pl_PL', pl_PL, 'i18ntest');

        var ngettext = i18n.pluralize('i18ntest');
        
        i18n.setLocale('pl_PL');
        assert.equals(i18n.variables(ngettext('1 file.', '{count} files.', 1), {count: 1}),
                      '1 plik.');
        assert.equals(i18n.variables(ngettext('1 file.', '{count} files.', 2), {count: 2}),
                      '2 pliki.');
        assert.equals(i18n.variables(ngettext('1 file.', '{count} files.', 3), {count: 3}),
                      '3 pliki.');
        assert.equals(i18n.variables(ngettext('1 file.', '{count} files.', 4), {count: 4}),
                      '4 pliki.');
        assert.equals(i18n.variables(ngettext('1 file.', '{count} files.', 5), {count: 5}),
                      "5 pliko'w.");
        assert.equals(i18n.variables(ngettext('1 file.', '{count} files.', 21), {count: 21}),
                      "21 pliko'w.");
        assert.equals(i18n.variables(ngettext('1 file.', '{count} files.', 22), {count: 22}),
                      "22 pliki.");
    },

    "load i18n": function(done) {
        $('head').append(
            '<link type="application/json" rel="i18n" href="i18ntest.i18n" />');
        this.mockJson('i18ntest.i18n', {
            "i18ntest": [
                {
                    "locale": "en_US",
                    "url": null
                },
                {
                    "locale": "nl_NL",
                    "url": "i18n-nl.json"
                }
            ]
        });
        this.mockJson('i18n-nl.json', {
            "": {
                "Content-Transfer-Encoding": "8bit",
                "Content-Type": "text/plain; charset=UTF-8",
                "Language": "nl",
                "Language-Team": "Dutch",
                "Last-Translator": "Martijn Faassen <faassen@startifact.com>",
                "MIME-Version": "1.0",
                "PO-Revision-Date": "2011-05-04 18:44+0200",
                "POT-Creation-Date": "2011-05-04 18:42+0200",
                "Plural-Forms": "nplurals=2; plural=(n != 1);",
                "Project-Id-Version": "obviel_forms 0.1",
                "Report-Msgid-Bugs-To": ""
            },
            "{count} crow": ["{count} crows", "{count} kraai", "{count} kraaien"],
            "greetings human!": [null, "gegroet mens!"]
        });
        i18n.load().done(function() {
            i18n.setLocale('nl_NL').done(function() {
                var _ = i18n.translate('i18ntest');
                assert.equals(_('greetings human!'), 'gegroet mens!');
                done();
            });
        });
    },

    "load multiple domains from url": function(done) {
        this.mockJson('a.json', {'a': [null, 'A']});
        this.mockJson('b.json', {'b': [null, 'B']});
        this.mockJson('test.i18n',
                      {'first': [{'locale': "en_US", url: 'a.json'}],
                       'second': [{'locale': "en_US", url: 'b.json'}]}
                     );
        i18n.loadI18nFromUrl('test.i18n').done(function() {
            i18n.setLocale('en_US').done(function() {
                var _ = i18n.translate('first');
                assert.equals(_('a'), 'A');
                assert.equals(_('b'), 'b');
                _ = i18n.translate('second');
                assert.equals(_('a'), 'a');
                assert.equals(_('b'), 'B');
                done();
            });
        });
    }

});


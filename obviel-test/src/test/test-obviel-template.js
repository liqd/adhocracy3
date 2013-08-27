/*global obviel:false, buster:false sinon:false, console:false */

var assert = buster.assert;
var refute = buster.refute;

var obtemp = obviel.template;

var normalizeHtml = function(html) {
    var el = $(document.createElement('div'));
    return el.html(html).html();
};

var extraNormalize = function(text) {
    text = obtemp.normalizeSpace(text);
    // wipe out all whitespace too, as IE and FF won't be consistent otherwise
    text = text.replace(/\s/g, '');
    return text;
};

buster.assertions.add('htmlEquals', {
    assert: function(actual, expected) {
        return actual === normalizeHtml(expected);
    },
    assertMessage: "${2}${0} expected to be equal to ${1}",
    refuteMessage: "${2}${0} expected not to be equal to ${1}",
    expectation: "toHtmlEquals"
});

function assertEnoughArguments(name, args, num) {
    if (args.length < num) {
        buster.assertions.fail("[" + name + "] Expected to receive at least " +
                               num + " argument" + (num > 1 ? "s" : ""));
        return false;
    }
    
    return true;
}

function interpolate(string, property, value) {
    return string.replace(new RegExp("\\$\\{" + property + "\\}", "g"), value);
}

function interpolateProperties(msg, properties) {
    for (var prop in properties) {
        msg = interpolate(msg, prop, buster.assertions.format(properties[prop]));
    }
    
    return msg || "";
}

function interpolatePosArg(message, values) {
    var value;
    values = values || [];
    
    for (var i = 0, l = values.length; i < l; i++) {
        message = interpolate(message, i, buster.assertions.format(values[i]));
    }
    
    return message;
}

function fail(type, assertion, msg) {
    delete this.fail;
    var message = interpolateProperties(
        interpolatePosArg(buster.assertions[type][assertion][msg] || msg,
                          [].slice.call(arguments, 3)), this);
    buster.assertions.fail("[" + type + "." + assertion + "] " + message);
}

function countAssertion() {
    if (typeof buster.assertions.count !== "number") {
        buster.assertions.count = 0;
    }
    
    buster.assertions.count += 1;
}

function captureException(callback) {
        try {
            callback();
        } catch (e) {
            return e;
        }
    
    return null;
}

assert.raises = function(callback, exception, message) {
    /*jshint newcap:false */
    countAssertion();
    if (!assertEnoughArguments("assert.raises", arguments, 1)) {
        return undefined;
    }
    if (!callback) {
        return undefined;
    }
    var err = captureException(callback);
    if (!err) {
        if (exception === undefined) {
            return fail.call({}, "assert", "raises", "typeNoExceptionMessage",
                             message, exception);
        } else {
            return fail.call({}, "assert", "raises", "message",
                                 message, exception);
        }
    }
    // XXX should add facility to handle with exception being undefined
    // when the wrong exception is thrown we want to see a stack trace
    // or string
    if (!(err instanceof exception)) {
        if (typeof window !== "undefined" && typeof console !== "undefined") {
            console.log(err);
        }
        if (err instanceof Error) {
            return fail.call({}, "assert", "raises", "typeFailMessage",
                         message, new exception().name, err.name);
        } else {
            
            return fail.call({}, "assert", "raises", "unknownExceptionMessage",
                             message, new exception().name);
        }
        
        
    }
    buster.assertions.emit("pass", "assert.raises", message, callback, exception);
    return undefined;
};

assert.raises.typeNoExceptionMessage = "Expected ${1} but no exception was thrown";
assert.raises.message = "Expected exception";
assert.raises.typeFailMessage = "Expected ${1} but threw ${2}";
assert.raises.unknownExceptionMessage = "Expected ${1} but threw non-error exception";
assert.raises.expectationName = "toThrow2";

var Translations = function() {
    this._trans = {
        'Hello world!': 'Hallo wereld!',
        'Bye world!': 'Tot ziens wereld!',
        'one < two': 'een < twee',
        'Their message was: "{message}".': 'Hun boodschap was: "{message}".',
        'Hello {who}!': '{who}, hallo!',
        'Hello {who}! ({who}?)': '{who}, hallo! ({who}?)',
        'Hello {qualifier} {who}!': '{qualifier} {who}, hallo!',
        'Hello!{break}Bye!': 'Hallo!{break}Tot ziens!',
        'explicit': 'explicit translated',
        'explicitWho': 'grote {who}',
        // note that the string in the HTML has whitespace in it, but not here
        'This has whitespace.': 'Dit heeft witruimte.',
        'Open {@open} and close {@close}': 'Openen {@open} en sluiten {@close}',
        'Open {@open}': 'Openen {'
    };
};

Translations.prototype.gettext = function(msgid) {
    var result = this._trans[msgid];
    if (result === undefined) {
        return msgid;
    }
    return result;
};

var pluralTranslations = {
    '1 cow': {one: '1 koe', more: '{count} koeien'},
    '{count} cow': {one: '{count} koe', more: '{count} koeien'}
};

var getPluralTranslation = function(singularMsgid, pluralMsgid,
                                      count) {
    var translation = pluralTranslations[singularMsgid];
    if (translation === undefined) {
        if (count === 1) {
            return singularMsgid;
        } else {
            return pluralMsgid;
        }
    }

    if (count === 1) {
        return translation.one;
    } else {
        return translation.more;
    }
};

var testel = function() {
    return $("<div></div>");
};

var renderEl = function(text, obj) {
    var el = testel();
    var template = new obtemp.Template(text);
    var translations = new Translations();
    var getTranslation = function(msgid) {
        return translations.gettext(msgid);
    };
    template.render(el, obj, {getTranslation: getTranslation,
                              getPluralTranslation: getPluralTranslation});
    return el;
};

var render = function(text, obj) {
    var el = renderEl(text, obj);
    return el.html();
};

var templateTestCase = buster.testCase('template tests', {
    setUp: function() {
        this.server = sinon.fakeServer.create();
        this.server.autoRespond = true;
        $('#jsview-area').html('<div id="viewdiv"></div><div id="normalize"></div>');
    },
    tearDown: function() {
        obviel.template.clearFormatters();
        obviel.template.clearFuncs();
        obviel.clearRegistry();
        obviel.template.setDefaultViewName('default');
        this.server.restore();
    },

    'template with text, without variable': function() {
        assert.htmlEquals(render('<p>Hello world!</p>', {}),
                          '<p>Hello world!</p>');
    },
    
    'render template twice on same element': function() {
        assert.htmlEquals(render('<p>Hello world!</p>', {}),
                          '<p>Hello world!</p>');
        assert.htmlEquals(render('<p>Bye world!</p>', {}),
                          '<p>Bye world!</p>');
    },
    
    "empty element": function() {
        assert.htmlEquals(render('<p></p>', {}),
                          '<p></p>');
    },
    
    "just text": function() {
        assert.htmlEquals(render("Hello world!", {}),
                          'Hello world!');
    },
    
    "text with a variable": function() {
        assert.htmlEquals(render("Hello {who}!", {who: "world"}),
                          'Hello world!');
    },
    
    
    'text with sub element': function() {
        assert.htmlEquals(render('<p><em>Sub</em></p>', {}),
                          '<p><em>Sub</em></p>');
    },
    
    "text with element with variable": function() {
        assert.htmlEquals(render("Hello <em>{who}</em>!", {who: "world"}),
                          'Hello <em>world</em>!');
    },
    
    'element with empty element': function() {
        assert.htmlEquals(render('<p><em></em></p>', {}),
                          '<p><em></em></p>');
    },
    
    'element with variable': function() {
        assert.htmlEquals(render('<p>{who}</p>', {who: 'world'}),
                          '<p>world</p>');
    },
    
    'element with text and variable': function() {
        assert.htmlEquals(render('<p>Hello {who}!</p>', {who: 'world'}),
                          '<p>Hello world!</p>');
    },
    
    'variable and sub element': function() {
        assert.htmlEquals(render('<p>a <em>very nice</em> {time}, sir!</p>', {time: 'day'}),
                          '<p>a <em>very nice</em> day, sir!</p>');
    },
    
    
    'two elements': function() {
        assert.htmlEquals(render('<p>First</p><p>Second</p>', {}),
                          '<p>First</p><p>Second</p>');
    },
    
    'element with text following': function() {
        assert.htmlEquals(render('<p>First</p>more', {}),
                          '<p>First</p>more');
    },
    
    'text with element following': function() {
        assert.htmlEquals(render('more<p>First</p>', {}),
                          'more<p>First</p>');
    },
    
    'variable in sub element': function() {
        assert.htmlEquals(render('<p>a <em>{quality}</em> day, sir!</p>', {quality: 'nice'}),
                          '<p>a <em>nice</em> day, sir!</p>');
    },
    
    
    'template with multiple variables': function() {
        assert.htmlEquals(render('<p>{first}{second}</p>', {first: 'One', second: 'Two'}),
                          '<p>OneTwo</p>');
    },
    
    "variable with dotted name": function() {
        assert.htmlEquals(render('<p>Hello {something.who}!</p>', {something: {who: 'world'}}),
                          '<p>Hello world!</p>');
    },
    
    "variable with formatter": function() {
        obtemp.registerFormatter('upper', function(value) {
            return value.toUpperCase();
        });
        assert.htmlEquals(render('{foo|upper}', {foo: 'hello'}),
                          'HELLO');
    },
    
    "variable with formatter that does not exist": function() {
        assert.raises(function() {
            render('{foo|upper}', {foo: 'hello'});
        }, obtemp.RenderError);
    },
    
    "nested scoping": function() {
        assert.htmlEquals(render('<div data-with="second">{alpha}{beta}</div>',
                                 {'beta': 'Beta',
                                  second: {alpha: "Alpha"}}),
                          '<div>AlphaBeta</div>');
    },
    
    "nested scoping with override": function() {
        assert.htmlEquals(render('<div data-with="second">{alpha}{beta}</div>',
                                 {beta: 'Beta',
                                  second: {'alpha': "Alpha",
                                           'beta': "BetaOverride"}}),
                          '<div>AlphaBetaOverride</div>');
    },
    
    "things disappear out of scope": function() {
        assert.raises(function()  {
            render('<div><div data-with="sub">{foo}</div><div>{foo}</div>',
                   {sub:{
                       foo: "Hello!"
                   }});
        }, obtemp.RenderError);
        
    },
    
    "variable that does not exist": function() {
        assert.raises(function() {
            render('<p>{who}</p>', {});
        }, obtemp.RenderError);
        
    },
    
    // attempting to debug IE 7 issues:
    // things to try
    // cloneNode versus jQuery clone
    // attribute set in original HTML versus set manually
    // attribute set using setAttribute versus .attr()
    // attribute retrieved using getAttribute versus .attr()
    
    // 'attribute change detected by innerHTML': function() {
    //     var outerEl = $('<div></div>');
    //     var innerEl = $('<p class="Bar"></p>');
    //     outerEl.append(innerEl);
    //     //innerEl.get(0).setAttribute('class', 'Bar');
    //     //innerEl.attr('class', 'Bar');
    //     var newOuterEl = outerEl.clone();
    //     //newOuterEl.get(0).childNodes[0].setAttribute('class', 'Foo');
    
    //     $(newOuterEl.get(0).childNodes[0]).attr('class', 'Foo');
    //     // assert.equals(outerEl.children()[0].attr('class'), 'Foo');
    //     assert.equals(newOuterEl.html(), '<P class=Foo></P>');
    //     assert.equals(outerEl.html(), '');
    // },
    
    'attribute variable': function() {
        assert.htmlEquals(render('<p class="{a}"></p>', {a: 'Alpha'}),
                          '<p class="Alpha"></p>');
    },
    
    'attribute text and variable': function() {
        assert.htmlEquals(render('<p class="the {text}!"></p>', {text: 'thing'}),
                          '<p class="the thing!"></p>');
    },
    
    'attribute in sub-element': function() {
        assert.htmlEquals(render('<p><em class="{a}">foo</em></p>', {a: 'silly'}),
                          '<p><em class="silly">foo</em></p>');
    },
    
    
    'json output for objects': function() {
            var template = new obtemp.Template('{@.}');
        var el = $("<div></div>");
        
        template.render(el, {'a': 'silly'});
        
        // wish I could do a simple htmlEqual but IE 8 is too helpful
        // with whitespace
        assert.equals(extraNormalize(el.text()),
                      extraNormalize('{\n    "a": "silly"\n}'));
    },

    'json output for arrays': function() {
            var template = new obtemp.Template('{@.}');
        var el = $("<div></div>");
        
        template.render(el, ['a', 'b']);

        // wish I could do a simple htmlEqual but IE 8 is too helpful
        // with whitespace
        assert.equals(extraNormalize(el.text()),
                      extraNormalize("[\n    \"a\",\n    \"b\"\n]"));
    },


    "element with both id and variable": function() {
        assert.htmlEquals(render('<p id="foo">{content}</p>', {content: 'hello'}),
                          '<p id="foo">hello</p>');
    },

    "disallow dynamic id in template": function() {
        assert.raises(function() {
            render('<p id="{dynamic}"></p>', {dynamic: 'test'});
        }, obtemp.CompilationError);
    },

    "data-id": function() {
        assert.htmlEquals(render('<p data-id="{foo}"></p>', {foo: 'Foo'}),
                          '<p id="Foo"></p>');
    },

    'non-dynamic data-id': function() {
        assert.htmlEquals(render('<p data-id="foo"></p>', {}),
                          '<p id="foo"></p>');
    },

    "data-id with dynamic class": function() {
        // for some reason htmlEquals for normalized HTML compare doesn't
        // work on Chromium, so test by hand
        var el = renderEl('<p data-id="{foo}" class="{bar}"></p>',
                          {foo: 'Foo', bar: 'Bar'});
        var p_el = $('p', el);
        assert.equals(p_el.attr('id'), 'Foo');
        assert(p_el.hasClass('Bar'));
    },

    "disallow dynamic src in template": function() {
        assert.raises(function() {
            render('<img src="{dynamic}" />',
                   {dynamic: 'fixtures/destroy.png'});
        }, obtemp.CompilationError);
    },

    "data-src": function() {
        assert.htmlEquals(render('<img data-src="{foo}" />',
                                 {foo: 'fixtures/destroy.png'}),
                          '<img src="fixtures/destroy.png"/>');
    },

    "data-src with dynamic class": function() {
        // for some reason htmlEquals for normalized HTML compare doesn't
        // work on Chromium, so test by hand
        var el = renderEl('<img data-src="{foo}" class="{bar}" />',
                          {foo: 'fixtures/destroy.png',
                           bar: 'Bar'});
        var img_el = $('img', el);
        assert.equals(img_el.attr('src'), 'fixtures/destroy.png');
        assert(img_el.hasClass('Bar'));
    },


    'non-dynamic data-src': function() {
        assert.htmlEquals(render('<img data-src="fixtures/destroy.png" />', {}),
                          '<img src="fixtures/destroy.png" />');
    },

    'data-src and data-id case': function() {
        var template = new obtemp.Template(
            '<img data-id="{id}" data-src="fixtures/{id}.png" />');
        var el = testel();
        template.render(el, {id: 'destroy'});
        assert.equals($('#destroy', el).attr('id'), 'destroy');
        assert.equals($('#destroy', el).attr('src'), 'fixtures/destroy.png');
    },

    "data-with": function() {
        assert.htmlEquals(render('<p data-with="alpha">{beta}</p>', {alpha: { beta: "Hello"}}),
                          '<p>Hello</p>');
    },

    "data-with not pointing to object": function() {
        assert.raises(function() {
            render('<p data-with="alpha"></p>', {alpha: 'not an object'});
        }, obtemp.RenderError);
        
    },

    "data-with not pointing to anything": function() {
        assert.raises(function() {
            render('<p data-with="alpha"></p>', {});
        }, obtemp.RenderError);
        
    },

    "deeper data-with": function() {
        assert.htmlEquals(render('<div><p data-with="alpha">{beta}</p></div>',
                                 {alpha: { beta: "Hello"}}),
                          '<div><p>Hello</p></div>');
    },

    "nested data-with": function() {
        assert.htmlEquals(render('<div data-with="alpha"><div data-with="beta"><div data-with="gamma">{delta}</div></div></div>',
                                 {alpha: { beta: { gamma: { delta: "Hello"}}}}),
                          '<div><div><div>Hello</div></div></div>');
    },

    "data-with with dotted name": function() {
        assert.htmlEquals(render('<div data-with="alpha.beta.gamma">{delta}</div>',
                                 {alpha: { beta: { gamma: { delta: "Hello"}}}}),
                          '<div>Hello</div>');
    },

    "data-with with attribute": function() {
        assert.htmlEquals(render('<div data-with="alpha" class="{beta}"></div>',
                                 {alpha: { beta: 'Beta'}}),
                          '<div class="Beta"></div>');

    },

    "deeper data-with with attribute": function() {
        assert.htmlEquals(render('<div><div data-with="alpha" class="{beta}"></div></div>',
                                 {alpha: { beta: 'Beta'}}),
                          '<div><div class="Beta"></div></div>');

    },

    "data-if where if is true with dynamic class": function() {
        assert.htmlEquals(render('<div data-if="alpha" class="{foo}">{beta}</div>',
                                 {alpha: true,
                                  beta: 'Beta',
                                  foo: 'Foo'}),
                          '<div class="Foo">Beta</div>');
    },

    "data-if where if is true with dynamic class, subsection": function() {
        assert.htmlEquals(render('<div data-if="always"><div data-if="alpha" class="{foo}">{beta}</div></div>',
                                 {alpha: true,
                                  always: true,
                                  beta: 'Beta',
                                  foo: 'Foo'}),
                          '<div><div class="Foo">Beta</div></div>');
    },

    "data-if where if is true": function() {
        assert.htmlEquals(render('<div data-if="alpha">{beta}</div>',
                                 {alpha: true,
                                  beta: 'Beta'}),
                          '<div>Beta</div>');
    },

    "data-if where if is false": function() {
        assert.htmlEquals(render('<div data-if="alpha">{beta}</div>',
                                 {alpha: false,
                                  beta: 'Beta'}),
                          '');
    },

    "data-if where if is false with dynamic class": function() {
        assert.htmlEquals(render('<div data-if="alpha" class="{foo}">{beta}</div>',
                                 {alpha: false,
                                  beta: 'Beta',
                                  foo: 'Foo'}),
                          '');
    },

    
    "data-if where if is false with dynamic class, subsection": function() {
        assert.htmlEquals(render('<div data-if="always"><div data-if="alpha" class="{foo}">{beta}</div></div>',
                                 {alpha: false,
                                  always: true,
                                  beta: 'Beta',
                                  foo: 'Foo'}),
                          '<div></div>');
    },

    'data-if in data-with': function() {
        assert.htmlEquals(
            render('<div data-with="something"><p data-if="!flag">not flag</p><p data-if="flag">flag</p></div>',
                   {something: {flag: true}}),
            '<div><p>flag</p></div>');
    },

    'data-if with not (!) where data is false': function() {
        assert.htmlEquals(render('<div data-if="!alpha">{beta}</div>',
                                 {alpha: false,
                                  beta: 'Beta'}),
                          '<div>Beta</div>');
    },

    'data-if with not where data is true': function() {
        assert.htmlEquals(render('<div data-if="!alpha">{beta}</div>',
                                 {alpha: true,
                                  beta: 'Beta'}),
                          '');
    },


    'data-if with not where data is null': function() {
        assert.htmlEquals(render('<div data-if="!alpha">{beta}</div>',
                                 {alpha: null,
                                  beta: 'Beta'}),
                          '<div>Beta</div>');
    },

    'data-if with not where data is string': function() {
        assert.htmlEquals(render('<div data-if="!alpha">{beta}</div>',
                                 {alpha: 'something',
                                  beta: 'Beta'}),
                          '');
    },

    "deeper data-if where if is true": function() {
        assert.htmlEquals(render('<div><div data-if="alpha">{beta}</div></div>',
                                 {alpha: true,
                                  beta: 'Beta'}),
                          '<div><div>Beta</div></div>');
    },


    "deeper data-if where if is false": function() {
        assert.htmlEquals(render('<div><div data-if="alpha">{beta}</div></div>',
                                 {alpha: false,
                                  beta: 'Beta'}),
                          '<div></div>');
    },

    "data-if where if is null": function() {
        assert.htmlEquals(render('<div data-if="alpha">{beta}</div>',
                                 {alpha: null,
                                  beta: 'Beta'}),
                          '');
    },

    "data-if where if is undefined": function() {
        assert.htmlEquals(render('<div data-if="alpha">{beta}</div>',
                                 {alpha: undefined,
                                  beta: 'Beta'}),
                          '');
    },

    'data-if with value if defined': function() {
        // textarea has replaceable text content, can only contain text..
        assert.htmlEquals(render('<div data-el="textarea"><div data-if="width" data-attr="style" data-value="width: {width}em;" /></div>',
                                 {width: 10}),
                          '<textarea style="width: 10em;"></textarea>');
    },


    'data-if with value if not defined': function() {
        // textarea has replaceable text content, can only contain text..
        assert.htmlEquals(render('<div data-el="textarea"><div data-if="width" data-attr="style" data-value="width: {width}em;" /></div>',
                                 {}),
                          '<textarea></textarea>');
    },

    "data-if where if is 0": function() {
        assert.htmlEquals(render('<div data-if="alpha">{beta}</div>',
                                 {alpha: 0,
                                  beta: 'Beta'}),
                          '');
    },

    "data-if where if is 1": function() {
        assert.htmlEquals(render('<div data-if="alpha">{beta}</div>',
                                 {alpha: 1,
                                  beta: 'Beta'}),
                          '<div>Beta</div>');
    },

    "data-if where if is empty string": function() {
        assert.htmlEquals(render('<div data-if="alpha">{beta}</div>',
                                 {alpha: '',
                                  beta: 'Beta'}),
                          '');
    },

    "data-if where if is non-empty string": function() {
        assert.htmlEquals(render('<div data-if="alpha">{beta}</div>',
                                 {alpha: 'non empty',
                                  beta: 'Beta'}),
                          '<div>Beta</div>');
    },

    "data-if where if is empty array": function() {
        assert.htmlEquals(render('<div data-if="alpha">{beta}</div>',
                                 {alpha: [],
                                  beta: 'Beta'}),
                          '');
    },

    "data-if where if is non-empty array": function() {
        assert.htmlEquals(render('<div data-if="alpha">{beta}</div>',
                                 {alpha: ['a'],
                                  beta: 'Beta'}),
                          '<div>Beta</div>');
    },


    "data-if where if is not there": function() {
        assert.htmlEquals(render('<div data-if="alpha">{beta}</div>',
                                 {beta: 'Beta'}),
                          '');
    },

    "data-with and data-if where if is true": function() {
        assert.htmlEquals(render('<div data-if="alpha" data-with="beta">{gamma}</div>',
                                 {alpha: true,
                                  beta: {
                                      gamma: "Gamma"
                                  }}),
                          '<div>Gamma</div>');
    },


    "data-with and data-if where if is false": function() {
        assert.htmlEquals(render('<div data-if="alpha" data-with="beta">{gamma}</div>',
                                 {alpha: false,
                                  beta: {
                                      gamma: "Gamma"
                                  }}),
                          '');
    },


    'data-repeat with 3 elements': function() {
        assert.htmlEquals(render('<ul><li data-repeat="list">{title}</li></ul>',
                                 {list: [{title: 'a'},
                                         {title: 'b'},
                                         {title: 'c'}]}),
                          '<ul><li>a</li><li>b</li><li>c</li></ul>');
    },

    'top-level data each': function() {
        assert.htmlEquals(render('<p data-repeat="list">{title}</p>',
                                 {list: [{title: 'a'},
                                         {title: 'b'},
                                         {title: 'c'}]}),
                          '<p>a</p><p>b</p><p>c</p>');
    },

    'data-repeat with @.': function() {
        assert.htmlEquals(render('<p data-repeat="list">{@.}</p>',
                                 {list: ['a', 'b', 'c']}),
                          '<p>a</p><p>b</p><p>c</p>');
    },

    'data-repeat with 2 elements': function() {
        assert.htmlEquals(render('<ul><li data-repeat="list">{title}</li></ul>',
                                 {list: [{title: 'a'},
                                         {title: 'b'}]}),
                          '<ul><li>a</li><li>b</li></ul>');
    },

    'data-repeat with 1 element': function() {
        assert.htmlEquals(render('<ul><li data-repeat="list">{title}</li></ul>',
                                 {list: [{title: 'a'}]}),
                          '<ul><li>a</li></ul>');
    },

    'data-repeat with 0 elements': function() {
        assert.htmlEquals(render('<ul><li data-repeat="list">{title}</li></ul>',
                                 {list: []}),
                          '<ul></ul>');
    },

    'data-repeat, small table': function() {
        var data = { table: [] };
        for (var i = 0; i < 2; i++) {
            data.table.push([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
        }
        assert.htmlEquals(render('<table>' +
                                 '<tr data-repeat="table">' +
                                 '<td data-repeat="@.">{@.}</td>' +
                                 '</tr>' +
                                 '</table>', data),
                          '<table>' +
                          '<tbody>' +
                          '<tr><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td><td>8</td><td>9</td><td>10</td></tr>' +
                          '<tr><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td><td>8</td><td>9</td><td>10</td></tr>' +
                          '</tbody>' +
                          '</table>');
    },

    'data-repeat with deeper elements': function() {
        assert.htmlEquals(render('<ul><li data-repeat="list"><p>{title}</p></li></ul>',
                                 {list: [{title: 'a'},
                                         {title: 'b'},
                                         {title: 'c'}]}),
                          '<ul><li><p>a</p></li><li><p>b</p></li><li><p>c</p></li></ul>');
    },

    'data-repeat with some element content not rendered': function() {
        assert.htmlEquals(render(
            '<ul><li data-repeat="list"><p data-if="@.">whatever</p></li></ul>',
            {list: [true, false]}),
                          '<ul><li><p>whatever</p></li><li></li></ul>');
    },


    'data-repeat with half of element content not rendered': function() {
        assert.htmlEquals(render(
            '<ul><li data-repeat="list"><p data-if="@.">True</p><p data-if="!@.">False</p></li></ul>',
            {list: [true, false]}),
                          '<ul><li><p>True</p></li><li><p>False</p></li></ul>');
    },

    'data-repeat with attributes': function() {
        assert.htmlEquals(render('<a data-repeat="list" href="{url}">link</a>',
                                 {list: [{url: 'a'},
                                         {url: 'b'}]}),
                          '<a href="a">link</a><a href="b">link</a>');

    },

    'data-repeat with text after it': function() {
        assert.htmlEquals(render('<ul><li data-repeat="list">{title}</li>after</ul>',
                                 {list: [{title: 'a'},
                                         {title: 'b'}]}),
                          '<ul><li>a</li><li>b</li>after</ul>');
    },

    'data-repeat not pointing to array': function() {
        assert.raises(function() {
            render('<p data-repeat="foo"></p>', {foo: 'not an array'});
        }, obtemp.RenderError);
    },
    
    'data-repeat with data-if and true': function() {
        assert.htmlEquals(render('<ul><li data-if="flag" data-repeat="list">{title}</li></ul>',
                                 {flag: true,
                                  list: [{title: 'a'},
                                         {title: 'b'}]}),
                          '<ul><li>a</li><li>b</li></ul>');

    },

    'data-repeat with data-if and false': function() {
        assert.htmlEquals(render('<ul><li data-if="flag" data-repeat="list">{title}</li></ul>',
                                 {flag: false,
                                  list: [{title: 'a'},
                                         {title: 'b'}]}),
                          '<ul></ul>');

    },

    'data-repeat with data-with': function() {
        assert.htmlEquals(render('<ul><li data-repeat="list" data-with="sub">{title}</li></ul>',
                                 {list: [{sub: {title: 'a'}},
                                         {sub: {title: 'b'}}]}),
                          '<ul><li>a</li><li>b</li></ul>');
    },

    'data-repeat with data-with and data-if and true': function() {
        assert.htmlEquals(render('<ul><li data-if="flag" data-repeat="list" data-with="sub">{title}</li></ul>',
                                 {flag: true,
                                  list: [{sub: {title: 'a'}},
                                         {sub: {title: 'b'}}]}),
                          '<ul><li>a</li><li>b</li></ul>');
    },

    'data-repeat with data-with and data-if and false': function() {
        assert.htmlEquals(render('<ul><li data-if="flag" data-repeat="list" data-with="sub">{title}</li></ul>',
                                 {flag: false,
                                  list: [{sub: {title: 'a'}},
                                         {sub: {title: 'b'}}]}),
                          '<ul></ul>');
    },

    'data-repeat with data-trans': function() {
        assert.htmlEquals(render(
            '<ul><li data-repeat="list" data-trans="">Hello world!</li></ul>',
            {list: [1, 2]}),
                          '<ul><li>Hallo wereld!</li><li>Hallo wereld!</li></ul>');
    },


    'nested data-repeat': function() {
        assert.htmlEquals(render(
            '<ul><li data-repeat="outer"><ul><li data-repeat="inner">{title}</li></ul></li></ul>',
            {outer: [
                {inner: [{title: 'a'}, {title: 'b'}]},
                {inner: [{title: 'c'}, {title: 'd'}]}
            ]}),
                          '<ul><li><ul><li>a</li><li>b</li></ul></li><li><ul><li>c</li><li>d</li></ul></li></ul>');
        
    },

    'data-repeat with @repeat vars': function() {
        assert.htmlEquals(render(
            '<ul><li data-repeat="list">{@repeat.index} {@repeat.length}</li></ul>',
            {list: [1, 2]}),
                          '<ul><li>0 2</li><li>1 2</li></ul>');
    },
    
    'data-repeat first': function() {
        assert.htmlEquals(render(
            '<ul><li data-repeat="list">{@repeat.first}</li></ul>',
            {list: [1, 2]}),
                          '<ul><li>true</li><li>false</li></ul>');
    },

    'data-repeat last': function() {
        assert.htmlEquals(render(
            '<ul><li data-repeat="list">{@repeat.last}</li></ul>',
            {list: [1, 2]}),
                          '<ul><li>false</li><li>true</li></ul>');
    },

    'data-repeat with @repeat vars, explicit loop': function() {
        assert.htmlEquals(render(
            '<ul><li data-repeat="list">{@repeat.list.index} {@repeat.list.length}</li></ul>',
            {list: [1, 2]}),
                          '<ul><li>0 2</li><li>1 2</li></ul>');
    },

    'data-repeat with @repeat vars, nested loop': function() {
        assert.htmlEquals(render(
            '<ul><li data-repeat="outer"><ul><li data-repeat="inner">{@repeat.inner.index} {@repeat.outer.index}</li></ul></li></ul>',
            {outer: [
                {inner: [{title: 'a'}, {title: 'b'}]},
                {inner: [{title: 'c'}]}
            ]}),
                          '<ul><li><ul><li>0 0</li><li>1 0</li></ul></li><li><ul><li>0 1</li></ul></li></ul>'
                         );
    },

    'data-repeat with @repeat vars using number': function() {
        assert.htmlEquals(render(
            '<ul><li data-repeat="list">{@repeat.number}</li></ul>',
            {list: ['a', 'b']}),
                          '<ul><li>1</li><li>2</li></ul>');
    },

    'data-repeat with @repeat vars using even/odd': function() {
        assert.htmlEquals(render(
            '<ul><li data-repeat="list"><p data-if="@repeat.even">Even</p><p data-if="@repeat.odd">Odd</p></li></ul>',
            {list: ['a', 'b']}),
                          '<ul><li><p>Even</p></li><li><p>Odd</p></li></ul>');
    },

    'data-repeat with @repeat vars with dotted name': function() {
        assert.htmlEquals(render(
            '<ul><li data-repeat="sub.list">{@repeat.sub_list.number}</li></ul>',
            {sub: {list: ['a', 'b']}}),
                          '<ul><li>1</li><li>2</li></ul>');
    },

    'data-call': function() {
        obtemp.registerFunc('addattr', function(el) {
            el.attr('magic', "Magic!");
        });
        
        assert.htmlEquals(render(
            '<p data-call="addattr">Hello world!</p>', {}),
                          '<p magic="Magic!">Hello world!</p>');
        
    },

    'data-call with variable': function() {
        obtemp.registerFunc('addattr', function(el, variable) {
            el.attr('magic', variable('foo'));
        });
        
        assert.htmlEquals(render(
            '<p data-call="addattr">Hello world!</p>', {foo: "Foo!"}),
                          '<p magic="Foo!">Hello world!</p>');
        
    },

    'data-call with data-with': function() {
        obtemp.registerFunc('addattr', function(el, variable) {
            el.attr('magic', variable('foo'));
        });
        
        assert.htmlEquals(render(
            '<p data-with="sub" data-call="addattr">Hello world!</p>',
            {sub: {foo: "Foo!"}}),
                          '<p magic="Foo!">Hello world!</p>');

    },

    'data-call with data-if where if is true': function() {
        obtemp.registerFunc('addattr', function(el, variable) {
            el.attr('magic', variable('foo'));
        });
        
        assert.htmlEquals(render(
            '<p data-if="flag" data-call="addattr">Hello world!</p>',
            {foo: "Foo!", flag: true}),
                          '<p magic="Foo!">Hello world!</p>');
    },


    'data-call with data-if where if is false': function() {
        obtemp.registerFunc('addattr', function(el, variable) {
            el.attr('magic', variable('foo'));
        });
        
        assert.htmlEquals(render(
            '<p data-if="flag" data-call="addattr">Hello world!</p>',
            {foo: "Foo!", flag: false}),
                          '');
    },

    'data-call with data-trans': function() {
        obtemp.registerFunc('addattr', function(el, variable) {
            el.attr('magic', variable('foo'));
            // translation has happened before data-call is called
            assert.equals(el.text(), 'Hallo wereld!');
        });
        
        assert.htmlEquals(render(
            '<p data-trans="" data-call="addattr">Hello world!</p>',
            {foo: "Foo!"}),
                          '<p magic="Foo!">Hallo wereld!</p>');
    },

    'data-call with data-repeat': function() {
        obtemp.registerFunc('even-odd', function(el, variable) {
            if (variable('@repeat.index') % 2 === 0) {
                el.addClass('even');
            } else {
                el.addClass('odd');
            }
        });
        
        assert.htmlEquals(render(
            '<p data-repeat="list" data-call="even-odd">{@.}</p>',
            {list: [0, 1, 2, 3]}),
                          '<p class="even">0</p><p class="odd">1</p><p class="even">2</p><p class="odd">3</p>'
                         );
    },


    'data-call where func is missing': function() {
        assert.raises(function() {
            render('<p data-trans="" data-call="addattr">Hello world!</p>',
                   {foo: "Foo!"});
        }, obtemp.RenderError);
    },

    "data-trans with plain text, translation found": function() {
        assert.htmlEquals(render('<p data-trans="">Hello world!</p>', {}),
                          '<p>Hallo wereld!</p>');
    },

    'data-trans with text, translation not there': function() {
        assert.htmlEquals(render('<p data-trans="">This is not translated</p>', {}),
                          '<p>This is not translated</p>');
    },

    'data-trans with whitespace in element content, translation found': function() {
        assert.htmlEquals(render('<p data-trans="">  This has \n  whitespace.  </p>', {}),
                          '<p>Dit heeft witruimte.</p>');
    },

    'data-tvar with whitespace, translation found': function() {
        // IE 8 and earlier "helpfully" collapse whitespace in text nodes.
        // this is why there is no space between </em> and "is there" in this
        // test; this whitespace is eliminated in IE. since it's not what
        // we're testing (we're testing a tvar) we leave it out so the test
        // passes in IE too
        assert.htmlEquals(render('<p data-trans=""><em data-tvar="something">  This has \n  whitespace.  </em>is there</p>', {}),
                          '<p><em>Dit heeft witruimte.</em>is there</p>');
    },

    'attribute with whitespace, translation not found': function() {
        // attributes do take whitespace literally, so translation won't be
        // found as we look up "  This has \n  whitespace.  " up literally
        assert.htmlEquals(render('<p data-trans="title" title="  This has \n  whitespace.  "></p>', {}),
                          '<p title="  This has \n  whitespace.  "></p>');
    },

    'data-trans with whitespace in element content, not translated': function() {
        assert.htmlEquals(render('<p data-trans="">  This also has \n  whitespace.  </p>', {}),
                          '<p>  This also has \n  whitespace.  </p>');
    },

    'data-trans with text and msgid, translation not there': function() {
        assert.htmlEquals(render('<p data-trans=":foo">This is not translated</p>', {}),
                          '<p>This is not translated</p>');
    },

    'data-trans with text and msgid for attr, translation not there': function() {
        assert.htmlEquals(render('<p data-trans="title:foo" title="This is not translated"></p>', {}),
                          '<p title="This is not translated"></p>');
    },

    "data-trans with text & entity reference": function() {
        assert.htmlEquals(render('<p data-trans="">one &lt; two</p>', {}),
                          '<p>een &lt; twee</p>');
    },

    "data-trans with text & comment": function() {
        assert.htmlEquals(render('<p data-trans="">Hello world!<!-- comment -->', {}),
                          '<p>Hallo wereld!</p>');
    },

    "data-trans with text & comment and element": function() {
        assert.htmlEquals(render('<p data-trans=""><!-- comment -->Hello <!-- comment --><em data-tvar="who">{who}</em>!</p>',
                                 {who: "Bob"}),
                          '<p><em>Bob</em>, hallo!</p>');
    },

    // CDATA is too different in browsers and not really sensible to support
    // see also CDATASection in HTML for more info:
    // http://reference.sitepoint.com/javascript/CDATASection
    // "data-trans with text & CDATA section": function() {
    //     assert.htmlEquals(render('<p data-trans=""><![CDATA[Hello world!]]></p>', {}),
    //           '<p>Hallo wereld!</p>');
    // });


    "data-trans with variable": function() {
        assert.htmlEquals(render('<p data-trans="">Hello {who}!</p>', {who: "Fred"}),
                          '<p>Fred, hallo!</p>');
    },

    'data-trans with variable and formatter': function() {
        obtemp.registerFormatter('upper', function(value) {
            return value.toUpperCase();
        });
        assert.htmlEquals(render('<p data-trans="">Hello {who|upper}!</p>', {who: "Fred"}),
                          '<p>FRED, hallo!</p>');
    },

    'data-trans with attribute and formatter': function() {
        obtemp.registerFormatter('upper', function(value) {
            return value.toUpperCase();
        });
        assert.htmlEquals(render('<p data-trans="title" title="Hello {who|upper}!"></p>',
                                 {who: "Fred"}),
                          '<p title="FRED, hallo!"></p>');

    },

    'data-trans with multiple variables and different formatter': function() {
        obtemp.registerFormatter('upper', function(value) {
            return value.toUpperCase();
        });
        obtemp.registerFormatter('lower', function(value) {
            return value.toLowerCase();
        });


        assert.raises(function() {
            render('<p data-trans="">Hello {who|upper}! ({who|lower}?)</p>',
                   {who: "Fred"});
        }, obtemp.CompilationError);
    },


    'data-trans on attr with multiple variables and different formatter': function() {
        obtemp.registerFormatter('upper', function(value) {
            return value.toUpperCase();
        });
        obtemp.registerFormatter('lower', function(value) {
            return value.toLowerCase();
        });


        assert.raises(function() {
            render('<p data-trans="title" title="Hello {who|upper}! ({who|lower}?)"></p>',
                   {who: "Fred"});
        }, obtemp.CompilationError);
    },


    'data-trans with multiple variables and same formatter': function() {
        obtemp.registerFormatter('upper', function(value) {
            return value.toUpperCase();
        });
        
        assert.htmlEquals(
            render('<p data-trans="">Hello {who|upper}! ({who|upper}?)</p>',
                   {who: "Fred"}),
            '<p>FRED, hallo! (FRED?)</p>');
    },


    'data-trans on attr with multiple variables and same formatter': function() {
        obtemp.registerFormatter('upper', function(value) {
            return value.toUpperCase();
        });
        
        assert.htmlEquals(
            render('<p data-trans="title" title="Hello {who|upper}! ({who|upper}?)"></p>',
                   {who: "Fred"}),
            '<p title="FRED, hallo! (FRED?)"></p>');
    },

    'data-trans on empty attribute': function() {
        assert.raises(function() {
            render('<p data-trans="title" title=""></p>');
        }, obtemp.CompilationError);
    },

    'data-trans on attribute with just variable': function() {
        assert.raises(function() {
            render('<p data-trans="title" title="{foo}"></p>', {foo: 'Foo'});
        }, obtemp.CompilationError);
    },


    'data-trans with implicit tvar with formatter': function() {
        obtemp.registerFormatter('upper', function(value) {
            return value.toUpperCase();
        });
        
        assert.htmlEquals(
            render('<p data-trans="">Hello <em>{who|upper}</em>!</p>',
                   {who: "Fred"}),
            '<p><em>FRED</em>, hallo!</p>');
    },

    'data-trans with view based tvar with name': function() {
        obviel.view({
            iface: 'person',
            name: 'summary',
            render: function() {
                this.el.text('the ' + this.obj.name);
            }
        });
        assert.htmlEquals(render('<p data-trans="">Hello <em data-render="who|summary" />!</p>',
                                 {who: {iface: 'person', name: 'Fred'}}),
                          '<p><em>the Fred</em>, hallo!</p>');
    },

    'data-trans with data-tvar': function() {
        assert.htmlEquals(render('<p data-trans="">Hello <em data-tvar="who">world</em>!</p>',
                                 {}),
                          '<p><em>world</em>, hallo!</p>');
    },

    'data-trans with data-tvar and variable in tvar': function() {
        assert.htmlEquals(render('<p data-trans="">Hello <em data-tvar="who">{who}</em>!</p>',
                                 {who: 'wereld'}),
                          '<p><em>wereld</em>, hallo!</p>');
    },


    'implicit data-tvar for variable in element': function() {
        assert.htmlEquals(render('<p data-trans="">Hello <em>{who}</em>!</p>',
                                 {who: 'wereld'}),
                          '<p><em>wereld</em>, hallo!</p>');
    },

    'implicit data-tvar for variable in element when no translation available': function() {
        assert.htmlEquals(render('<p data-trans="">Greetings <em>{who}</em>!</p>',
                                 {who: 'wereld'}),
                          '<p>Greetings <em>wereld</em>!</p>');
    },

    'data-tvar for variable in element when no translations are available': function() {
            var text = '<p data-trans="">Greetings <em data-tvar="who">{who}</em>!</p>';
        var template = new obtemp.Template(text);
        var el = $("<div></div>");
        template.render(el, {who: 'wereld'}, {});
        var html = el.html();

        assert.htmlEquals(html, '<p>Greetings <em>wereld</em>!</p>');
    },

    'implicit data-tvar for data-render': function() {
        obviel.view({
            iface: 'person',
            render: function() {
                this.el.append('<em>' + this.obj.name + '</em>');
            }
        });

        assert.htmlEquals(render('<p data-trans="">Hello <span data-render="who"></span>!</p>',
                                 {who: {iface: 'person', name: 'Bob'}}),
                          '<p><span><em>Bob</em></span>, hallo!</p>');
    },


    'implicit data-tvar not allowed for empty sub-element': function() {
        assert.raises(function() {
            render('<p data-trans="">Hello <em></em>!</p>',
                   {});
        }, obtemp.CompilationError);
    },

    'data-trans with data-tvar and variable in text': function() {
        assert.htmlEquals(render('<p data-trans="">Hello {qualifier} <em data-tvar="who">{who}</em>!</p>',
                                 {who: 'wereld',
                                  qualifier: 'beste'}),
                          '<p>beste <em>wereld</em>, hallo!</p>');
        
    },

    'data-trans with multiple data-tvars': function() {
        assert.htmlEquals(render('<p data-trans="">Hello <strong data-tvar="qualifier">{qualifier}</strong> <em data-tvar="who">{who}</em>!</p>',
                                 {who: 'wereld',
                                  qualifier: 'beste'}),
                          '<p><strong>beste</strong> <em>wereld</em>, hallo!</p>');

    },

    'data-trans may not contain data-if': function() {
        assert.raises(function() {
            render('<p data-trans="">Hello <strong data-tvar="who" data-if="flag">{who}</strong>!',
                   {who: 'X', flag: true});
        }, obtemp.CompilationError);
    },

    'data-trans may not contain data-with': function() {
        assert.raises(function() {
            render('<p data-trans="">Hello <strong data-tvar="who" data-with="something">{who}</strong>!',
                   {something: {who: 'X'}});
        }, obtemp.CompilationError);
    },


    'data-trans may not contain data-repeat': function() {
        assert.raises(function() {
            render('<p data-trans="">Hello <strong data-tvar="who" data-repeat="a">{who}</strong>!',
                   {who: 'X', a: []});
        }, obtemp.CompilationError);
    },

    'data-tvar may not contain data-if': function() {
        assert.raises(function() {
            render('<p data-trans="">Hello <strong data-tvar="who">blah<em data-tvar="nested" data-if="flag">{who}</em></strong>!',
                   {who: 'X', flag: true});
        }, obtemp.CompilationError);
    },

    'data-tvar may not contain data-with': function() {
        assert.raises(function() {
            render('<p data-trans="">Hello <strong data-tvar="who">blah<em data-tvar="nested" data-with="something">{who}</em></strong>!',
                   {something: {who: 'X'}});
        }, obtemp.CompilationError);
    },


    'data-tvar may not contain data-repeat': function() {
        assert.raises(function() {
            render('<p data-trans="">Hello <strong data-tvar="who">blah<em data-tvar="nested" data-repeat="a">{who}</em></strong>!',
                   {who: 'X', a: []});
        }, obtemp.CompilationError);
    },

    'data-trans may contain data-id': function() {
        assert.htmlEquals(
            render('<p data-trans="">Hello <strong data-id="{myId}" data-tvar="who">{who}</strong>!</p>',
                   {who: 'X', myId: 'foo'}),
            '<p><strong id="foo">X</strong>, hallo!</p>');
    },

    'data-trans with just variable, no text': function() {
        assert.raises(function() {
            render('<p data-trans="">{hello}</p>', {hello: 'Hello!'});
        }, obtemp.CompilationError);
    },

    'data-trans used on whitespace': function() {
        assert.raises(function() {
            render('<p data-trans="">   </p>');
        }, obtemp.CompilationError);
        
    },

    'data-trans without text altogether': function() {
        assert.raises(function() {
            render('<p data-trans=""></p>');
        }, obtemp.CompilationError);
        
    },


    'data-trans with just a single data-tvar': function() {
        assert.raises(function() {
            render('<p data-trans=""><em data-tvar="something"></em></p>');
        }, obtemp.CompilationError);
    },

    'data-trans on attribute with plain text': function() {
        assert.htmlEquals(render(
            '<p data-trans="title" title="Hello world!">Hello world!</p>', {}),
                          '<p title="Hallo wereld!">Hello world!</p>');
    },


    'data-trans on attribute with variable': function() {
        assert.htmlEquals(render(
            '<p data-trans="title" title="Hello {who}!">Hello world!</p>',
            {who: 'X'}),
                          '<p title="X, hallo!">Hello world!</p>');
    },

    'data-trans on text and attribute': function() {
        assert.htmlEquals(render(
            '<p data-trans=". title" title="Hello world!">Hello world!</p>', {}),
                          '<p title="Hallo wereld!">Hallo wereld!</p>');
    },

    'data-trans without translation available but with tvar': function() {
        assert.htmlEquals(render('<p data-trans="">Hey there <em data-tvar="who">{who}</em>!</p>',
                                 {who: 'pardner'}),
                          '<p>Hey there <em>pardner</em>!</p>');
    },

    'data-trans with translated tvar with variable': function() {
        assert.htmlEquals(render('<p data-trans="">Their message was: "<em data-tvar="message">Hello {who}!</em>".</p>',
                                 {who: 'X'}),
                          '<p>Hun boodschap was: "<em>X, hallo!</em>".</p>');
    },

    'data-trans with translated tvar without variable': function() {
        assert.htmlEquals(render('<p data-trans="">Their message was: "<em data-tvar="message">Hello world!</em>".</p>',
                                 {}),
                          '<p>Hun boodschap was: "<em>Hallo wereld!</em>".</p>');
    },

    'data-trans with tvar with tvar in it': function() {
        assert.htmlEquals(render('<p data-trans="">Their message was: "<em data-tvar="message">Hello <strong data-tvar="who">{name}</strong>!</em>".</p>',
                                 {name: 'X'}),
                          '<p>Hun boodschap was: "<em><strong>X</strong>, hallo!</em>".</p>');
    },


    'data-trans with data-tvar with data-trans on it for attribute': function() {
        assert.htmlEquals(render('<p data-trans="">Hello <em title="Hello world!" data-trans="title" data-tvar="who">{who}</em>!</p>',
                                 {who: 'X'}),
                          '<p><em title="Hallo wereld!">X</em>, hallo!</p>');
    },

    'data-trans with data-tvar with data-trans on it indicating same content not allowed': function() {
        assert.raises(function() {
            render('<p data-trans="">Hello <em data-trans="" data-tvar="who">{who}</em>!</p>',
                   {who: 'X'});
        }, obtemp.CompilationError);
    },

    'data-trans with data-tvar with data-trans on it indicating same content not allowed 2': function() {
        assert.raises(function() {
            render('<p data-trans="">Hello <em data-trans="." data-tvar="who">{who}</em>!</p>',
                   {who: 'X'});
        }, obtemp.CompilationError);
    },

    'data-trans with non-unique tvar': function() {
        assert.raises(function() {
            render('<p data-trans=""><em data-tvar="message">msg</em><strong data-tvar="message">msg</strong></p>',
                   {});
        }, obtemp.CompilationError);
    },

    'data-trans with non-unique tvar, matches variable': function() {
        assert.raises(function() {
            render('<p data-trans=""><em data-tvar="message">msg</em>{message}</p>',
                   {message: 'X'});
        }, obtemp.CompilationError);
    },

    'data-trans with non-unique tvar, matches variable other way around': function() {
        assert.raises(function() {
            render('<p data-trans="">{message}<em data-tvar="message">msg</em></p>',
                   {message: 'X'});
        }, obtemp.CompilationError);
    },

    'data-trans with multiple variables of same name is allowed': function() {
        assert.htmlEquals(render('<p data-trans="">{message} or {message}</p>',
                                 {message: 'X'}),
                          '<p>X or X</p>');
    },


    // empty data-tvar element is allowed
    'data-trans with empty tvar': function() {
        assert.htmlEquals(render('<p data-trans="">Hello!<br data-tvar="break"/>Bye!</p>',
                                 {}),
                          '<p>Hallo!<br/>Tot ziens!</p>');
    },



    'data-trans with explicit message id for text content': function() {
        assert.htmlEquals(render('<p data-trans=":explicit">test</p>', {}),
                          '<p>explicit translated</p>');
    },

    'data-trans with explicit message id for text content 2': function() {
        assert.htmlEquals(render('<p data-trans=".:explicit">test</p>', {}),
                          '<p>explicit translated</p>');
    },

    'data-trans with explicit message id for attribute': function() {
        assert.htmlEquals(render('<p data-trans="title:explicit" title="test">test</p>', {}),
                          '<p title="explicit translated">test</p>');

    },

    'data-trans with explicit message id for attribute and text': function() {
        assert.htmlEquals(render('<p data-trans=".:explicit title:explicit" title="test">test</p>', {}),
                          '<p title="explicit translated">explicit translated</p>');

    },


    'data-tvar with explicit message id': function() {
        assert.htmlEquals(render(
            '<p data-trans="">Hello <em data-tvar="who:explicitWho">great {who}</em>!</p>',
            {who: 'maker'}),
                          '<p><em>grote maker</em>, hallo!</p>');

    },

    'included html is escaped': function() {
        assert.htmlEquals(render('<p>{html}</p>', {html: '<em>test</em>'}),
                          '<p>&lt;em&gt;test&lt;/em&gt;</p>');
    },

    'data-render by itself': function() {
        obviel.view({
            iface: 'person',
            render: function() {
                this.el.append('<p>' + this.obj.name + '</p>');
            }
        });

        assert.htmlEquals(render('<div data-render="bob"></div>', {bob: {iface: 'person',
                                                                       name: 'Bob'}}),
                          '<div><p>Bob</p></div>');
    },

    'data-render to url instead of obj': function(done) {
        obviel.view({
            iface: 'person',
            render: function() {
                this.el.append('<p>' + this.obj.name + '</p>');
            }
        });

        this.server.respondWith("GET", "bob_url",
                                [200, {"Content-Type": "application/json"},
                                 '{"iface": "person", "name": "Bob"}']);
        
        var template = new obtemp.Template('<div data-render="bob"></div>');
        var el = $("<div></div>");
        
        template.render(el,  {bob: 'bob_url'}).done(function() {
            assert.htmlEquals(el.html(), '<div><p>Bob</p></div>');
            done();
        });
    
    },
    
    'data-render with named view': function() {
        obviel.view({
            iface: 'person',
            name: 'summary',
            render: function() {
                this.el.append('<p>' + this.obj.name + '</p>');
            }
        });

        assert.htmlEquals(render('<div data-render="bob|summary"></div>', {bob: {iface: 'person',
                                                                               name: 'Bob'}}),
                          '<div><p>Bob</p></div>');

    },

    'data-render with for @. with named view': function() {
        obviel.view({
            iface: 'person',
            name: 'summary',
            render: function() {
                this.el.append('<p>' + this.obj.name + '</p>');
            }
        });

        assert.htmlEquals(render('<div data-render="@.|summary"></div>',
                                  {iface: 'person',
                                  name: 'Bob'}),
        '<div><p>Bob</p></div>');
    },

    // XXX check this with data-trans system as well, using data-tvar?


    'data-render with altered default view': function() {
        obviel.view({
            iface: 'person',
            name: 'summary',
            render: function() {
                this.el.append('<p>' + this.obj.name + '</p>');
            }
        });

        obtemp.setDefaultViewName('summary');
        
        assert.htmlEquals(render('<div data-render="bob"></div>', {bob: {iface: 'person',
                                                                       name: 'Bob'}}),
                          '<div><p>Bob</p></div>');

    },

    'data-render empties element': function() {
        obviel.view({
            iface: 'person',
            render: function() {
                this.el.append('<p>' + this.obj.name + '</p>');
            }
        });
        
        assert.htmlEquals(render('<div data-render="bob"><div>Something</div></div>',
                                 {bob: {iface: 'person',
                                        name: 'Bob'}}),
                          '<div><p>Bob</p></div>');

    },

    'data-render must point to object or string': function() {
        obviel.view({
            iface: 'person',
            render: function() {
                this.el.append('<p>' + this.obj.name + '</p>');
            }
        });

        assert.raises(function() {
            render('<div data-render="bob"></div>', {bob: 1});
        }, obtemp.RenderError);
    },

    'data-render cannot find view for object': function() {
        assert.raises(function() {
            render('<div data-render="bob"></div>', {bob: {iface: 'person'}});
        }, obtemp.RenderError);
    },

    'data-render with data-with': function() {
        obviel.view({
            iface: 'person',
            render: function() {
                this.el.empty();
                this.el.append('<p>' + this.obj.name + '</p>');
            }
        });
        assert.htmlEquals(render('<div data-with="sub" data-render="person">person</div>',
                                 {sub: {person: {iface: 'person',
                                                 name: 'Bob'}}}),
                          '<div><p>Bob</p></div>');
    },

    'deeper data-render with data-with': function() {
        obviel.view({
            iface: 'person',
            render: function() {
                this.el.empty();
                this.el.append('<p>' + this.obj.name + '</p>');
            }
        });
        assert.htmlEquals(render('<div><div data-with="sub" data-render="person">person</div></div>',
                                 {sub: {person: {iface: 'person',
                                                 name: 'Bob'}}}),
                          '<div><div><p>Bob</p></div></div>');
    },

    'data-render with data-if where if is true': function() {
        obviel.view({
            iface: 'person',
            render: function() {
                this.el.empty();
                this.el.append('<p>' + this.obj.name + '</p>');
            }
        });
        
        
        assert.htmlEquals(render('<div data-if="flag" data-render="person">person</div>',
                                 {person: {iface: 'person',
                                           name: 'Bob'},
                                  flag: true}),
                          '<div><p>Bob</p></div>');
        
    },

    'data-render with deeper data-if where if is false': function() {
        obviel.view({
            iface: 'person',
            render: function() {
                this.el.empty();
                this.el.append('<p>' + this.obj.name + '</p>');
            }
        });
        

        assert.htmlEquals(render('<div><div data-if="flag" data-render="person"></div></div>',
                                 {person: {iface: 'person',
                                           name: 'Bob'},
                                  flag: false}),
                          '<div></div>');

    },

    'data-render with data-repeat': function() {
        obviel.view({
            iface: 'person',
            render: function() {
                this.el.empty();
                this.el.append('<p>' + this.obj.name + '</p>');
            }
        });
        
        assert.htmlEquals(render('<div data-repeat="persons" data-render="@."></div>',
                                 {persons: [
                                     {iface: 'person',
                                      name: 'Bob'},
                                     {iface: 'person',
                                      name: 'Jay'},
                                     {iface: 'person',
                                      name: 'Stephen'}]}),
                          '<div><p>Bob</p></div><div><p>Jay</p></div><div><p>Stephen</p></div>');
        
    },


    'deeper data-render with data-repeat': function() {
        obviel.view({
            iface: 'person',
            render: function() {
                this.el.empty();
                this.el.append('<p>' + this.obj.name + '</p>');
            }
        });
        
        assert.htmlEquals(render('<div><div data-repeat="persons" data-render="@."></div></div>',
                                 {persons: [
                                     {iface: 'person',
                                      name: 'Bob'},
                                     {iface: 'person',
                                      name: 'Jay'},
                                     {iface: 'person',
                                      name: 'Stephen'}]}),
                          '<div><div><p>Bob</p></div><div><p>Jay</p></div><div><p>Stephen</p></div></div>');
        
    },

    'data-render with data-trans on same element is not allowed': function() {
        assert.raises(function() {
            render('<div data-render="foo" data-trans="">foo</div>', {});
        }, obtemp.CompilationError);
    },

    'data-render with data-trans on same element for attributes is allowed': function() {
        obviel.view({
            iface: 'person',
            render: function() {
                this.el.empty();
                this.el.append('<p>' + this.obj.name + '</p>');
            }
        });

        assert.htmlEquals(
            render('<div data-render="foo" data-trans="title" title="Hello world!">foo</div>',
                   {foo: {iface: 'person', name: 'Bob'}}),
            '<div title="Hallo wereld!"><p>Bob</p></div>');
    },

    'data-render with data-tvar is allowed': function() {
        obviel.view({
            iface: 'person',
            render: function() {
                this.el.append('<strong>' + this.obj.name + '</strong>');
            }
        });

        assert.htmlEquals(
            render('<div data-trans="">Hello <span data-tvar="who" data-render="foo"></span>!</div>',
                   {foo: {iface: 'person', name: 'Bob'}}),
            '<div><span><strong>Bob</strong></span>, hallo!</div>');
    },

    'data-tvar must be within data-trans or data-tvar': function() {
        assert.raises(function() {
            render('<div data-tvar="foo">Blah</div>');
        }, obtemp.CompilationError);
    },

    'data-trans with data-with': function() {
        assert.htmlEquals(render('<div data-with="foo" data-trans="">Hello {who}!</div>',
                                 {foo: {who: "X"}}),
                          '<div>X, hallo!</div>');
        
    },

    'data-trans with data-if where if is true': function() {
        assert.htmlEquals(render('<div data-if="flag" data-trans="">Hello {who}!</div>',
                                 {flag: true, who: "X"}),
                          '<div>X, hallo!</div>');
        
    },

    'data-trans with data-if where if is false': function() {
        assert.htmlEquals(render('<div data-if="flag" data-trans="">Hello {who}!</div>',
                                 {flag: false, who: "X"}),
                          '');
        
    },

    'data-trans with data-repeat': function() {
        assert.htmlEquals(render('<div data-repeat="entries" data-trans="">Hello {who}!</div>',
                                 {entries: [{who: 'Bob'}, {who: 'Jay'}]}),
                          '<div>Bob, hallo!</div><div>Jay, hallo!</div>');
    },

    "data-el by itself": function() {
        assert.htmlEquals(render('<div data-el="{name}" class="foo">Content</div>',
                                 {name: 'p'}),
                          '<p class="foo">Content</p>');
    },
    
    "data-el with dynamic class": function() {
        assert.htmlEquals(render('<div data-el="{name}" class="{foo}">Content</div>',
                                 {name: 'p', foo: 'Hello world'}),
                          '<p class="Hello world">Content</p>');
    },


    'data-el without element name is an error': function() {
        assert.raises(function() {
            render('<div data-el="">content</div>');
        }, obtemp.CompilationError);
    },

    "deeper data-el": function() {
        assert.htmlEquals(render('<div><div data-el="{name}" class="foo">Content</div></div>',
                                 {name: 'span'}),
                          '<div><span class="foo">Content</span></div>');
    },

    'deeper data-el with data-if and dynamic content where flag is true': function() {
        assert.htmlEquals(render('<div><div data-el="{name}" class="foo" data-if="flag"><em>{content}</em></div></div>',
                                 {name: 'span', content: "Hello world", flag: true}),
                          '<div><span class="foo"><em>Hello world</em></span></div>');
    },

    'deeper data-el with data-if and dynamic content where flag is false': function() {
        assert.htmlEquals(render('<div><div data-el="{name}" class="foo" data-if="flag"><em>{content}</em></div></div>',
                                 {name: 'span', content: "Hello world", flag: false}),
                          '<div></div>');
    },

    "data-el with data-repeat": function() {
        assert.htmlEquals(render('<div data-el="{@.}" data-repeat="list">Content</div>',
                                 {list: ['p', 'span']}),
                          '<p>Content</p><span>Content</span>');
    },

    'data-attr: dynamically generated attribute': function() {
        assert.htmlEquals(render('<p><span data-attr="class" data-value="foo"/>Hello world!</p>',
                                 {}),
                          '<p class="foo">Hello world!</p>');
    },


    'data-attr with data-if where if is true': function() {
        assert.htmlEquals(render('<p><span data-attr="{name}" data-if="flag" data-value="{value}"/>Hello world!</p>',
                                 {flag: true, name: 'class', value: 'foo'}),
                          '<p class="foo">Hello world!</p>');
    },

    'data-attr with data-if where if is false': function() {
        assert.htmlEquals(render('<p><span data-attr="{name}" data-if="flag" data-value="{value}"/>Hello world!</p>',
                                 {flag: false, name: 'class', value: 'foo'}),
                          '<p>Hello world!</p>');
    },

    'data-attr in section': function() {
        assert.htmlEquals(render('<p data-if="flag"><span data-attr="class" data-value="foo"/>Hello world!</p>',
                                 {flag: true}),
                          '<p class="foo">Hello world!</p>');
        
    },

    'data-attr in section where data-if is false': function() {
        assert.htmlEquals(render('<p data-if="flag"><span data-attr="class" data-value="foo"/>Hello world!</p>',
                                 {flag: false}),
                          '');
        
    },

// XXX these don't work anymore, but they reach outside of the template anyway,
// so perhaps they should not work

// 'data-attr on top, single element template': function() {
//     var text = '<div data-attr="class" data-value="bar"/>';
//     var template = new obtemp.Template(text);
//     var el = $("<div></div>");
//     template.render(el, {}, {});
//     assert.htmlEquals(el.html(), '');
//     assert.equals(el.attr('class'), 'bar');
// });

// 'data-attr on top, multi element template': function() {
//     var text = '<div data-attr="class" data-value="bar"/><div>Another</div>';
//     var template = new obtemp.Template(text);
//     var el = $("<div></div>");
//     template.render(el, {}, {});
//     assert.htmlEquals(el.html(), '<div>Another</div>');
//     assert.equals(el.attr('class'), 'bar');
// });

// 'data-attr on top with text following': function() {
//     var text = '<div data-attr="class" data-value="bar"/>More';
//     var template = new obtemp.Template(text);
//     var el = $("<div></div>");
//     template.render(el, {}, {});
//     assert.htmlEquals(el.html(), 'More');
//     assert.equals(el.attr('class'), 'bar');
// });


    'data-attr in data-repeat': function() {
        assert.htmlEquals(render('<ul><li data-repeat="list"><span data-if="@repeat.even" data-attr="class" data-value="even" /><span data-if="@repeat.odd" data-attr="class" data-value="odd" /><p>{@.}</p></li></ul>',
                                 {list: ['a', 'b']}),
                          '<ul><li class="even"><p>a</p></li><li class="odd"><p>b</p></li></ul>');
    },


    'data-attr multiple times for classs': function() {
        assert.htmlEquals(render('<p><span data-attr="class" data-value="a" /><span data-attr="class" data-value="b" /></p>', {}),
                          '<p class="a b"></p>');
    },

// XXX setting style multiple times in IE is fubar, even when using
// jQuery to do the thing. a single time does work..
// 'dynamically generated attribute multiple times for style': function() {
//     var text = '<div><span data-attr="style" data-value="width: 15em;" /><span data-attr="style" data-value="height: 16em;" /></div>';
//     // var template = new obtemp.Template(text);
//     var el = $("<div></div>");
//     el.attr('style', 'width: 50em;');
//     //el.attr('style', el.attr('style') + ' height: 40em;');
    
//     assert.equals(el.attr('style'), 'foo');
//     // // template.render(el, {});
//     // // assert.equals(el.get(0).childNodes[0].style, 'foo');
    
    
//    // assert.htmlEquals(render(text, {}),
//    //           '<div style="width: 15em; height: 16em;"></div>');
// });

    'data-attr without data-value is an error': function() {
        assert.raises(function() {
            render('<div data-attr="name" />');
        }, obtemp.CompilationError);
    },

    'data-attr in void element': function() {
        assert.htmlEquals(
            render('<div data-el="input"><div data-attr="class" data-value="foo" /></div>', {}),
            '<input class="foo" />');
    },

// XXX data-attr-something support?
// 'data-attr-name to set attr of name dynamically': function() {
//     assert.htmlEquals(
//         render('<div data-attr-class="{foo}"></div>', {foo: 'Foo'}),
//         '<div class="Foo" />');
// });

    'data-unwrap in element': function() {
        assert.htmlEquals(render('<div><div data-unwrap="">Hello world!</div></div>', {}),
                          '<div>Hello world!</div>');
    },

    'data-unwrap with dynamic class': function() {
        assert.htmlEquals(render('<div><div data-unwrap="" class="{foo}">Hello world!</div></div>',
                                 {foo: 'Foo'}),
                          '<div>Hello world!</div>');
                          
    },
    
    'data-unwrap with multiple elements inside it': function() {
        assert.htmlEquals(render('<div><div data-unwrap=""><p>Hello</p><p>world!</p></div></div>', {}),
                          '<div><p>Hello</p><p>world!</p></div>');
    },

    'data-unwrap on top': function() {
        assert.htmlEquals(render('<div data-unwrap="">Hello world!</div>', {}),
                          'Hello world!');
    },

    'data-unwrap with data-if where if is true': function() {
        assert.htmlEquals(render('<div><div data-unwrap="" data-if="flag">Hello world!</div>Something</div>',
                                 {flag: true}),
                          '<div>Hello world!Something</div>');
    },

    'data-unwrap with data-if where if is false': function() {
        assert.htmlEquals(render('<div><div data-unwrap="" data-if="flag">Hello world!</div>Something</div>',
                                 {flag: false}),
                          '<div>Something</div>');
    },

    'data-unwrap with data-repeat': function() {
        assert.htmlEquals(render('<div data-unwrap="" data-repeat="list">{@.}</div>',
                                 {list: ['a', 'b']}),
                          'ab');
    },

    'data-unwrap in data-unwrap': function() {
        assert.htmlEquals(render('A<div data-unwrap="">B<div data-unwrap="">C</div>D</div>', {}),
                          'ABCD');
    },

    'data-unwrap with data-trans': function() {
        assert.htmlEquals(render('<div data-unwrap="" data-trans="">Hello world!</div>', {}),
                          'Hallo wereld!');
    },


    'empty data-if is illegal': function() {
        assert.raises(function() {
            render('<div data-if="">Foo</div>', {});
        }, obtemp.CompilationError);
    },

    'deeper empty data-if is illegal': function() {
        assert.raises(function() {
            render('<div><div data-if="">Foo</div></div>', {});
        }, obtemp.CompilationError);
    },

    'empty data-repeat is illegal': function() {
        assert.raises(function() {
            render('<div data-repeat="">Foo</div>', {});
        }, obtemp.CompilationError);
    },

    'deeper empty data-repeat is illegal': function() {
        assert.raises(function() {
            render('<div><div data-repeat="">Foo</div></div>', {});
        }, obtemp.CompilationError);
    },

    'empty data-with is illegal': function() {
        assert.raises(function() {
            render('<div data-with="">Foo</div>', {});
        }, obtemp.CompilationError);
    },

    'deeper empty data-with is illegal': function() {
        assert.raises(function() {
            render('<div><div data-with="">Foo</div></div>', {});
        }, obtemp.CompilationError);
    },

    'fallback with inner dottedname not in outer scope': function() {
        assert.htmlEquals(render('<div data-with="a">{foo.bar}</div>',
                                 {a: {}, foo: {bar: 'hoi'}}),
                          '<div>hoi</div>');
    },


    'fallback with inner dottedname in outer scope but inner is not': function() {
        assert.htmlEquals(render('<div data-with="a">{foo.bar}</div>',
                                 {a: {foo: {}}, foo: {bar: 'hoi'}}),
                          '<div>hoi</div>');
    },

    'empty variable is literally rendered': function() {
        assert.htmlEquals(render('<div>{}</div>', {}),
                          '<div>{}</div>');
    },

    'variable with double dots is illegal': function() {
        assert.raises(function() {
            render('<div>{foo..bar}</div>', {});
        }, obtemp.CompilationError);
    },

    'variable with starting dot is illegal': function() {
        assert.raises(function() {
            render('<div>{.foo}</div>', {});
        }, obtemp.CompilationError);
    },

    'variable with ending dot is illegal': function() {
        assert.raises(function() {
            render('<div>{foo.}</div>', {});
        }, obtemp.CompilationError);
    },

    'variable with number in it is legal': function() {
        assert.htmlEquals(render('<div>{12}</div>', { '12': 'foo'}),
                          '<div>foo</div>');
    },

    'variable with underscore in it is legal': function() {
        assert.htmlEquals(render('<div>{fooBar}</div>', { 'fooBar': 'hoi'}),
                          '<div>hoi</div>');

    },

    'illegal variable in data-trans is checked': function() {
        assert.raises(function() {
            render('<div data-trans="">Hello {who.}!</div>', {who: 'X'});
        }, obtemp.CompilationError);
    },

    'illegal variable in data-tvar is checked': function() {
        assert.raises(function() {
            render('<div data-trans="">Hello <em data-tvar="who">{who.}</em>!</div>', {who: 'X'});
        }, obtemp.CompilationError);
    },

    'illegal variable in data-with is checked': function() {
        assert.raises(function() {
            render('<div data-with="foo.">Hello world!</div>', {});
        }, obtemp.CompilationError);
    },

    'illegal variable in data-if is checked': function() {
        assert.raises(function() {
            render('<div data-if="foo.">Hello world!</div>', {});
        }, obtemp.CompilationError);
    },

    'illegal variable in data-repeat is checked': function() {
        assert.raises(function() {
            render('<div data-repeat="foo.">Hello world!</div>', {});
        }, obtemp.CompilationError);
    },

    'illegal variable in data-render is checked': function() {
        assert.raises(function() {
            render('<div data-render="foo."></div>', {});
        }, obtemp.CompilationError);
    },

    'illegal variable in data-id is checked': function() {
            assert.raises(function() {
                render('<div data-id="{foo.}"></div>', {});
            }, obtemp.CompilationError);
        },


    'insert open {': function() {
        assert.htmlEquals(render('<div>{@open}</div>', {}),
                          '<div>{</div>');
    },

    'insert close }': function() {
        assert.htmlEquals(render('<div>{@close}</div>', {}),
                          '<div>}</div>');
    },

    'insert open { in data-trans': function() {
        assert.htmlEquals(render('<div data-trans="">Hello <em data-tvar="who">{@open}{who}{@close}</em>!</div>',
                                 {who: "X"}),
                          '<div><em>{X}</em>, hallo!</div>');
    },


    'data-on working': function() {
        var handlerCalled = false;
        var handlers = {
            myHandler: function(ev) {
                handlerCalled = true;
                }
        };

        var getHandler = function(name) {
            return handlers[name];
        };
        
        var template = new obtemp.Template(
            '<div id="one" data-on="click|myHandler">Click here</div>');
        
        var el = $('<div></div>');
        template.render(el, {}, { getHandler: getHandler});
        $('#one', el).trigger('click');
        assert.equals(handlerCalled, true);
    },

    'data-on no handlers supplied': function() {
        var handlerCalled = false;
        
        var template = new obtemp.Template(
            '<div id="one" data-on="click|myHandler">Click here</div>');
        
        var el = $('<div></div>');
        assert.raises(function() {
            template.render(el, {}, {});
        }, obtemp.RenderError);
    },

    'data-on specific handler not supplied': function() {
        var handlerCalled = false;
        
        var getHandler = function(name) {
            return null;
        };
        
        var template = new obtemp.Template(
            '<div id="one" data-on="click|myHandler">Click here</div>');
        
        var el = $('<div></div>');
            assert.raises(function() {
                template.render(el, {}, {getHandler: getHandler});
            }, obtemp.RenderError);
    },

    'data-on with data-el': function() {
        var handlerCalled = false;
        var handlers = {
            myHandler: function(ev) {
                handlerCalled = true;
            }
        };
        
        var getHandler = function(name) {
            return handlers[name];
        };
        
        var template = new obtemp.Template(
            '<span data-el="div" id="one" data-on="click|myHandler">Click here</span>');
        
        var el = $('<div></div>');
        template.render(el, {}, { getHandler: getHandler});
        $('#one', el).trigger('click');
        assert.equals(handlerCalled, true);
        
    },

    'data-on multiple on same el': function() {
            var firstHandlerCalled = false;
        var secondHandlerCalled = false;
        var handlers = {
            firstHandler: function(ev) {
                firstHandlerCalled = true;
            },
            secondHandler: function(ev) {
                secondHandlerCalled = true;
            }
        };

        var getHandler = function(name) {
            return handlers[name];
        };
        
        var template = new obtemp.Template(
            '<div id="one" data-on="click|firstHandler blur|secondHandler">Click here</div>');
        
        var el = $('<div></div>');
        template.render(el, {}, { getHandler: getHandler});
        $('#one', el).trigger('click');
        $('#one', el).trigger('blur');
        assert.equals(firstHandlerCalled, true);
        assert.equals(secondHandlerCalled, true);
    },

    'data-on on textarea': function() {
        var handlerCalled = false;
        var handlers = {
            myHandler: function(ev) {
                handlerCalled = true;
            }
        };

        var getHandler = function(name) {
            return handlers[name];
        };
        
        var template = new obtemp.Template(
            '<textarea id="one" data-on="keyup|myHandler"></textarea>');
        
        var el = $('<div></div>');
        template.render(el, {}, { getHandler: getHandler});
        $('#one', el).trigger('keyup');
        assert.equals(handlerCalled, true);

    },
    // XXX test failure if dotted name has non-end name to name that doesn't exist
    // also test with data-with, data-if, data-repeat


    // XXX data-if random nonsense

    'access variable codegen': function() {
        var obj = {a: 'foo', b: { bar: 'bar'}};
        
        var scope = new obtemp.Scope(obj);
        var f = obtemp.resolveFunc('@.');
        assert.equals(f(scope), obj);

        f = obtemp.resolveFunc('a');
        assert.equals(f(scope), 'foo');

        f = obtemp.resolveFunc('b.bar');
        assert.equals(f(scope), 'bar');

        scope.push({c: 'C'});

        f = obtemp.resolveFunc('c');
        assert.equals(f(scope), 'C');

        f = obtemp.resolveFunc('a');
        assert.equals(f(scope), 'foo');

        f = obtemp.resolveFunc('nonexistent');
        assert.equals(f(scope), undefined);
    },

    'variables': function() {
        assert.equals(obtemp.variables('Hello {who}!', {who: "world"}),
                      'Hello world!');
    },

    "pluralize in text without translation implicit data-plural": function() {
        assert.htmlEquals(render('<div data-trans="">1 elephant||{count} elephants</div>',
                                 { 'count': 1}),
                          '<div>1 elephant</div>');
        assert.htmlEquals(render('<div data-trans="">1 elephant||{count} elephants</div>',
                                 { 'count': 2}),
                          '<div>2 elephants</div>');
    },

    "pluralize in tvar without translation implicit data-plural": function() {
        assert.htmlEquals(render('<div data-trans=""><div data-tvar="foo">1 elephant||{count} elephants</div>!</div>',
                                 { 'count': 1}),
                          '<div><div>1 elephant</div>!</div>');
        assert.htmlEquals(render('<div data-trans=""><div data-tvar="foo">1 elephant||{count} elephants</div>!</div>',
                                 { 'count': 2}),
                          '<div><div>2 elephants</div>!</div>');
    },

    "pluralize in text without translation explicit data-plural": function() {
        assert.htmlEquals(render('<div data-trans="" data-plural="count">1 elephant||{count} elephants</div>',
                                 { 'count': 1}),
                          '<div>1 elephant</div>');
        assert.htmlEquals(render('<div data-trans="" data-plural="count">1 elephant||{count} elephants</div>',
                                 { 'count': 2}),
                          '<div>2 elephants</div>');
    },

    "pluralize in tvar without translation explicit data-plural": function() {
        assert.htmlEquals(render('<div data-trans=""><div data-tvar="foo" data-plural="count">1 elephant||{count} elephants</div>!</div>',
                                 { 'count': 1}),
                          '<div><div>1 elephant</div>!</div>');
        assert.htmlEquals(render('<div data-trans=""><div data-tvar="foo" data-plural="count">1 elephant||{count} elephants</div>!</div>',
                                 { 'count': 2}),
                          '<div><div>2 elephants</div>!</div>');
    },

    "pluralize in text with multiple possible implicit count variables": function() {
        assert.raises(function() {
            render('<div data-trans="">{count} {size} elephant||{count} {size} elephants</div>',
                   {'count': 1, 'size': 'big'});
        }, obtemp.CompilationError);
    },

    "data-tvar does not count as implicit count variable": function() {
        assert.raises(function() {
            render('<div data-trans=""><em data-tvar="size">{size}</em> elephant||<em data-tvar="size">{size}</em> elephants</div>',
                   {'size': 3});
        }, obtemp.CompilationError);

    },

    "pluralize in text without translation use data-plural to indicate count variable": function() {
        assert.htmlEquals(render('<div data-trans="" data-plural="count">{count} {size} elephant||{count} {size} elephants</div>',
                                 {'count': 1, 'size': 'big'}),
                          '<div>1 big elephant</div>');
        
        assert.htmlEquals(render('<div data-trans="" data-plural="count">{count} {size} elephant||{count} {size} elephants</div>',
                                 {'count': 2, 'size': 'big'}),
                          '<div>2 big elephants</div>');
    },

    'pluralize in text without translation use data-plural to indicate non-existent count variable': function() {
        assert.raises(function() {
            render('<div data-trans="" data-plural="notthere">{count} elephant||{count} elephants</div>',
                   {'count': 1});
        }, obtemp.RenderError);
    },

    "pluralize with explicit data-trans but no ||": function() {
        assert.raises(function() {
            render('<div data-trans="" data-plural="count">{count} elephants</div>');
        }, obtemp.CompilationError);
    },

    'data-plural without data-trans is not allowed': function() {
        assert.raises(function() {
            render('<div data-plural="count">{count} elephant||{count} elephants</div>',
                   {'count': 1});
        }, obtemp.CompilationError);
    },

    "pluralize in text with translation": function() {
        assert.htmlEquals(render('<div data-trans="" data-plural="count">1 cow||{count} cows</div>',
                                 { 'count': 1}),
                          '<div>1 koe</div>');
        assert.htmlEquals(render('<div data-trans="" data-plural="count">1 cow||{count} cows</div>',
                                 { 'count': 2}),
                          '<div>2 koeien</div>');
    },

    "pluralize in attr without translation": function() {
        assert.htmlEquals(render('<div data-trans="title" data-plural="title:count" title="1 elephant||{count} elephants"></div>',
                                 { 'count': 1}),
                          '<div title="1 elephant"></div>');
        assert.htmlEquals(render('<div data-trans="title" data-plural="title:count" title="1 elephant||{count} elephants"></div>',
                                 { 'count': 2}),
                          '<div title="2 elephants"></div>');
    },

    "pluralize in attr with translation, same explicit as implicit": function() {
        assert.htmlEquals(render('<div data-trans="title" data-plural="title:count" title="1 cow||{count} cows"></div>',
                                 { 'count': 1}),
                          '<div title="1 koe"></div>');
        assert.htmlEquals(render('<div data-trans="title" data-plural="title:count" title="1 cow||{count} cows"></div>',
                                 { 'count': 2}),
                          '<div title="2 koeien"></div>');
    },

    "pluralize in attr with translation, different explicit as implicit": function() {
        assert.htmlEquals(render('<div data-trans="title" data-plural="title:amount" title="1 cow||{count} cows"></div>',
                                 { 'count': 1, 'amount': 2}),
                          '<div title="1 koeien"></div>');
        assert.htmlEquals(render('<div data-trans="title" data-plural="title:amount" title="1 cow||{count} cows"></div>',
                                 { 'count': 2, 'amount': 1}),
                          '<div title="1 koe"></div>');
    },

    "implicit pluralize in attr with translation": function() {
        assert.htmlEquals(render('<div data-trans="title" title="1 cow||{count} cows"></div>',
                                 { 'count': 1}),
                          '<div title="1 koe"></div>');
        assert.htmlEquals(render('<div data-trans="title" title="1 cow||{count} cows"></div>',
                                 { 'count': 2}),
                          '<div title="2 koeien"></div>');
    },

    // test pluralize with explicit message ids
    // also test fallback when no translation is available

    // XXX is pluralMessageId relevant? should there be a way to explicitly
    // define it or does it serve no purpose as it's never used for lookup?

    "pluralize in attr and content translation": function() {
        assert.htmlEquals(render('<div data-trans=". title" data-plural=".:amount title:count" title="1 {size} elephant||{count} {size} elephants">1 {size} elephant||{amount} {size} elephants</div>',
                                 { 'count': 1, 'amount': 2, 'size': 'big'}),
                          '<div title="1 big elephant">2 big elephants</div>');
        assert.htmlEquals(render('<div data-trans=". title" data-plural=".:amount title:count" title="1 {size} elephant||{count} {size} elephants">1 {size} elephant||{amount} {size} elephants</div>',
                                 { 'count': 2, 'amount': 1, 'size': 'big'}),
                          '<div title="2 big elephants">1 big elephant</div>');
    },

    "pluralize in text with tvar without translation": function() {
        assert.htmlEquals(render('<div data-trans="" data-plural="count"><em data-tvar="count">1</em> elephant||<em>{count}</em> elephants</div>',
                                 { 'count': 1}),
                          '<div><em>1</em> elephant</div>');
        assert.htmlEquals(render('<div data-trans="" data-plural="count"><em data-tvar="count">1</em> elephant||<em>{count}</em> elephants</div>',
                                 { 'count': 2}),
                          '<div><em>2</em> elephants</div>');
    },

    "pluralize in text with tvar with translation": function() {
        assert.htmlEquals(render('<div data-trans="" data-plural="count"><em data-tvar="count">1</em> cow||<em>{count}</em> cows</div>',
                                 { 'count': 1}),
                          '<div><em>1</em> koe</div>');
        assert.htmlEquals(render('<div data-trans="" data-plural="count"><em data-tvar="count">1</em> cow||<em>{count}</em> cows</div>',
                                 { 'count': 2}),
                          '<div><em>2</em> koeien</div>');
    },

    "escape || in data-trans": function() {
        assert.htmlEquals(render('<div data-trans="">We use {@doublepipe} to mark pluralization</div>', {}),
                          '<div>We use || to mark pluralization</div>');
    },

    'escape || outside translation': function() {
        assert.htmlEquals(render('<div>We use {@doublepipe} to mark pluralization</div>', {}),
                          '<div>We use || to mark pluralization</div>');
    },

    "data-trans and {@open}, {@close} should translate translation contains {@open}": function() {
        assert.htmlEquals(render('<div data-trans="">Open {@open} and close {@close}</div>', {}),
                          '<div>Openen { en sluiten }</div>');
    },


    "data-trans and {@open}, {@close} should translate translation contains {": function() {
        assert.htmlEquals(render('<div data-trans="">Open {@open}</div>', {}),
                          '<div>Openen {</div>');
    },



    "data-repeat should not break finders with second section": function() {
        // there was a bug where data-repeat broke finders referring to
        // elements coming after it, because they would now point into
        // the generated loop
        // this causes in this case 'var' to be rendered into the
        // second li generated by the loop, instead of the third li
        // where it belongs. this is because this is also a section
        
        var complex = (
            '<ul>' +
                '<li data-repeat="entries">' +
                '<span></span>' +
                '</li>' +
                '<li data-if="v">' +
                '<a>{v}</a>' +
                '</li>' +
                '</ul>');
        
        assert.htmlEquals(render(complex,
                                 { 'entries': [{}, {}], v: 'bar'}),
                          '<ul><li><span/></li><li><span/></li><li><a>bar</a></ul>');
    },

    "data-repeat should not break finders without second section": function() {
        var complex = (
            '<ul>' +
                '<li data-repeat="entries">' +
                '<span></span>' +
                '</li>' +
                '<li>' +
                '<a>{v}</a>' +
                '</li>' +
                '</ul>');
        
        assert.htmlEquals(render(complex,
                                 { 'entries': [{}, {}], v: 'bar'}),
                          '<ul><li><span/></li><li><span/></li><li><a>bar</a></li></ul>');
    },

    'getXpath for top element': function() {
        var el = $('<html></html>');
        assert.equals(obtemp.getXpath(el.get(0)), '/html');
    },

    'getXpath for lower element': function() {
        var doc = $('<div><span class="the_span"></span></div>');
        assert.equals(obtemp.getXpath($('.the_span', doc).get(0)), '/div/span');
    },

    'getXpath for second element of same': function() {
        var doc = $('<div><span></span><span class="the_span"></span></html>');
        assert.equals(obtemp.getXpath($('.the_span', doc).get(0)), '/div/span[2]');
    },

    'getXpath for second element but different': function() {
        var doc = $('<div><div></div><span class="the_span"></span></html>');
        assert.equals(obtemp.getXpath($('.the_span', doc).get(0)), '/div/span');
    },

    'getXpath for first element but second is same': function() {
        var doc = $('<div><span class="the_span"></span><span></span></html>');
        assert.equals(obtemp.getXpath($('.the_span', doc).get(0)), '/div/span[1]');
    },


    'tokenize single variable': function() {
        assert.equals(obtemp.tokenize("{foo}"), [{type: obtemp.NAME_TOKEN,
                                                  value: 'foo'}]);
        
    },

    'tokenize variable in text': function() {
        assert.equals(obtemp.tokenize("the {foo} is great"),
                      [
                          {type: obtemp.TEXT_TOKEN,
                           value: 'the '},
                          {type: obtemp.NAME_TOKEN,
                           value: 'foo'},
                          {type: obtemp.TEXT_TOKEN,
                           value: ' is great'}
                      ]);
        
    },

    'tokenize variable starts text': function() {
        assert.equals(obtemp.tokenize("{foo} is great"),
                      [
                          {type: obtemp.NAME_TOKEN,
                           value: 'foo'},
                          {type: obtemp.TEXT_TOKEN,
                           value: ' is great'}
                      ]);
        
    },

    'tokenize variable ends text': function() {
        assert.equals(obtemp.tokenize("great is {foo}"),
                      [
                          {type: obtemp.TEXT_TOKEN,
                           value: 'great is '},
                          {type: obtemp.NAME_TOKEN,
                           value: 'foo'}
                      ]);
        
    },

    'tokenize two variables follow': function() {
        assert.equals(obtemp.tokenize("{foo}{bar}"),
                      [
                          {type: obtemp.NAME_TOKEN,
                           value: 'foo'},
                          {type: obtemp.NAME_TOKEN,
                           value: 'bar'}
                      ]);
    },

    'tokenize two variables with text': function() {
        assert.equals(obtemp.tokenize("a{foo}b{bar}c"),
                      [
                          {type: obtemp.TEXT_TOKEN,
                           value: 'a'},
                          {type: obtemp.NAME_TOKEN,
                           value: 'foo'},
                          {type: obtemp.TEXT_TOKEN,
                           value: 'b'},
                          {type: obtemp.NAME_TOKEN,
                           value: 'bar'},
                          {type: obtemp.TEXT_TOKEN,
                           value: 'c'}
                      ]);
    },


    'tokenize no variables': function() {
        assert.equals(obtemp.tokenize("Hello world!"),
                      [
                          {type: obtemp.TEXT_TOKEN,
                           value: 'Hello world!'}
                      ]);
    },

    'tokenize open but no close': function() {
        assert.equals(obtemp.tokenize("{foo"),
                      [
                          {type: obtemp.TEXT_TOKEN,
                           value: '{foo'}
                      ]);
    },

    'tokenize open but no close after text': function() {
        assert.equals(obtemp.tokenize("after {foo"),
                      [
                          {type: obtemp.TEXT_TOKEN,
                           value: 'after {foo'}
                      ]);
    },

    'tokenize open but no close after variable': function() {
        assert.equals(obtemp.tokenize("{bar} after {foo"),
                      [
                          {"type": obtemp.NAME_TOKEN,
                           "value": "bar"},
                          {"type": obtemp.TEXT_TOKEN,
                           "value": " after {foo"}
                      ]);
    },

    'tokenize just close': function() {
        assert.equals(obtemp.tokenize("foo } bar"),
                      [
                          {type: obtemp.TEXT_TOKEN,
                           value: 'foo } bar'}
                      ]);
    },

    'tokenize empty variable': function() {
        assert.equals(obtemp.tokenize("{}"),
                      [
                          {type: obtemp.TEXT_TOKEN,
                           value: '{}'}
                      ]);

    },

    'tokenize whitespace variable': function() {
        assert.equals(obtemp.tokenize("{ }"),
                      [
                          {type: obtemp.TEXT_TOKEN,
                           value: '{ }'}
                      ]);

    },

    'tokenize non-trimmed variable': function() {
        assert.equals(obtemp.tokenize("{foo }"),
                      [
                          {type: obtemp.NAME_TOKEN,
                           value: 'foo'}
                      ]);

    },

    'tokenize whitespace after {': function() {
        assert.equals(obtemp.tokenize("{ foo}"),
                      [
                          {type: obtemp.TEXT_TOKEN,
                           value: '{ foo}'}
                      ]);
    },

    'tokenize whitespace after { with variable': function() {
        assert.equals(obtemp.tokenize("{ foo}{bar}"),
                      [
                          {type: obtemp.TEXT_TOKEN,
                           value: '{ foo}'},
                          {type: obtemp.NAME_TOKEN,
                           value: 'bar'}
                      ]);

    }

});



/*global buster:false, sinon:false, obviel:false */
var assert = buster.assert;
var refute = buster.refute;

var testel = function() {
    return $(document.createElement('div'));
};

var renderText = function() { this.el.text(this.obj.text); };

var trim = function(s) {
    return s.replace(/^\s\s*/, '').replace(/\s\s*$/, '');
};

var htmlLower = function(html) {
    // some nasty normalization for browser compatibility
    // Firefox & IE give different cases for html, and
    // also sometimes Firefox includes a \n where IE does not.
    // I would use trimRight instead of a regular expression but
    // IE 7 at least doesn't support it yet
    return trim(html.toLowerCase().replace(/\s+$/, ''));
};

var coreTestCase = buster.testCase("core tests", {
    setUp: function() {
        this.server = sinon.fakeServer.create();
        this.server.autoRespond = true;

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
        obviel.clearRegistry();
        obviel.clearTemplateCache();
        obviel.i18n.clearTranslations();
        obviel.i18n.clearLocale();
        obviel.clearIface();
        this.server.restore();
    },
    'view with default name': function() {
        obviel.view({
            render: renderText
        });
        var el = testel();
        el.render({text: 'foo'});
        assert.equals(el.text(), 'foo');
    },

    'named view, no name provided results in error': function() {
        obviel.view({
            name: 'foo',
            render: renderText
        });

        assert.exception(function() {
            testel().render({text: 'bar'});
        }, 'LookupError');
    },

    'named view with name provided': function() {
        obviel.view({
            name: 'foo',
            render: renderText
        });
        var el = testel();
        el.render({text: 'bar'}, 'foo');
        assert.equals(el.text(), 'bar');
    },

    'iface view, no iface provided': function() {
        obviel.view({
            iface: 'ifoo',
            render: renderText
        });
        assert.exception(function() {
            testel().render({text: 'bar'});
        }, 'LookupError');
    },
                                   
    'iface view with iface provided': function() {
        obviel.view({
            iface: 'ifoo',
            render: renderText
        });
        var el = testel();
        el.render({text: 'baz', ifaces: ['ifoo']});
        assert.equals(el.text(), 'baz');
    },

    'iface view with only single iface in model': function() {
        obviel.view({
            iface: 'ifoo',
            render: renderText
        });
        var el = testel();
        el.render({text: 'baz', iface: 'ifoo'});
        assert.equals(el.text(), 'baz');
    },

    'iface view with iface and ifaces': function() {
        obviel.view({
            iface: 'ifoo',
            render: renderText
        });
        assert.exception(function() {
            testel().render({text: 'baz', iface: 'ifoo', ifaces: ['ibar']});
        }, 'IfaceError');
    },

    'iface view with only ifaces string': function() {
        obviel.view({
            iface: 'ifoo',
            render: renderText
        });
        var el = testel();
        el.render({text: 'baz', ifaces: 'ifoo'});
        assert.equals(el.text(), 'baz');
    },

    'iface/named view, no name provided': function() {
        obviel.view({
            iface: 'ifoo',
            name: 'foo',
            render: renderText
        });
        assert.exception(function() {
            testel().render({text: 'qux', ifaces: ['ifoo']});
        }, 'LookupError');
    },
    
    'iface/named view, no iface provided': function() {
        obviel.view({
            iface: 'ifoo',
            name: 'foo',
            render: renderText
        });
        assert.exception(function() {
            testel().render({text: 'qux'}, 'foo');
        }, 'LookupError');
    },

    'iface/named view, both iface and name provided': function() {
        obviel.view({
            iface: 'ifoo',
            name: 'foo',
            render: renderText
        });

        var el = testel();
        
        el.render(
            {text: 'qux', ifaces: ['ifoo']},
            'foo');
        assert.equals(el.text(), 'qux');
    },

    'explicit view instance': function() {
        obviel.view(new obviel.View({
            iface: 'ifoo',
            render: renderText
        }));
        var el = testel();
        el.render({text: 'qux', ifaces: ['ifoo']});
        assert.equals(el.text(), 'qux');
    },

    'init': function() {
        obviel.view({
            iface: 'ifoo',
            init: function() {
            this.whatever = true;
            }
        });
        var el = testel();
        el.render({ifaces: ['ifoo']});
        assert.equals(el.view().whatever, true);
    },
    
    'cleanup': function() {
        var cleanupCalled = false;
        obviel.view({
            iface: 'cleanup',
            render: renderText,
            cleanup: function() { cleanupCalled = true; }
        });
        obviel.view({
            ifaces: 'another',
            render: renderText
        });
        var el = testel();
        el.render({text: 'bar', ifaces: ['cleanup']}).done(
            function(view) {
                assert.equals(view.el.text(), 'bar');
                el.render({text: 'foo', ifaces: ['another']});
                assert.equals(view.el.text(), 'foo');
                assert(cleanupCalled);
            });
    },

    'unregister view, default name': function() {
        obviel.view({
            iface: 'ifoo',
            render: renderText
        });
        obviel.unregisterView('ifoo');
        assert.exception(function() {
            testel().render({iface: 'ifoo', text: 'qux'});
        }, 'LookupError');
    },
    
    'unregister view, custom name': function() {
        obviel.view({
            iface: 'ifoo',
            name: 'custom',
            render: renderText
        });
        obviel.unregisterView('ifoo', 'custom');
        assert.exception(function() {
            testel().render({iface: 'ifoo', text: 'qux'}, 'custom');
        }, 'LookupError');
    },
    'unregister unknown view is noop': function() {
        obviel.unregisterView('ifoo');
        assert(true);
    },
    'render url, default name': function(done) {
        obviel.view({
            render: renderText
        });
        var el = testel();
        
        this.mockJson('testUrl', {text: "foo"});
        el.render('testUrl').done(function() {
            assert.equals(el.text(), 'foo');
            done();
        });
    },

    'render url with name': function(done) {
        obviel.view({
            render: renderText,
            name: 'foo'
        });

        var el = testel();
        this.mockJson('testUrl', {text: "bar"});

        el.render('testUrl', 'foo').done(function() {
            assert.equals(el.text(), 'bar');
            done();
        });
    },
                                   
    'render url with iface': function(done) {
        obviel.view({
            render: renderText,
            iface: 'ifoo'
        });

        var el = testel();

        this.mockJson('testUrl', {"ifaces": ["ifoo"], "text": "baz"});
        
        el.render('testUrl').done(function() {
            assert.equals(el.text(), 'baz');
            done();
        });
    },

    'render url with name and iface': function(done) {
        obviel.view({
            render: renderText,
            iface: 'ifoo',
            name: 'foo'
        });

        var el = testel();
        this.mockJson('testUrl', {"ifaces": ["ifoo"], "text": "qux"});
        el.render('testUrl', 'foo').done(
            function() {
                assert.equals(el.text(), 'qux');
                done();
            });
    },

    'rerender url': function(done) {
        obviel.view({
            iface: 'ifoo',
            render: function() {
                this.el.text(this.obj.text);
            }
        });
        
        var called = 0;
        
        this.mockJson('testUrl', function() {
                called++;
                return {ifaces: ['ifoo'],
                        text: called.toString()};
        });

        var el = testel();
        el.render('testUrl').done(function(view) {
            assert.equals(view.el.text(), '1');
            el.rerender().done(function(view) {
                // this should call the URL again
                assert.equals(view.el.text(), '2');
                done();
            });
        });
    },
    
    'rerender context object': function() {
        obviel.iface('rerender');
            var numrenders = 0;
        obviel.view({
            iface: 'rerender',
            render: function() {
                var self = this;
                numrenders++;
                self.el.text(numrenders.toString());
            }
        });
        
        var el = testel();
        el.render({ifaces: ['rerender']});
        assert.equals(el.text(), '1');
        el.rerender();
        assert.equals(el.text(), '2');
    },

    'no content, empty render': function() {
        obviel.view({
            render: function() {}
        });
        var el = testel();
        el.html('<span>foo</span>');
        el.render({});
        assert.equals(el.text(), 'foo');
    },
                                   
    'no content no render': function() {
        obviel.view({
        });
        var el = testel();
        el.html('<span>foo</span>');
        el.render({});
        assert.equals(el.text(), 'foo');
    },


    // XXX is this correct?
    'rerender without viewstack': function() {
            var newel = $('div');
        refute.exception(function() {
            $(newel).rerender();
        });
    },

    'rerender ephemeral': function() {
        obviel.view({
            render: renderText
        });
        obviel.view({
            name: 'ephemeral',
            ephemeral: true,
            render: renderText
        });
        var el = testel();
        el.render({text: 'foo'});
        assert.equals(el.text(), 'foo');
        el.render({text: 'bar'}, 'ephemeral');
        assert.equals(el.text(), 'bar');
        el.rerender();
        assert.equals(el.text(), 'foo');
    },

    'render subviews': function(done) {
        obviel.view({
            iface: 'subviews',
            render: function() {
                this.el.html('<div class="sub1"></div><div class="sub2"></div>' +
                             '<div class="sub3"></div>');
            },
            subviews: {
                '.sub1': 'subUrl',
                '.sub2': 'subHtml',
                '.sub3': ['subNamed', 'foo']
            }
        });
        
        obviel.view({
            render: renderText
        });

        obviel.view({
            name: 'foo',
            render: function() {
                this.el.text('named');
            }
        });

        var el = testel();

        this.mockJson('testUrl', {"text": "foo"});
        el.render({
            ifaces: ['subviews'],
            subUrl: 'testUrl', // url
            subHtml: {text: 'bar'}, //  obj
            subNamed: {} // is registered by name foo
        }).done(function() {
            assert.equals($('.sub1', el).text(), 'foo');
            assert.equals($('.sub2', el).text(), 'bar');
            assert.equals($('.sub3', el).text(), 'named');
            done();
        });
    },

    'render subview false argument': function() {
        obviel.view({
            render: function() {
                this.el.html('<div class="sub1"></div>');
            },
            subviews: {
                '.sub1': 'subContent'
            }
        });
        // should just not render the sub view
        var el = testel();
        el.render({
            subContent: false
        });
        assert.equals($('.sub1', el).text(), '');
    },

    'render subview undefined argument': function() {
        obviel.view({
            render: function() {
                this.el.html('<div class="sub1"></div>');
            },
            subviews: {
                '.sub1': 'subContent'
            }
        });
        
        // should also not render the sub view
        var el = testel();
        el.render({});
        assert.equals($('.sub1', el).text(), '');
    },

    'view with html': function() {
        var renderCalled = 0;
        obviel.view({
            iface: 'html',
            html: '<div>foo!</div>',
            render: function() {
                renderCalled++;
            }
        });

        var el = testel();
        el.render(
            {ifaces: ['html']}).done(function() {
                assert.equals(htmlLower(el.html()), '<div>foo!</div>');
                assert.equals(renderCalled, 1);
            });
    },

    'view with htmlScript pointing to missing id': function() {
        obviel.view({
            iface: 'html',
            htmlScript: 'nonexistent_id'
        });

        var el = testel();
        assert.exception(function() {
            el.render({ifaces: ['html']});
        }, 'SourceLoaderError');
    },
    
    'view with htmlScript pointing to existing id': function() {
        var renderCalled = 0;
        obviel.view({
            iface: 'html',
            htmlScript: 'html_script_id',
            render: function() {
                renderCalled++;
            }
        });

        var el = testel();

        // make sure that the script tag is available
        $('body').append(
            '<script type="text/template" id="html_script_id"><div>foo!</div></script>');

        el.render({ifaces: ['html']}).done(
            function() {
                assert.equals(htmlLower(el.html()), '<div>foo!</div>');
                assert.equals(renderCalled, 1);
            });
    },

    'view with htmlUrl': function(done) {
        this.server.respondWith('GET', 'testUrl',
                                [200, {'Content-Type': 'text/html'},
                                 '<div>foo</div>']);
        
        var renderCalled = 0;
        obviel.view({
            iface: 'html',
            htmlUrl: 'testUrl',
            render: function() {
                renderCalled++;
            }
        });

        
        var el = testel();
        
        $(el).render(
            {ifaces: ['html']}).done(function() {
                assert.equals(htmlLower(el.html()), '<div>foo</div>');
                assert.equals(renderCalled, 1);
                done();
            });
    },
                                   
    'html context attribute overrides htmlUrl view one': function(done) {
        this.server.respondWith('GET', 'testUrl',
                                [200, {'Content-Type': 'text/html'},
                                 '<div>foo</div>']);
        
        var renderCalled = 0;
        obviel.view({
            iface: 'html',
            htmlUrl: 'testUrl',
            render: function() {
                renderCalled++;
            }
        });

        var el = testel();
        
        $(el).render(
            {ifaces: ['html'],
             html: '<span>spam!</span>'}).done(function() {
                 assert.equals(htmlLower(el.html()), '<span>spam!</span>');
                 assert.equals(renderCalled, 1);
                 done();
             });
    },
    
    'html context attribute overrides html view one': function(done) {
        var renderCalled = 0;
        obviel.view({
            iface: 'html',
            html: '<span>overridden</span>',
            render: function() {
                renderCalled++;
            }
        });

        var el = testel();
        
        el.render(
            {ifaces: ['html'],
             html: '<span>spam!</span>'}).done(function() {
                 assert.equals(htmlLower(el.html()), '<span>spam!</span>');
                 assert.equals(renderCalled, 1);
                 done();
             });
    },
    
    'htmlUrl context attr overrides html view one': function(done) {
        this.server.respondWith('GET', 'testUrl',
                                [200, {'Content-Type': 'text/html'},
                                 '<div>foo</div>']);

        obviel.view({
            iface: 'inlineHtml',
            html: '<span></span>',
            render: function() {
                // this will not work as there is no span
                $('span', this.el).text(this.obj.text);
            }
        });
        
        var el = testel();
        el.render(
            {ifaces: ['inlineHtml'],
             htmlUrl: 'testUrl',
             text: 'spam'}).done(function() {
                 assert.equals(htmlLower(el.html()), '<div>foo</div>');
                 done();
             });
    },

    'jsonScript view': function(done) {
        obviel.view({
            iface: 'jt',
            jsontScript: 'jsont_script_id'
        });
        
        var cache = obviel.cachedTemplates;
        // some implementation detail knowledge about cache keys is here
        var cacheKey = 'script_jsont_jsont_script_id';
        assert.equals(cache.get(cacheKey), null);

        $('body').append('<script type="text/template" id="jsont_script_id"><div>{foo}</div></script>');

        var el = testel();
        
        el.render(
            {foo: 'the value', ifaces: ['jt']}).done(function() {
                assert.equals($.trim(el.text()), 'the value');
                // we can find it in the cache now
                assert(cache.get(cacheKey));
                done();
            });
    },

    'html inline view is not cached': function(done) {
        obviel.view({
            iface: 'foo',
            html: '<p class="foo"></p>',
            render: function() {
                $('.foo', this.el).text(this.obj.foo);
                }
        });
        
        var cache = obviel.cachedTemplates;
        // some implementation detail knowledge about cache keys is here
        var cacheKey = 'inline_html_<p class="foo"></p>';
        assert.equals(cache.get(cacheKey), null);

        var el = testel();
        
        el.render(
            {foo: 'the value', ifaces: ['foo']}).done(function() {
                assert.equals($.trim($('.foo', el).text()), 'the value');
                // we can find it in the cache now
                assert.equals(cache.get(cacheKey), null);
                done();
            });
    },
    
    'jsont view': function(done) {
        this.server.respondWith('GET', 'testUrl',
                                [200, {'Content-Type': 'text/html'},
                                 '<div>{foo}</div>']);


        obviel.view({
            iface: 'jt',
            jsontUrl: 'testUrl'
        });
        
        var cache = obviel.cachedTemplates;
        // some implementation detail knowledge about cache keys is here
        var cacheKey = 'url_jsont_' + 'testUrl';
        assert.equals(cache.get(cacheKey), null);

        var el = testel();
        
        el.render(
            {foo: 'the value', ifaces: ['jt']}).done(function() {
                assert.equals($.trim(el.text()), 'the value');
                // we can find it in the cache now
                assert(cache.get(cacheKey));
                done();
            });
    },

    'view override on iface': function() {
        var el = testel();
        obviel.view({
            iface: 'ifoo',
            render: renderText
        });
        obviel.view({
            iface: 'ifoo',
            render: function() {
                this.el.text('spam: ' + this.obj.text);
            }
        });
        el.render({
            ifaces: ['ifoo'],
            text: 'eggs'});
        assert.equals(el.text(), 'spam: eggs');
    },

    'render on ancestor': function() {
        var called = 0;
        
        obviel.view({
            iface: 'ifoo',
            render: function() {
                this.el.append('<div>' + this.obj.text + '</div>');
                called++;
            }
        });

        var ancestor = testel();
        var descendant = $('<div class="descendant"></div>');
        ancestor.append(descendant);
            
        // first render on ancestor
        ancestor.render({
            ifaces: ['ifoo'],
            text: 'eggs'
        });
          
        // we now have a div appended
        assert.equals(ancestor.children().last().text(), 'eggs');
        assert.equals(called, 1);
        
        // then render on descendant of ancestor. but because
        // we have rendered this iface on ancestor, it will bubble up
        descendant.render({
            ifaces: ['ifoo'],
            text: 'ham'
        });
        assert.equals(called, 2);
        // nothing added to descendant
        assert.equals(descendant.children().length, 0);
        // instead it got added to ancestor
        assert.equals(ancestor.children().last().text(), 'ham');
        // this does apply directly to descendant
        obviel.view({
            iface: 'ibar',
            render: renderText
        });
        
        descendant.render({
            ifaces: ['ibar'],
            text: 'spam'
        });
        assert.equals(descendant.text(), 'spam');
        assert.equals(called, 2);
        // but rendering an ifoo again brings us back to ancestor
        descendant.render({
            ifaces: ['ifoo'],
            text: 'breakfast'
        });
        assert.equals(called, 3);
        assert.equals(ancestor.children().last().text(), 'breakfast');
    },

    'render-done.obviel event without subviews': function(done) {
        obviel.view({
            iface: 'ifoo',
            html: 'something'
        });
        var el = testel();
        var called = 0;
        el.bind('render-done.obviel', function(ev) {
            called++;
            // this is called only once
            assert.equals(called, 1);
            assert.equals(el.text(), 'something');
            done();
        });
        el.render({ifaces: ['ifoo']});
    },
                                   
    'render-done.obviel event with subviews': function(done) {
        obviel.view({
            iface: 'ifoo',
            html: '<div class="sub1"></div><div class="sub2"></div>',
            subviews: {
                '.sub1': 'sub1',
                '.sub2': 'sub2'
            }
        });
        obviel.view({
            render: renderText
        });
        // hook in event handler
        var el = testel();
        var called = 0;
        el.bind('render-done.obviel', function(ev) {
            called++;
            if (ev.view.iface === 'ifoo') {
                assert.equals(called, 3);
                assert.equals($('.sub1', el).text(), 'foo');
                assert.equals($('.sub2', el).text(), 'sub2 text');
                done();
            }
        });

        this.mockJson('testUrl', {text: "foo"});
        
        el.render({
            ifaces: ['ifoo'],
            sub1: 'testUrl',
            sub2: {'text': 'sub2 text'}
        });
        
    },

    'view events': function(done) {
        obviel.view({
            iface: 'ifoo',
            html: '<div class="class1"></div>',
            events: {
                'custom': {
                    '.class1': function(ev) {
                        assert.equals(ev.view.iface, 'ifoo');
                        assert(true, "event triggered");
                        done();
                    }
                }
            }
        });
        var el = testel();
        el.render({ifaces: ['ifoo']});
        $('.class1', el).trigger('custom');
    },

    'view events handler string': function(done) {
        obviel.view({
            iface: 'ifoo',
            html: '<div class="class1"></div>',
            custom: function(ev) {
                var self = this;
                assert.equals(self.iface, 'ifoo');
                assert(ev.view === self);
                assert(true, "event triggered");
                done();
            },
            events: {
                'custom': {
                    '.class1': 'custom'
                }
            }
        });
        var el = testel();
        el.render({ifaces: ['ifoo']});
        $('.class1', el).trigger('custom');
    },

    'view events cleanup': function() {
        var called = 0;
        obviel.view({
            iface: 'ifoo',
            html: '<div class="class1"></div>',
            events: {
                'custom': {
                    '.class1': function(ev) {
                        called++;
                    }
                }
            }
        });
        obviel.view({
            iface: 'ibar'
        });
        var el = testel();
        el.render({ifaces: ['ifoo']});
        // rendering ibar will clean up the events for ifoo, so the
        // event shouldn't have been triggered
        el.render({ifaces: ['ibar']});
        $('.class1').trigger('custom');
        assert.equals(called, 0);
    },

    'view events cleanup handler string': function() {
        var called = 0;
        obviel.view({
            iface: 'ifoo',
            html: '<div class="class1"></div>',
            custom: function(ev) {
                called++;
            },
            events: {
                'custom': {
                    '.class1': 'custom'
                }
        }
        });
        obviel.view({
            iface: 'ibar'
        });
        var el = testel();
        el.render({ifaces: ['ifoo']});
        // rendering ibar will clean up the events for ifoo, so the
        // event shouldn't have been triggered
        el.render({ifaces: ['ibar']});
        $('.class1').trigger('custom');
        assert.equals(called, 0);
    },

    // object events
    'object events': function(done) {
        obviel.view({
            iface: 'ifoo',
            html: '<div id="id1"></div>',
            objectEvents: {
                'custom': function(ev) {
                    assert.equals(ev.view.iface, 'ifoo');
                    assert(true, "event triggered");
                    done();
                    }
            }
        });
        var el = testel();
        var obj = {ifaces: ['ifoo']};
        el.render(obj);
        $(obj).trigger('custom');
    },

    'object events handler string': function(done) {
        obviel.view({
            iface: 'ifoo',
            html: '<div id="id1"></div>',
            custom: function(ev) {
                var self = this;
                assert.equals(self.iface, 'ifoo');
                assert(ev.view === self);
                assert(true, "event triggered");
                done();
            },
            objectEvents: {
                'custom': 'custom'
            }
        });
        var el = testel();
        var obj = {ifaces: ['ifoo']};
        el.render(obj);
        $(obj).trigger('custom');
    },

    'object event triggers rerender': function() {
        obviel.view({
            iface: 'ifoo',
            html: '<div class="theClass"></div>',
            render: function() {
                $('.theClass', this.el).text(this.obj.title);
            },
            objectEvents: {
            'custom': 'rerender'
            }
        });
        var el = testel();
        var obj = {ifaces: ['ifoo'], title: 'Hello'};
        el.render(obj);

        assert.equals($('.theClass', el).text(), 'Hello');
        
        obj.title = 'Bye';
        $(obj).trigger('custom');
        
        assert.equals($('.theClass', el).text(), 'Bye');
    },
    
    'object event triggers rerender with named view': function() {
        obviel.view({
            iface: 'ifoo',
            name: 'foo',
            html: '<div class="theClass"></div>',
            render: function() {
                $('.theClass', this.el).text(this.obj.title);
            },
            objectEvents: {
                'custom': 'rerender'
            }
        });
        var el = testel();
        var obj = {ifaces: ['ifoo'], title: 'Hello'};
        el.render(obj, 'foo');
        
        assert.equals($('.theClass', el).text(), 'Hello');
        
        obj.title = 'Bye';
        $(obj).trigger('custom');
        
        assert.equals($('.theClass', el).text(), 'Bye');
    },
    
    'object events cleanup': function() {
        var called = 0;
        obviel.view({
            iface: 'ifoo',
            html: '<div id="id1"></div>',
            objectEvents: {
                'custom': function(ev) {
                    called++;
                }
        }
        });
        obviel.view({
            iface: 'ibar'
        });
        var el = testel();
        var obj = {ifaces: ['ifoo']};
        el.render(obj);
        // rendering ibar will clean up the events for ifoo, so the
        // event shouldn't have been triggered
        el.render({ifaces: ['ibar']});
        $(obj).trigger('custom');
        assert.equals(called, 0);
    },
    
    'object events cleanup handler string': function() {
            var called = 0;
        obviel.view({
            iface: 'ifoo',
            html: '<div id="id1"></div>',
            custom: function(ev) {
                called++;
            },
            objectEvents: {
                'custom': 'custom'
            }
        });
            obviel.view({
                    iface: 'ibar'
            });
        var el = testel();
        var obj = {ifaces: ['ifoo']};
        el.render(obj);
        // rendering ibar will clean up the events for ifoo, so the
        // event shouldn't have been triggered
        el.render({ifaces: ['ibar']});
        $(obj).trigger('custom');
        assert.equals(called, 0);
    },

    'object event nested views': function(done) {
        var called = 0;

        // a view with a manually nested bar view
        obviel.view({
            iface: 'ifoo',
            html: '<div class="class1"></div>',
            render: function() {
                $('.class1', this.el).render(this.obj.bar);
            }
        });
        // a completely different view
        obviel.view({
            iface: 'iqux',
            html: '<p>Something else</p>'
        });

        // the bar view
        obviel.view({
            iface: 'ibar',
            render: function() {
                this.el.text(this.obj.title);
            },
            objectEvents: {
                'update': function(ev) {
                    called++;
                    done();
                }
            }
        });

        // render the foo object with the foo view, indirectly rendering
        // the bar view
        var el = testel();
        var obj = {
            ifaces: ['ifoo'],
            bar: {
                ifaces: ['ibar'],
                title: "Hello world"
            }
        };
        el.render(obj);

        // now render a completely different object in its place
        el.render({iface: 'iqux'});

        // when we trigger the event on bar, the event will still be called
        // even though it is on a now unconnected element
        $(obj.bar).trigger('update');

        assert.equals(called, 1);

        // is this a problem? first, for plain events this is not a problem,
        // as nothing will be triggering events on the elements they are associated
        // with anymore. but for objects possibly temporarily not represented by
        // a visible view it is odd that a now-invisible view is still handling
        // events for it.

        // one way to solve this problem would be to automatically disconnect
        // all subviews when unrendering a view. declarative subviews are easy
        // enough to unconnect, but non-declarative ones such as the one in this
        // test are more difficult. of course it should still be possible to
        // disconnect them if we simply thrawl through all the underlying
        // elements disconnecting everything in there.
        // alternatively we could disconnect the object views of the object being
        // rendered as soon as an object is not being viewed anymore. we also
        // would need to do this for sub-objects.
    },

    'element bind': function() {
        obviel.view({
            iface: 'ifoo',
            render: function() {
                this.el.append('<div class="added">/div>');
            }
        });

        obviel.view({
            iface: 'ibar'
        });

        var el = testel();
        // render a view on el
        el.render({ifaces: ['ifoo']});
        // should see single added div
        assert.equals($('.added', el).length, 1);
        
        // render the original object again, in a sub el
        el.append('<div class="sub">nothing</div>');
        var subEl = $('.sub', el);
        subEl.render({ifaces: ['ifoo']});

        // the sub el should be unchanged
        assert.equals(subEl.text(), 'nothing');
        assert.equals(subEl.children().length, 0);
        
        // the original el should have a second div added
        assert.equals($('.added', el).length, 2);
    },

    'element bind cleanup': function() {
        obviel.view({
            iface: 'ifoo',
            render: function() {
                    this.el.append('<div class="added"></div>');
            }
        });

        obviel.view({
            iface: 'ibar'
        });

        var el = testel();
        // render a view on el
        el.render({ifaces: ['ifoo']});
        // we expect a single added div
        assert.equals($('.added', el).length, 1);
        
        // render another view on el, wiping out the previous one
        el.render({ifaces: ['ibar']});

        // render the original object again, on a sub object
        el.append('<div class="sub"></div>');
        var subEl = $('.sub', el);
        subEl.render({ifaces: ['ifoo']});
        
        // since we've cleaned up the original ifoo view for 'el' by
        // rendering the ibar view, we should render it on the subobject,
        // not the original el
        assert.equals($('.added', subEl).length, 1);

        // in total we've added two things
        assert.equals($('.added', el).length, 2);
        
    },

    'unview': function() {
        obviel.view({
            iface: 'ifoo',
            render: function() {
                this.el.append('<div class="added">/div>');
            }
        });

        obviel.view({
            iface: 'ibar'
        });

        var el = testel();
        // render a view on el
        el.render({ifaces: ['ifoo']});
        // should see single added div
        assert.equals($('.added', el).length, 1);
        
        // render the original object again, in a sub el
        el.append('<div class="sub">nothing</div>');
        var subEl = $('.sub', el);
        subEl.render({ifaces: ['ifoo']});

        // the sub el should be unchanged
            assert.equals(subEl.text(), 'nothing');
        assert.equals(subEl.children().length, 0);
        
        // the original el should have a second div added
        assert.equals($('.added', el).length, 2);

        // try it again, should see another div added
        subEl.render({ifaces: ['ifoo']});
        assert.equals($('.added', el).length, 3);

        // still nothing on sub el
        assert.equals(subEl.children().length, 0);
        
        // now we unview the original view
        el.unview();

        // if we render on subview now, we should see a div added there
        subEl.render({ifaces: ['ifoo']});
        assert.equals($('.added', subEl).length, 1);
        // and 1 more in total
        assert.equals($('.added', el).length, 4);
    },

    'parentView': function() {
        var el = testel();
        assert(el.parentView() === null);
        obviel.view({
            iface: 'ifoo'
        });
        el.render({'ifaces': ['ifoo']});
        assert(el.parentView() === el.view());

        var newEl = $('<div></div>');
        el.append(newEl);
        assert(newEl.parentView() === el.view());
    },


    'transform server contents': function(done) {
        /* view works on ifoo iface only */
        obviel.view({
            iface: 'ifoo',
            render: function() {
                this.el.text(this.obj.text + ': ' + this.obj.viewName);
            }
        });

        /* return an object without iface; we will add "ifoo" iface
           using transformer */
        this.mockJson('testUrl', {text: 'Hello world'});
    
        obviel.transformer(function(obj, url, name) {
            obj.iface = 'ifoo';
            obj.viewName = name;
            return obj;
        });
        
        var el = testel();
        el.render('testUrl').done(function(view) {
            assert.equals(view.el.text(), 'Hello world: default');
            done();
        });
    },
    
    'transform server contents only obj arg': function(done) {
        /* view works on ifoo iface only */
        obviel.view({
            iface: 'ifoo',
            render: function() {
                this.el.text(this.obj.text);
            }
        });
        
        /* return an object without iface; we will add "ifoo" iface
           using transformer */
        this.mockJson('testUrl', {text: 'Hello world'});
        
        obviel.transformer(function(obj) {
            obj.iface = 'ifoo';
            return obj;
        });
        
        var el = testel();
        el.render('testUrl').done(function(view) {
            assert.equals(view.el.text(), 'Hello world');
            done();
        });
    },
    
    'disable transformer': function(done) {
        /* view works on ifoo iface only */
        obviel.view({
            iface: 'ifoo',
            render: function() {
                this.el.text(this.obj.text);
            }
        });

        this.mockJson('testUrl', {iface: 'ifoo', text: 'Hello world'});
        
        obviel.transformer(function(obj) {
            obj.text = obj.text + ' transformed';
            return obj;
        });

        /* disable transformer again */
        obviel.transformer(null);
        
        var el = testel();
        el.render('testUrl').done(function(view) {
            assert.equals(view.el.text(), 'Hello world');
            done();
        });
    },

    'transform server contents distinguish between uris': function(done) {
        obviel.view({
            iface: 'ifoo',
            render: function() {
                this.el.text("ifoo: " + this.obj.text);
            }
        });
        obviel.view({
            iface: 'ibar',
            render: function() {
                this.el.text("ibar: " + this.obj.text);
            }
        });
        
        this.mockJson('testFooUrl',
                      {text: 'Hello world foo'});
        this.mockJson('testBarUrl',
                      {text: 'Hello world bar'});
        
        obviel.transformer(function(obj, url) {
            if (url === 'testFooUrl') {
                obj.iface = 'ifoo';
                return obj;
            } else if (url === 'testBarUrl') {
                obj.iface = 'ibar';
                return obj;
            }
            return null;
        });
        
        var el = testel();
        el.render('testFooUrl').done(function(view) {
            assert.equals(view.el.text(), 'ifoo: Hello world foo');
        });

        el.render('testBarUrl').done(function(view) {
            assert.equals(view.el.text(), 'ibar: Hello world bar');
            done();
        });
    },

    'transform content based on view using before': function() {
        obviel.view({
            iface: 'text',
            before: function() {
                this.obj.length = this.obj.data.length;
            },
            jsont: 'The text "{data}" has {length} characters.'
        });
        
        var el = testel();
        el.render({
            iface: 'text',
            data: 'Hello world'
        });

        assert.equals(el.text(), 'The text "Hello world" has 11 characters.');
    },

    'obviel template view': function() {
        obviel.view({
            iface: 'test',
            obvt: '{hello}'
        });

        var el = testel();
        el.render({
            iface: 'test',
            hello: 'Hello world!'
        });

        assert.equals(el.text(), 'Hello world!');
    },

    'obviel template obvtScript': function() {
        obviel.view({
            iface: 'test',
            obvtScript: 'obvt_script_id'
        });

        var el = testel();

        $('body').append(
            '<script type="text/template" id="obvt_script_id">Hello <em>{world}</em></script>');
        
        el.render({
            iface: 'test',
            world: 'world'
        });

        assert.equals(htmlLower(el.html()), 'hello <em>world</em>');
    },

        'obviel template with sub elements view': function() {
            obviel.view({
                iface: 'test',
                obvt: '<p>{hello}</p>'
            });

            var el = testel();
            el.render({
                    iface: 'test',
                hello: 'Hello world!'
            });

            assert.equals(el.children().get(0).nodeName, 'P');
            assert.equals(el.children().first().text(), 'Hello world!');

        },

    'obviel template with event handler hooking up to view': function() {
        var clicked = false;
        
        obviel.view({
            iface: 'test',
            obvt: '<div class="someClass" data-on="click|handleClick">Click here!</div>',
            handleClick: function(ev) {
                clicked = true;
            }
        });

        var el = testel();
        el.render({ iface: 'test'});

        $('.someClass', el).trigger('click');

        assert.equals(clicked, true);
    },

    'obviel template, event handler can access view correctly': function() {
        
        obviel.view({
            iface: 'test',
            obvt: '<div class="someClass" data-on="click|handleClick">Click here!</div>',
            handleClick: function(ev) {
                this.obj.clicked = true;
            }
        });

        var el = testel();
        var test = {iface: 'test', clicked: false};
        
        el.render(test);

        $('.someClass', el).trigger('click');

        assert.equals(test.clicked, true);
    },

    'obviel template, formatter lookup on view': function() {
        obviel.view({
            iface: 'test',
            obvt: '<div class="someClass">{value|myFormatter}</div>',
            myFormatter: function(value) {
                return value.toUpperCase();
            }
        });

        var el = testel();
        el.render({iface: 'test', value: 'the value'});
        assert.equals($('.someClass', el).text(), 'THE VALUE');
    },

    'obviel template, formatter lookup falls back to globally registered': function() {
        
        obviel.template.registerFormatter(
            'myFormatter',
            function(value) {
                return value + ' BUT GLOBAL!';
            });
        
        obviel.view({
            iface: 'test',
            obvt: '<div class="someClass">{value|myFormatter}</div>'
        });

        var el = testel();
        el.render({iface: 'test', value: 'the value'});
        assert.equals($('.someClass', el).text(), 'the value BUT GLOBAL!');
    },


    'obviel template, data-call lookup on view': function() {
        obviel.view({
            iface: 'test',
            obvt: '<div class="someClass" data-call="myFunc"></div>',
            myFunc: function(el) {
                el.addClass('FOO');
            }
        });

        var el = testel();
        el.render({iface: 'test'});
        assert($('.someClass', el).hasClass('FOO'));
    },

    'obviel template, data-call lookup falls back to globally registered': function() {
        
        obviel.template.registerFunc(
            'myFunc',
            function(el) {
                el.addClass('FOO');
            });
        
        obviel.view({
            iface: 'test',
            obvt: '<div class="someClass" data-call="myFunc"></div>'
        });

        var el = testel();
        el.render({iface: 'test'});
        assert($('.someClass', el).hasClass('FOO'));
    },

    'obviel template, data-call which refers to view': function() {
        obviel.view({
            iface: 'foo',
            obvt: '<div class="alpha" data-call="someFunc"></div>',
            someFunc: function(el, variable, context) {
                if (this.obj.flag) {
                    el.addClass('foo');
                }
            }
        });

        var el = testel();
        el.render({iface: 'foo', flag: true});
        assert($('.alpha', el).hasClass('foo'));
    },

    // XXX this used to work but we switched to frag based rendering
    // to isolate things
    // 'obviel data-repeat with data-attr inside': function() {
    //     obviel.view({
    //         iface: 'outer',
    //         obvt: '<ul><li data-repeat="items" data-render="@."></li></ul>'
    //     });
    //     obviel.view({
    //         iface: 'inner',
    //         obvt: '<div data-attr="class" data-value="done" /><div>Foo</div>'
    //     });

    //     var el = testel();
    //     var test = {iface: 'outer', items: [{iface: 'inner'}, {iface: 'inner'}]};

    //     el.render(test);

    //     $('li', el).each(function(index, el) {
    //         assert($(el).hasClass('done'));
    //     });
    // },

    // this broke in the transition from jQuery 1.6.x to 1.7.
    'fallback to global event handler for detached element': function() {

        obviel.view({
            iface: 'person',
            render: function() {
                this.el.text(this.obj.name);
            }
        });

        var el = $('<div></div>');
        el.render({iface: 'person', name: 'foo'});

        assert.equals(el.text(), 'foo');
    },

    'obviel i18n default domain used by template, no translations': function() {
        obviel.view({
            iface: 'person',
            obvt: '<p class="result" data-trans="">This is {name}.</p>'
        });

        var el = testel();
        el.render({iface: 'person', name: 'foo'});

        assert.equals($('.result', el).text(), 'This is foo.');
        
    },

    'obviel i18n default domain used by template, translation': function() {
        var nl_NL = obviel.i18n.translationSource({'This is {name}.':
                                                   'Dit is {name}.'});

        obviel.i18n.registerTranslation('nl_NL', nl_NL);

        obviel.i18n.setLocale('nl_NL');
        
        obviel.view({
            iface: 'person',
            obvt: '<p class="result" data-trans="">This is {name}.</p>'
        });

        var el = testel();
        el.render({iface: 'person', name: 'foo'});

        assert.equals($('.result', el).text(), 'Dit is foo.');
        
    },

    "obviel i18n non-default domain, no locale set": function() {
        var nl_NL = obviel.i18n.translationSource({'This is {name}.':
                                                   'Dit is {name}.'});
        
        obviel.i18n.registerTranslation('nl_NL', nl_NL, 'other');
        
        obviel.i18n.translate('other');
        
        obviel.view({
            iface: 'person',
            obvt: '<p class="result" data-trans="">This is {name}.</p>'
        });
        
        var el = testel();
        el.render({iface: 'person', name: 'foo'});
        
        assert.equals($('.result', el).text(), 'This is foo.');
        
    },
    
    
    "obviel i18n non-default domain, locale set": function() {
        var nl_NL = obviel.i18n.translationSource({'This is {name}.':
                                                   'Dit is {name}.'});
        
        obviel.i18n.registerTranslation('nl_NL', nl_NL, 'other');
        
        obviel.i18n.translate('other');
        
        obviel.i18n.setLocale('nl_NL');
        
        obviel.view({
            iface: 'person',
            obvt: '<p class="result" data-trans="">This is {name}.</p>'
        });
        
        var el = testel();
        el.render({iface: 'person', name: 'foo'});
        
        assert.equals($('.result', el).text(), 'Dit is foo.');
    },
    
    
    "obviel i18n default domain, try to look up in non-default": function() {
        // register some translations in 'other' domain
        var nl_NL = obviel.i18n.translationSource({'This is {name}.':
                                                   'Dit is {name}.'});
        
        obviel.i18n.registerTranslation('nl_NL', nl_NL, 'other');
        
        // now translation is in default domain
        obviel.i18n.translate();
        
        obviel.i18n.setLocale('nl_NL');
        
        obviel.view({
        iface: 'person',
            obvt: '<p class="result" data-trans="">This is {name}.</p>'
        });
        
            // now we expect no translation to take place
        var el = testel();
        el.render({iface: 'person', name: 'foo'});
        
        assert.equals($('.result', el).text(), 'This is foo.');
    },
    
    'obviel i18n with pluralization, Dutch translation': function() {
        var nlNL = obviel.i18n.translationSource({'1 cow': [
            '{count} cows', '1 koe', '{count} koeien']});
        
        obviel.i18n.registerTranslation('nlNL', nlNL, 'other');
        
        obviel.i18n.translate('other');
        
        obviel.i18n.setLocale('nlNL');
        
        obviel.view({
            iface: 'something',
            obvt: '<p class="result" data-trans="">1 cow||{count} koeien</p>'
        });
        
        var el = testel();
        
        el.render({iface: 'something', count: 1});
        
        assert.equals($('.result', el).text(), '1 koe');
        
        el.render({iface: 'something', count: 2});
        
        assert.equals($('.result', el).text(), '2 koeien');
        
    },
    
    'obviel i18n with pluralization and tvar, Dutch translation': function() {
        var nlNL = obviel.i18n.translationSource({'{count} cow': [
            '{count} cows', '{count} koe', '{count} koeien']});
        
        obviel.i18n.registerTranslation('nlNL', nlNL, 'other');
        
        obviel.i18n.translate('other');
        
        obviel.i18n.setLocale('nlNL');
        
        obviel.view({
            iface: 'something',
            obvt: '<p class="result" data-plural="count" data-trans=""><em data-tvar="count">1</em> cow||<em>{count}</em> koeien</p>'
        });
        
        var el = testel();
        
        el.render({iface: 'something', count: 1});
        
        assert.equals($('.result', el).html().toLowerCase(), '<em>1</em> koe');
        
        el.render({iface: 'something', count: 2});
        
        assert.equals($('.result', el).html().toLowerCase(), '<em>2</em> koeien');
        
    },
    
    'obviel i18n with pluralization, Polish translation': function() {
        var plPL = obviel.i18n.translationSource({
            '': {
                'Plural-Forms': 'nplurals=3; plural=(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)'
            },
            '1 file.':
            ['{count} file.',
             '1 plik.',
             '{count} pliki.',
             "{count} pliko'w."]});
        
        obviel.i18n.registerTranslation('plPL', plPL, 'other');
        
        obviel.i18n.translate('other');
        
        obviel.i18n.setLocale('plPL');
        
        obviel.view({
            iface: 'something',
            obvt: '<p class="result" data-trans="">1 file.||{count} files.</p>'
        });
        
        var el = testel();
        
        el.render({iface: 'something', count: 1});
        assert.equals($('.result', el).text(), '1 plik.');
        
        el.render({iface: 'something', count: 2});
        assert.equals($('.result', el).text(), '2 pliki.');
        
        el.render({iface: 'something', count: 3});
        assert.equals($('.result', el).text(), '3 pliki.');
        
        el.render({iface: 'something', count: 4});
        assert.equals($('.result', el).text(), '4 pliki.');
        
        el.render({iface: 'something', count: 5});
        assert.equals($('.result', el).text(), "5 pliko'w.");
        
        el.render({iface: 'something', count: 21});
        assert.equals($('.result', el).text(), "21 pliko'w.");
        
        el.render({iface: 'something', count: 22});
        assert.equals($('.result', el).text(), "22 pliki.");
        
    },
    
    'render only completes when render method promise completes': function() {
        var defer = $.Deferred();
        obviel.view({
            iface: 'foo',
            render: function() {
                // don't resolve defer here, but later
                return defer.promise();
            }
        });
        var called = false;
        var el = testel();
        el.render({iface: 'foo'}).done(function() {
            called = true;
        });
        
        assert.equals(called, false);
        // resolving the render defer should complete things
        defer.resolve();
        assert.equals(called, true);
    },
    
    'render only completes when data-render has been rendered': function() {
        var defer = $.Deferred();
        obviel.view({
            iface: 'subview',
            render: function() {
                // don't resolve defer here, but later
                return defer.promise();
            }
        });
        obviel.view({
            iface: 'main',
            obvt: '<div><p data-render="sub"></p></div>'
        });
        
        var called = false;
        
        var el = testel();
        
        el.render({iface: 'main', sub: {iface: 'subview'}}).done(
            function() {
                called = true;
            });
        assert.equals(called, false);
        // now resolve subview
        defer.resolve();
        assert.equals(called, true);
    },
    
    'render only completes when all data-render has been rendered': function() {
        var defer0 = $.Deferred(),
        defer1 = $.Deferred();
        obviel.view({
            iface: 'subview0',
            render: function() {
                // don't resolve defer here, but later
                return defer0.promise();
            }
        });
        obviel.view({
            iface: 'subview1',
            render: function() {
                // don't resolve defer here, but later
                return defer1.promise();
            }
        });
        
        obviel.view({
            iface: 'main',
            obvt: '<div><p data-repeat="l" data-render="@."></p></div>'
        });
        
        var called = false;
        
        var el = testel();
        
        el.render({iface: 'main', l: [{iface: 'subview0'},
                                      {iface: 'subview1'}]}).done(
                                          function() {
                                              called = true;
                                          });
        assert.equals(called, false);
        // now resolve subview0
        defer0.resolve();
        assert.equals(called, false);
        // now resolve subview1, thereby resolving all in list
        defer1.resolve();
        assert.equals(called, true);
    },
    
    'render returns a promise': function(done) {
        obviel.view({
            iface: 'foo'
        });
        
        var called = false;
        var el = testel();
        el.render({iface: 'foo'}).done(function(view) {
            called = true;
            done();
        });
        
        assert.equals(called, true);
    },
    
    "location of inline compiler error in top section": function() {
        obviel.view({
            iface: 'foo',
            obvt: '<p data-repeat=""></p>' // deliberately broken
        });
        
        var el = testel();
        
        // first time rendering will also compile
        try {
            el.render({iface: 'foo'});
        } catch(e) {
            assert.equals(e.toString(),
                          "data-repeat may not be empty (foo obvt /p)");
        }
    },
    
    "location of inline compiler error in deeper section": function() {
        obviel.view({
            iface: 'foo',
            obvt: '<div data-if="foo"><p data-repeat=""></p></div>' // deliberately broken
        });
        
        var el = testel();
        
        // first time rendering will also compile
        try {
            el.render({iface: 'foo'});
        } catch(e) {
            assert.equals(e.toString(),
                          "data-repeat may not be empty (foo obvt /div/p)");
        }
    },
    
    "location of inline template error": function() {
        obviel.view({
            iface: 'foo',
            obvt: '<p>{notfound}</p>'
        });
        
        var el = testel();
        
        try {
            el.render({iface: 'foo'});
        } catch(e) {
            assert.equals(e.toString(),
                          "variable 'notfound' could not be found (foo obvt /p)");
        }
    },
    
    
    "location of script template error": function() {
        obviel.view({
            iface: 'foo',
            obvtScript: 'obvt_notfound_id'
        });
        
        var el = testel();

        $('body').append(
            '<script type="text/template" id="obvt_notfound_id">{notfound}</script>');

        try {
            el.render({iface: 'foo'});
        } catch (e) {
            assert.equals(e.toString(),
                          "variable 'notfound' could not be found (foo obvtScript:obvt_notfound_id /)");
        }
    },
    "http error": function(done) {
        var spy = sinon.spy();
        obviel.httpErrorHook(spy);
        
        this.server.respondWith('GET', 'testUrl',
                                [500, {'Content-Type': 'text/html'},
                                 '<div>Internal server error</div>']);

        var el = testel();
        el.render('testUrl').fail(function() {
            assert.calledOnce(spy);
            assert.equals(spy.args[0][0].status, 500);
            done();
        });
    },
    
    "http error in template-based subview": function(done) {
        obviel.view({
            iface: 'foo',
            obvt: '<div data-render="sub"></div>'
        });
        var spy = sinon.spy();
        obviel.httpErrorHook(spy);
        
        this.server.respondWith('GET', 'testUrl',
                                [500, {'Content-Type': 'text/html'},
                                 '<div>Internal server error</div>']);

        var el = testel();
        el.render({iface: 'foo', sub: 'testUrl'}).fail(function() {
            assert.calledOnce(spy);
            assert.equals(spy.args[0][0].status, 500);
            done();
        });

    },
    "http error in classic subview": function(done) {
        obviel.view({
            iface: 'foo',
            obvt: '<div class="thediv"></div>',
            subviews: {
                ".thediv": 'sub'
            }
        });
        var spy = sinon.spy();
        obviel.httpErrorHook(spy);
        
        this.server.respondWith('GET', 'testUrl',
                                [500, {'Content-Type': 'text/html'},
                                 '<div>Internal server error</div>']);

        var el = testel();
        el.render({iface: 'foo', sub: 'testUrl'}).fail(function() {
            assert.calledOnce(spy);
            assert.equals(spy.args[0][0].status, 500);
            done();
        });
    }
    
    
    // XXX problems testing this due to asynchronous nature of JS; exception
// doesn't get thrown in time. need to write this around deferred.reject
// "location of script url error": function(done) {
//     $.mockJson('obvtUrl', '{notfound}');
    
//     obviel.view({
//         iface: 'foo',
//         obvtUrl: 'obvtUrl'
//     });

//     var el = testel();
//     el.render({iface: 'foo'}).fail(function() {
//         assert.equals(e.toString(),
//               "variable 'notfound' could not be found (iface: foo name: default; obvt from url obvtUrl)");
//         done();
//     });
    
// });

});

/*global buster:false, sinon:false, obviel:false */
var assert = buster.assert;
var refute = buster.refute;

// TODO

// * configure updater to remove properties or leave them be
// * configure to interpret messages back as add, update, delete (I guess
// the type of updater could also do this). how to determine where we
// want to do the add?
// * if we can't find a property on m.obj we want to give a nice error?


// * in many cases we don't want to add an entry implicitly as a default;
// we only want to add it if the outer object is there in the first place.
// * we also want to make sure a default gets added in if we have update: {}
// * we shouldn't be adding 'add' implicitly to all mapping configs?

var syncTestCase = buster.testCase("sync tests:", {
    setUp: function() {
        this.server = sinon.fakeServer.create();
        this.server.autoRespond = true;
    },
    tearDown: function() {
        obviel.sync.clear();
        this.server.restore();
    },
    "config with explicit target.update.http": function() {
        obviel.sync.mapping({
            iface: 'test',
            target: {
                update: {
                    http: {
                        method: 'POST',
                        url: function(action) {
                            return action.obj.updateUrl + '_extra';
                        }
                    }
                }
            }
        });
        assert.equals(
            obviel.sync.getMapping('test').target.update.http.method,
            'POST');
        assert.equals(
            obviel.sync.getMapping('test').target.update.http.url(
                {obj: { updateUrl: 'foo' }}), 'foo_extra');
    },
    "config with implicit target.update.http": function() {
        obviel.sync.mapping({
            iface: 'test',
            target: {
            }
        });
        assert.equals(
            obviel.sync.getMapping('test').target.update.http.method,
            'POST');
        assert.equals(
            obviel.sync.getMapping('test').target.update.http.url(
                {obj: { updateUrl: 'foo' }}), 'foo');
    },
    "config with empty target.update": function() {
        obviel.sync.mapping({
            iface: 'test',
            target: {
                update: {
                }
            }
        });
        assert($.isPlainObject(obviel.sync.getMapping('test').target.update.http));
    },
    "config empty target, without update": function() {
        obviel.sync.mapping({
            iface: 'test',
            target: {
            }
        });
        assert($.isPlainObject(obviel.sync.getMapping('test').target.update));
    },
    "config without target": function() {
        obviel.sync.mapping({
            iface: 'test'
        });
        assert($.isPlainObject(obviel.sync.getMapping('test').target));
    },

    "config with explicit source.update": function() {
        obviel.sync.mapping({
            iface: 'test',
            source: {
                update: {
                    finder: function(action) {
                        action.obj.found = true;
                        return action.obj;
                    }
                }
            }
        });
        var obj = {};
        assert.equals(
            obviel.sync.getMapping('test').source.update.finder(
                {obj: obj}),
            obj);
        assert(
            obviel.sync.getMapping('test').source.update.finder(
                {obj: obj}).found);
    },
    "config with empty source.update": function() {
        obviel.sync.mapping({
            iface: 'test',
            source: {
                update: {
                }
            }
        });
        var obj = { id: 'foo', model: true };
        obviel.sync.registerObjById(obj);

        var backendObj = { id: 'foo', backend: true};
        
        assert.equals(
            obviel.sync.getMapping('test').source.update.finder(
                {obj: backendObj}),
            obj);
        refute.equals(
            obviel.sync.getMapping('test').source.update.finder(
                {obj: backendObj}),
            backendObj);
    },
    "config with empty source": function() {
        obviel.sync.mapping({
            iface: 'test',
            source: {
            }
        });
        assert($.isPlainObject(obviel.sync.getMapping('test').source.update));
    },
    "config without source": function() {
        obviel.sync.mapping({
            iface: 'test'
        });
        assert($.isPlainObject(obviel.sync.getMapping('test').source));
    },
    "update to object URL": function(done) {
        obviel.sync.mapping({
            iface: 'test'
        });
        var updateData = null;

        var testUrl = 'blah';
        
        this.server.respondWith('POST', testUrl, function(request) {
            updateData = $.parseJSON(request.requestBody);
            request.respond(200, {'Content-Type': 'application/json'},
                            JSON.stringify({}));
        });

        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            id: 'testid',
            value: 1.0,
            updateUrl: testUrl
        };
        session.update(obj);
        session.commit().done(function() {
            assert.equals(updateData.value, 1.0);
            done();
        });
    },
    "add to container URL": function(done) {
        obviel.sync.mapping({
            iface: 'container'
        });

        var testUrl = 'blah';
        
        var addData = null;
        
        this.server.respondWith('POST', testUrl, function(request) {
            addData = $.parseJSON(request.requestBody);
            request.respond(200, {'Content-Type': 'application/json'},
                            JSON.stringify({}));
        });

        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            id: 'testid',
            value: 1.0
        };
        var container = {
            iface: 'container',
            entries: [],
            addUrl: testUrl
        };
        container.entries.push(obj);
        session.add(obj, container, 'entries');
        session.commit().done(function() {
            assert.equals(addData, {iface: 'test', id: 'testid',
                                    value: 1.0});
            done();
        });
    },
    "remove from container URL with id, HTTP JSON post": function(done) {
        obviel.sync.mapping({
            iface: 'container'
        });

        var testUrl = 'blah';

        var removeIds;
        
        this.server.respondWith('POST', testUrl, function(request) {
            removeIds = $.parseJSON(request.requestBody);
            request.respond(200, {'Content-Type': 'application/json'},
                            JSON.stringify({}));
        });

        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            id: 'testid',
            value: 1.0
        };
        var container = {
            iface: 'container',
            entries: [obj],
            removeUrl: testUrl
        };
        container.entries.splice(0, 1);
        session.remove(obj, container, 'entries');
        session.commit().done(function() {
            assert.equals(removeIds, ['testid']);
            done();
        });

    },
    
    "remove multiple from container URL with id, single HTTP JSON post": function(done) {
        obviel.sync.mapping({
            iface: 'container'
        });

        var testUrl = 'blah';

        var removeIds;
        
        this.server.respondWith('POST', testUrl, function(request) {
            removeIds = $.parseJSON(request.requestBody);
            request.respond(200, {'Content-Type': 'application/json'},
                            JSON.stringify({}));
        });

        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj1 = {
            iface: 'test',
            id: 'testid1',
            value: 1.0
        };
        var obj2 = {
            iface: 'test',
            id: 'testid2',
            value: 2.0
        };
        
        var container = {
            iface: 'container',
            entries: [obj1, obj2],
            removeUrl: testUrl
        };
        container.entries.splice(0, 2);
        // XXX should the remove check whether there is something to remove?
        // or is this really the job of the mutator API?
        session.remove(obj1, container, 'entries');
        session.remove(obj2, container, 'entries');
        
        session.commit().done(function() {
            assert.equals(removeIds, ['testid1', 'testid2']);
            done();
        });

    },
    "remove single id from container URL with multiple entries": function(done) {
        obviel.sync.mapping({
            iface: 'container'
        });

        var testUrl = 'blah';

        var removeIds;
        
        this.server.respondWith('POST', testUrl, function(request) {
            removeIds = $.parseJSON(request.requestBody);
            request.respond(200, {'Content-Type': 'application/json'},
                            JSON.stringify({}));
        });

        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj1 = {
            iface: 'test',
            id: 'testid1',
            value: 1.0
        };
        var obj2 = {
            iface: 'test',
            id: 'testid2',
            value: 2.0
        };
        
        var container = {
            iface: 'container',
            entries: [obj1, obj2],
            removeUrl: testUrl
        };
        container.entries.splice(1, 1);
        session.remove(obj2, container, 'entries');
        
        session.commit().done(function() {
            assert.equals(removeIds, ['testid2']);
            done();
        });

    },

    "remove from container URL without id fails": function() {
        obviel.sync.mapping({
            iface: 'container'
        });

        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        // obj has no id, so we cannot remove it
        var obj = {
            iface: 'test',
            value: 1.0
        };
        
        var testUrl = 'blah';
        var container = {
            iface: 'container',
            entries: [obj],
            addUrl: testUrl
        };
        container.entries.splice(0, 1);
        session.remove(obj, container, 'entries');
        assert.exception(function() {
            session.commit();
        }, 'IdError');
    },

    "update to socket io": function(done) {
        obviel.sync.mapping({
            iface: 'test',
            target: {
                update: {
                    socket: {
                        type: 'updateTest'
                    }
                }
            }
        });
        // mock a socket io
        var io = {
            emit: sinon.spy()
        };
        
        var conn = new obviel.sync.SocketIoConnection(io);
        var session = conn.session();

        var obj = {
            iface: 'test',
            id: 'testid',
            value: 1.0
        };
        session.update(obj);
        session.commit().done(function() {
            assert(io.emit.calledWith('updateTest', obj));
            done();
        });
    },
    "source refresh from HTTP response, client-initiated": function(done) {
        var obj = {
            iface: 'test',
            id: 'testid',
            value: 1.0,
            refreshUrl: 'refreshObj'
        };

        obviel.sync.mapping({
            iface: 'test',
            source: {
                update: {
                    finder: function(action) {
                        return obj;
                    }
                }
            }
        });
        
        this.server.respondWith('GET', 'refreshObj', function(request) {
            request.respond(
                200, {'Content-Type': 'application/json'},
                JSON.stringify({
                    iface: 'test',
                    id: 'testid',
                    value: 2.0,
                    refreshUrl: 'refreshObj'
                }));
        });

        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();
        session.refresh(obj);
        session.commit().done(function() {
            assert.equals(obj.value, 2.0);
            done();
        });
    },
    "source update from HTTP response, after POST": function(done) {
        var testUrl = 'blah';

        // client-side data
        
        var obj = {
            iface: 'test',
            id: 'testid',
            value: 1.0
        };
        var container = {
            iface: 'container',
            entries: [],
            addUrl: testUrl
        };

        // mapping
        obviel.sync.mapping({
            iface: 'test',
            source: {
                update: {
                    finder: function(action) {
                        return obj;
                    }
                }
            }
        });

        obviel.sync.mapping({
            iface: 'container',
            source: {
                update: {
                    finder: function(action) {
                        return container;
                    }
                }
            }
        });

        // server-side data; a simple list
        var serverData = [];
        
        // when we get a new entry, add it to the list, touch value to
        // see we had it, and respond with an array of things to update
        this.server.respondWith('POST', testUrl, function(request) {
            var addData = $.parseJSON(request.requestBody);
            serverData.push(addData);

            addData.value += 1;
            
            request.respond(200, {'Content-Type': 'application/json'},
                            JSON.stringify([
                                addData,
                                {
                                    iface: 'container',
                                    count: serverData.length
                                }
                            ]));
        });

        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        container.entries.push(obj);
        session.add(obj, container, 'entries');
        session.commit().done(function() {
            assert.equals(serverData,
                          [{iface: 'test', id: 'testid', value: 2.0}]);
            assert.equals(container.count, 1);
            assert.equals(container.entries[0].value, 2.0);
            done();
        });
        
    },
    "source add from HTTP response after refresh": function(done) {
        var container = {
            id: 'foo',
            iface: 'container',
            entries: [],
            refreshUrl: 'getAdditions'
        };
        
        obviel.sync.mapping({
            iface: 'container',
            source: {
                add: {
                    finder: function(action) {
                        return {
                            container: container,
                            propertyName: 'entries'
                        };
                    }
                }
            },
            target: {
                refresh: {
                    http: {
                        response: obviel.sync.actionProcessor
                    }
                }
            }
        });
        
        this.server.respondWith('GET', 'getAdditions', function(request) {
            request.respond(
                200, {'Content-Type': 'application/json'},
                JSON.stringify({
                    name: 'add',
                    containerIface: 'container',
                    obj: {
                        iface: 'test',
                        id: 'testid',
                        value: 2.0
                    }
                }));
        });
        
        
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        session.refresh(container);
        
        session.commit().done(function(entries) {
            assert.equals(container.entries.length, 1);
            assert.equals(container.entries[0], {
                iface: 'test',
                id: 'testid',
                value: 2.0
            });
            done();
        });
    },
    
    "mutator single object update": function() {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            id: 'testid',
            value: 1.0
        };

        var m = session.mutator(obj);

        m.set('value', 2.0);

        assert.equals(obj.value, 2.0);
        assert.equals(session.updated(), [obj]);
    },
    
    "mutator single object refresh": function() {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            id: 'testid',
            value: 1.0
        };

        var m = session.mutator(obj);

        m.refresh();
        
        assert.equals(obj.value, 1.0);
        assert.equals(session.refreshed(), [obj]);
    },

    
    "mutator single object, multiple updates, object with id": function() {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            id: 'testid',
            value: 1.0
        };

        var m = session.mutator(obj);

        m.set('value', 2.0);
        m.set('value', 3.0);
        
        assert.equals(obj.value, 3.0);
        assert.equals(session.updated(), [obj]);
    },
    "mutator single object, multiple updates, object without id": function() {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            value: 1.0
        };

        var m = session.mutator(obj);

        m.set('value', 2.0);
        m.set('value', 3.0);
        
        assert.equals(obj.value, 3.0);
        assert.equals(session.updated(), [obj]);
    },
    "mutator single object, multiple refreshes": function() {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            id: 'testid',
            value: 1.0
        };

        var m = session.mutator(obj);

        m.refresh();
        m.refresh();
        
        assert.equals(session.refreshed(), [obj]);
    },
    
    "mutator multiple objects, multiple updates": function() {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj1 = {
            iface: 'test',
            id: '1',
            value: 1.0
        };

        var obj2 = {
            iface: 'test',
            id: '2',
            value: 1.0
        };

        
        var m1 = session.mutator(obj1);
        var m2 = session.mutator(obj2);
        
        m1.set('value', 2.0);
        m2.set('value', 3.0);
        
        assert.equals(obj1.value, 2.0);
        assert.equals(obj2.value, 3.0);
        
        assert.equals(session.updated(), [obj1, obj2]);
    },

    "mutator add to array, single add": function() {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            id: 'a',
            entries: []
        };
        
        var m = session.mutator(obj);

        var addedObj = {name: 'alpha'};
        
        m.get('entries').push(addedObj);
        
        assert.equals(obj.entries, [{name: 'alpha'}]);
        
        assert.equals(session.added(),
                      [{container: obj, propertyName: 'entries',
                        obj: addedObj}]);
    },

    "add to array, backend-assigned id": function(done) {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        obviel.sync.mapping({
            iface: 'container',
            target: {
                add: {
                    http: {
                        url: 'add',
                        response: obviel.sync.actionProcessor
                    }
                }
            }
        });

        obviel.sync.mapping({
            iface: 'item'
        });
        
        this.server.respondWith('POST', 'add', function(request) {
            var obj = $.parseJSON(request.requestBody);
            // the backend assigns the id
            obj.id = 'b';
            request.respond(
                200, {'Content-Type': 'application/json'},
                JSON.stringify({
                    name: 'update',
                    obj: obj}));
        });

        var obj = {
            iface: 'container',
            id: 'a',
            entries: []
        };
        
        var m = session.mutator(obj);

        var addedObj = {iface: 'item', name: 'alpha'};
        
        m.get('entries').push(addedObj);

        session.commit().done(function() {
            assert.equals(addedObj.id, 'b');
            done();
        });
        
    },

    "add to array, then update": function() {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            id: 'a',
            entries: []
        };
        
        var m = session.mutator(obj);

        var addedObj = {name: 'alpha'};
        
        m.get('entries').push(addedObj);
        session.mutator(addedObj).set('name', 'alphaChanged');
        
        assert.equals(obj.entries, [{name: 'alphaChanged'}]);
        
        assert.equals(session.added(),
                      [{container: obj, propertyName: 'entries',
                        obj: addedObj}]);
        // add trumps updating; we are already going to send it to backend
        // as an add so we don't need to care about the update
        assert.equals(session.updated(),
                      []);
    },

    "update, then add to array": function() {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            id: 'a',
            entries: []
        };
        
        var addedObj = {name: 'alpha'};
        
        session.mutator(addedObj).set('name', 'alphaChanged');
        session.mutator(obj).get('entries').push(addedObj);
        
        assert.equals(obj.entries, [{name: 'alphaChanged'}]);
        
        assert.equals(session.added(),
                      [{container: obj, propertyName: 'entries',
                        obj: addedObj}]);
        // add trumps updating; we are already going to send it to backend
        // as an add so we don't need to care about the earlier update
        assert.equals(session.updated(),
                      []);

    },

    "add to array, then refresh": function() {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            id: 'a',
            entries: []
        };
        
        var m = session.mutator(obj);

        var addedObj = {name: 'alpha'};
        
        m.get('entries').push(addedObj);
        session.mutator(addedObj).refresh();
        
        
        assert.equals(session.added(),
                      [{container: obj, propertyName: 'entries',
                        obj: addedObj}]);
        assert.equals(session.refreshed(),
                      [{name: 'alpha'}]);
    },

    "add to array, then remove": function() {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            id: 'a',
            entries: []
        };
        
        var m = session.mutator(obj);

        var addedObj = {name: 'alpha'};
        
        m.get('entries').push(addedObj);
        m.get('entries').remove(addedObj);
        
        assert.equals(obj.entries, []);
        
        // add & removal cancel each other, so no action needs to be taken
        assert.equals(session.added(), []);
        assert.equals(session.removed(), []);
    },

    "update, then refresh": function() {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            value: 1.0
        };

        var m = session.mutator(obj);

        m.refresh();
        m.set('value', 2.0);
        
        assert.equals(obj.value, 2.0);
        assert.equals(session.updated(), [obj]);
        // the refresh will happen later
        assert.equals(session.refreshed(), [obj]);
    },
    "remove from array, then update": function() {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();
        
        var addedObj = {name: 'alpha'};

        var obj = {
            iface: 'test',
            id: 'a',
            entries: [addedObj]
        };
        
        var m = session.mutator(obj);
        
        m.get('entries').remove(addedObj);
        session.mutator(addedObj).set(name, 'alphaChanged');
        
        assert.equals(session.removed(),
                      [{container: obj, propertyName: 'entries',
                        obj: addedObj}]);
        assert.equals(session.updated(), []);
    },
    "commit directly from object mutator": function(done) {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        obviel.sync.mapping({
            iface: 'test'
        });
        var updateData = null;

        var testUrl = 'blah';
        
        this.server.respondWith('POST', testUrl, function(request) {
            updateData = $.parseJSON(request.requestBody);
            request.respond(200, {'Content-Type': 'application/json'},
                            JSON.stringify({}));
        });

        
        var obj = {
            iface: 'test',
            updateUrl: testUrl
        };
        
        var m = session.mutator(obj);
        m.set('foo', 'bar');
        m.commit().done(function() {
            delete updateData['clientId'];
            assert.equals(updateData, {iface: 'test',
                                       updateUrl: testUrl,
                                       foo: 'bar'});
            done();
        });
    },
    "commit directly from array mutator": function(done) {
        obviel.sync.mapping({
            iface: 'container'
        });

        var testUrl = 'blah';
        
        var addData = null;
        
        this.server.respondWith('POST', testUrl, function(request) {
            addData = $.parseJSON(request.requestBody);
            request.respond(200, {'Content-Type': 'application/json'},
                            JSON.stringify({}));
        });

        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        var obj = {
            iface: 'test',
            id: 'testid',
            value: 1.0
        };
        var container = {
            iface: 'container',
            entries: [],
            addUrl: testUrl
        };
        var m = session.mutator(container);
        m.get('entries').push(obj);
        m.get('entries').commit().done(function() {
            assert.equals(addData, {iface: 'test', id: 'testid',
                                    value: 1.0});
            done();
        });
    },
    "get on array mutator to get mutator for index": function() {
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();
        
        var indexObj = {name: 'alpha'};

        var obj = {
            iface: 'test',
            id: 'a',
            entries: [indexObj]
        };
        
        var m = session.mutator(obj);

        assert.equals(m.get('entries').get(0).get('name'), 'alpha');
    },
    "get mutator directly from connection": function() {
        var conn = new obviel.sync.HttpConnection();

        var obj = {
            iface: 'test',
            value: 'a'
        };
        var m = conn.mutator(obj);
        m.set('value', 'b');
        
        assert.equals(obj.value, 'b');
    },
    "localstorage init": function(done) {
        var obj = {
            iface: 'test',
            value: 'a'
        };

        obviel.sync.mapping({
            iface: 'test',
            source: {
                update: {
                    finder: function(orig) {
                        return obj;
                    }
                }
            }
        });

        var conn = new obviel.sync.LocalStorageConnection('test');
        conn.init(obj);

        var m = conn.mutator(obj);
        m.set('value', 'b');
        m.commit().done(function() {
            var conn2 = new obviel.sync.LocalStorageConnection('test');
            obj.value = 'c';
            conn2.init(obj).done(function() {
                assert.equals(obj.value, 'b');
                done();
            });
        });
        
    },
    "a session is reused if not yet committed": function() {
        var obj = {
            iface: 'test',
            value: 'a',
            entries: []
        };

        var conn = new obviel.sync.HttpConnection();
        
        var m = conn.mutator(obj);
        m.set('value', 'b');
        assert.equals(m.session.updated(), [obj]);

        var newObj = {
            iface: 'sub'
        };
        m.get('entries').push(newObj);
        assert.equals(m.session.added(), [{container: obj,
                                           propertyName: 'entries',
                                           obj: newObj}]);
        assert.equals(m.session.updated(), [obj]);
        
    },
    "events are sent for targets if configured": function(done) {
        obviel.sync.mapping({
            iface: 'test',
            target: {
                update: {
                    event: 'foo'
                }
            }
        });

        var testUrl = 'testurl';
        
        var obj = {
            iface: 'test',
            value: 'a',
            updateUrl: testUrl
        };
        
        this.server.respondWith('POST', testUrl, function(request) {
            request.respond(200, {'Content-Type': 'application/json'},
                            JSON.stringify({}));
        });
        
        var events = 0;
        $(obj).bind('foo', function() {
            events++;
        });
        
        var conn = new obviel.sync.HttpConnection();
        var m = conn.mutator(obj);
        m.set('value', 'b');
        // nothing has been committed, so no events sent
        assert.equals(events, 0);
        // now we commit
        m.commit().done(function() {
            // now we expect there have been an event
            assert.equals(events, 1);
            done();
        });
    },
    "events are sent for sources if configured": function(done) {
        obviel.sync.mapping({
            iface: 'test',
            source: {
                update: {
                    event: 'foo'
                }
            },
            target: {
                refresh: {
                    http: {
                        response: obviel.sync.actionProcessor
                    }
                }
            }
        });

        var testUrl = 'testurl';
        
        var obj = {
            id: 'one',
            iface: 'test',
            value: 'a',
            refreshUrl: testUrl
        };

        obviel.sync.registerObjById(obj);
        
        this.server.respondWith('GET', testUrl, function(request) {
            request.respond(200, {'Content-Type': 'application/json'},
                JSON.stringify({
                    name: 'update',
                    obj: {
                        id: 'one',
                        iface: 'test',
                        value: 'b',
                        refreshUrl: testUrl
                    }
                }));
        });
        
        var events = 0;
        $(obj).bind('foo', function() {
            events++;
        });
        
        var conn = new obviel.sync.HttpConnection();
        var m = conn.mutator(obj);
        m.refresh();
        // nothing has been committed, so no events sent
        assert.equals(events, 0);
        // now we commit
        m.commit().done(function() {
            // now we expect there have been an event
            assert.equals(events, 1);
            done();
        });
    },
    "source transformer for update": function(done) {
        var obj = {
            iface: 'test',
            id: 'testid',
            value: 1.0,
            refreshUrl: 'refreshObj'
        };

        obviel.sync.mapping({
            iface: 'test',
            source: {
                update: {
                    finder: function(action) {
                        return obj;
                    },
                    http: {
                        transformer: function(obj) {
                            obj.extra = "extra!";
                            return obj;
                        }
                    }
                }
            }
        });
        
        this.server.respondWith('GET', 'refreshObj', function(request) {
            request.respond(
                200, {'Content-Type': 'application/json'},
                JSON.stringify({
                    iface: 'test',
                    id: 'testid',
                    value: 2.0,
                    refreshUrl: 'refreshObj'
                }));
        });

        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();
        session.refresh(obj);
        session.commit().done(function() {
            assert.equals(obj.extra, "extra!");
            done();
        });

    },
    "source transformer for add": function(done) {
        var container = {
            id: 'foo',
            iface: 'container',
            entries: [],
            refreshUrl: 'getAdditions'
        };
        
        obviel.sync.mapping({
            iface: 'container',
            source: {
                add: {
                    finder: function(action) {
                        return {
                            container: container,
                            propertyName: 'entries'
                        };
                    },
                    http: {
                        transformer: function(obj) {
                            obj.extra = 'extra!';
                            return obj;
                        }
                    }
                }
            },
            target: {
                refresh: {
                    http: {
                        response: obviel.sync.actionProcessor
                    }
                }
            }
        });
        
        this.server.respondWith('GET', 'getAdditions', function(request) {
            request.respond(
                200, {'Content-Type': 'application/json'},
                JSON.stringify({
                    name: 'add',
                    containerIface: 'container',
                    obj: {
                        iface: 'test',
                        id: 'testid',
                        value: 2.0
                    }
                }));
        });
        
        
        var conn = new obviel.sync.HttpConnection();
        var session = conn.session();

        session.refresh(container);
        
        session.commit().done(function(entries) {
            assert.equals(container.entries.length, 1);
            assert.equals(container.entries[0], {
                iface: 'test',
                id: 'testid',
                value: 2.0,
                extra: 'extra!'
            });
            done();
        });
    }
    
    // refresh & remove
    // remove & remove again
    
    // XXX obj that is inherited?

    
});

/*global buster:false, obviel:false */
var assert = buster.assert;
var refute = buster.refute;

var ifaceTestCase = buster.testCase("iface tests", {
    setUp: function() {
    },
    tearDown: function() {
        obviel.clearIface();
    },
    "object implements object iface": function() {
        assert(obviel.provides({}, 'object'));
    },

    "object ifaces": function() {
        assert.equals(obviel.ifaces({}), ['object']);
    },

    'object does not implement base': function() {
        refute(obviel.provides({}, 'base'));
    },
    
    'foo implements foo': function() {
        assert(obviel.provides({ifaces: ['foo']}, 'foo'));
    },

    'foo implements object': function() {
        assert(obviel.provides({ifaces: ['foo']}, 'object'));
    },

    'foo implements base': function() {
        assert(obviel.provides({ifaces: ['foo']}, 'base'));
    },

    'foo does not implement bar': function() {
        refute(obviel.provides({ifaces: ['foo']}, 'bar'));
    },

    'foo ifaces': function() {
        assert.equals(
            obviel.ifaces({ifaces: ['foo']}),
            ['foo', 'base', 'object']);
    },

    'bar implements bar': function() {
        assert(obviel.provides({ifaces: ['bar']}, 'bar'));
    },

    'bar implements foo': function() {
        obviel.iface('foo');
        obviel.iface('bar', 'foo');
        assert(obviel.provides({ifaces: ['bar']}, 'foo'));
    },

    'bar ifaces': function() {
        obviel.iface('foo');
        obviel.iface('bar', 'foo');
        assert.equals(
            obviel.ifaces({ifaces: ['bar']}),
            ['bar', 'foo', 'base', 'object']);
    },

    'qux ifaces': function() {
        obviel.iface('foo');
        obviel.iface('baz', 'foo');
        obviel.iface('qux', 'baz');
        assert.equals(
            obviel.ifaces({ifaces: ['qux']}),
            ['qux', 'baz', 'foo', 'base', 'object']);
    },

    'mess ifaces': function() {
        obviel.iface('spam');
        obviel.iface('eggs', 'spam');
        obviel.iface('foo');
        obviel.iface('baz', 'foo');
        obviel.iface('qux', 'baz');
        obviel.iface('mess', 'eggs', 'qux');
        assert.equals(
            obviel.ifaces({ifaces: ['mess']}),
            ['mess', 'eggs', 'qux', 'spam', 'baz', 'foo',
             'base', 'object']);
    },
                               
    'foo+spam ifaces': function() {
        assert.equals(
            obviel.ifaces({ifaces: ['foo', 'spam']}),
            ['foo', 'spam', 'base', 'object']);
    },

    'bar+foo ifaces': function() {
        obviel.iface('foo');
        obviel.iface('bar', 'foo');
        assert.equals(
            obviel.ifaces({ifaces: ['bar', 'foo']}),
            ['bar', 'foo', 'base', 'object']);
    },
    
    'cannot define same iface twice': function() {
        obviel.iface('foo');
        assert.exception(function() {
            obviel.iface('foo');
        }, 'IfaceError');
    },

    'must define base iface': function() {
        assert.exception(function() {
            obviel.iface('bar', 'foo');
        }, 'IfaceError');
    },

    'foo+bar ifaces': function() {
        obviel.iface('foo');
        obviel.iface('bar', 'foo');
        // XXX should not bar be the first iface here?
        assert.equals(
            obviel.ifaces({ifaces: ['foo', 'bar']}),
            ['foo', 'bar', 'base', 'object']);
    },

    'eggs+qux ifaces': function() {
        obviel.iface('spam');
        obviel.iface('eggs', 'spam');
        obviel.iface('foo');
        obviel.iface('baz', 'foo');
        obviel.iface('qux', 'baz');
        
        assert.equals(
            obviel.ifaces({ifaces: ['eggs', 'qux']}),
            ['eggs', 'qux', 'spam', 'baz', 'foo', 'base', 'object']);
    },

    'basic extendsIface': function() {
        obviel.iface('a');
        obviel.iface('b');
        obviel.iface('combined1', 'a', 'b');
        obviel.iface('combined2');
        obviel.extendsIface('combined2', 'a');
        obviel.extendsIface('combined2', 'b');
        assert.equals(obviel.ifaces('combined1'), obviel.ifaces('combined2'));
    },

    'extendsIface non-existent iface': function() {
        obviel.iface('foo');
        assert.exception(function() {
            obviel.extendsIface('nonexistent', 'foo');
        }, 'IfaceError');
    },

    'extendsIface from non-existent iface': function() {
        obviel.iface('existent');
        assert.exception(function() {
            obviel.extendsIface('existent', 'foo');
        }, 'IfaceError');
    },
    
    'error on recursion': function() {
        obviel.iface('x');
        obviel.iface('y', 'x');
        assert.exception(function() {
            obviel.extendsIface('x', 'y');
        }, 'IfaceError');
    }

    // 'iface as well as ifaces property': function() {

    // }
    
});

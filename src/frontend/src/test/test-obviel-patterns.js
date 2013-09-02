/*global obviel:false, buster:false */

var assert = buster.assert;

var messages = [];

var testel = function() {
    return $(document.createElement('div'));
};

var patternsTestCase = buster.testCase('patterns tests', {
    setUp: function() {
        messages = [];
    },
    tearDown: function() {
        messages = [];
    },

    'messages': function() {
        obviel.view({
            iface: 'message',
            render: function() {
                messages.push(this.obj);
                }
            });
        
        var feedbackMessages = [
            { iface: 'message',
              message: 'one'},
            { iface: 'message',
              message: 'two'}
        ];
        
        var feedback = {
            iface: 'multi',
            objects: feedbackMessages
        };

        var el = testel();
        
        el.render(feedback);
        assert.equals(messages, feedbackMessages);
    },
    
    'events': function(done) {
        
        var feedbackEvents = [
            { iface: 'event',
              name: 'a'},
            { iface: 'event',
              name: 'b'}
            ];
        
        var feedback = {
            iface: 'multi',
            objects: feedbackEvents
        };
        
        
        var el = testel();
        
        var triggeredEvents = [];
        
        el.bind('a', function() {
            triggeredEvents.push('a');
        });
        
        el.bind('b', function() {
            triggeredEvents.push('b');
            done();
        });
        
        el.render(feedback);
        
        assert.equals(triggeredEvents, ['a', 'b']);
    },
    
    'redirect': function() {
        /* thanks to the general obviel patterns, target can be a url as well */
        
        var redirect = {
            iface: 'redirect',
            target: {
                iface: 'redirected'
            }
        };
        
        var redirected = false;
        
        obviel.view({
            iface: 'redirected',
            render: function() {
                redirected = true;
            }
        });

        var el = testel();
        
        el.render(redirect);
        
        assert(redirected);
    }

});
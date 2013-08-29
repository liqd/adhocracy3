(function($, obviel) {
    // enter key
    var KEYCODE = 13;

    //var conn = new obviel.sync.LocalStorageConnection('todos');
    var conn = new obviel.sync.HttpConnection();
    
    var _ = obviel.i18n.translate('todos');
    
    // the application model
    var todos = {
        iface: 'todos',
        items: []
    };
    
    // XXX these are pretty empty; can we get rid of them entirely?
    // maybe not anymore once we have JS events configured
    obviel.sync.mapping({
        iface: 'todos',
        source: {
            'update': {
                finder: function() {
                    return todos;
                }
            }
        },
        target: {
            update: {
                event: 'update'
            },
            touch: {
                event: 'update'
            },
            add: {
                http: {
                    response: obviel.sync.actionProcessor
                },
                event: 'update'
            },
            remove: {
                event: 'update'
            },
            refresh: {
                http: {
                    url: function(m) { return '/todos'; },
                    responseTransformer: function(orig) {
                        var i, item,
                            items = [];
                        for (i = 0; i < orig.items.length; i++) {
                            item = orig.items[i];
                            item.iface = 'todo';
                            items.push(item);
                        }
                        return {
                            iface: 'todos',
                            items: items,
                            addUrl: orig.addUrl,
                            removeUrl: orig.removeUrl
                        };
                    }
                }
            }
        }
    });
    
    obviel.sync.mapping({
        iface: 'todo',
        target: {
            update: {
                event: 'update'
            },
            touch: {
                event: 'update'
            }
        }
    });

    obviel.sync.mapping({
        iface: 'todo-editing',
        target: {
            update: {
                event: 'update'
            },
            touch: {
                event: 'update'
            }

        }
    });

    
    // create a special stats model from the todos
    var getStats = function(todos) {
        var remaining = 0;
        var done = 0;
        var amount = 0;
        $.each(todos.items, function(index, todo) {
            if (todo.done) {
                done += 1;
            } else {
                remaining += 1;
            }
            amount += 1;
        });
        return {iface: 'stats', remaining: remaining, done: done,
                amount: amount};
    };
    
    // a view for the whole todos application
    obviel.view({
        iface: 'todos',
        obvtScript: 'obvt-todos',
        objectEvents: {
            update: 'rerender',
            updateStats: 'updateStats'
        },
        render: function() {
            $('#new-todo').focus();
            this.updateStats();
        },
        updateStats: function() {
            var stats = getStats(this.obj);
            if (stats.amount) {
                $('#toggle-all').get(0).checked = !stats.remaining;
                $('footer', this.el).render(stats);
                $('footer', this.el).show();
            } else {
                $('footer', this.el).hide();
            }
        },
        createOnEnter: function(ev) {
            if (ev.keyCode !== KEYCODE) {
                return;
            }
            var value = $('#new-todo').val();
            if (value === '') {
                return;
            }
            var m = this.mutator();
            var newObj = {iface: 'todo', done: false, title: value};
            m.get('items').push(newObj);
        },
        toggleAll: function() {
            var done = $('#toggle-all').get(0).checked;
            var m = this.mutator().get('items');
            var i;
            for (i = 0; i < this.obj.items.length; i++) {
                m.get(i).touch('done', done);
            }
        }
    });

    // a view for the stats
    obviel.view({
        iface: 'stats',
        obvtScript: 'obvt-todo-stats',
        clearCompleted: function() {
            var m = conn.mutator(todos),
                toRemove = [];
            $.each(todos.items, function(index, item) {
                if (item.done) {
                    toRemove.push(item);
                }
            });
            $.each(toRemove, function(index, item) {
                m.get('items').remove(item);
            });
        }
    });

    // a view for an individual todo item, not editable
    obviel.view({
        iface: 'todo',
        obvtScript: 'obvt-todo',
        objectEvents: {
            update: 'rerender'
        },
        checked: function(el, variable) {
            if (variable('done')) {
                el.get(0).checked = true;
            }
        },
        render: function() {
            if (this.obj.done) {
                this.el.addClass('done');
            } else {
                this.el.removeClass('done');
            }
        },
        edit: function() {
            var m = this.mutator();
            m.touch('iface', 'todo-editing');
        },
        toggle: function() {
            var m = this.mutator();
            m.touch('done', !this.obj.done);
            // XXX how do we handle updateStats case?
            $(todos).trigger('updateStats');
        },
        clear: function() {
            conn.mutator(todos).get('items').remove(this.obj);
        }
    });

    // a view for an editable todo item
    obviel.view({
        iface: 'todo-editing',
        obvtScript: 'obvt-todo-editing',
        objectEvents: {
            update: 'rerender'
        },
        render: function() {
            $('input.edit', this.el).focus();
        },
        updateOnEnter: function(ev) {
            if (ev.keyCode === KEYCODE) {
                this.close();
            }
        },
        close: function() {
            var value = $('input.edit', this.el).val();
            if (!value) {
                conn.mutator(todos).get('items').remove(this.obj);
                return;
            }
            var m = this.mutator();
            m.set('title', value);
            m.touch('iface', 'todo');
        } 
    });
    

    // XXX initialization can be summarized in one call like this
    // obviel.init(todos, '#app', connection, 'nl_NL');
    // or
    // $('#app').initrender(todos, connection, 'nl_NL');
    
    // when the document is ready, load up languages & sync the todos
    // model, and render it when it's done
    $(document).ready(function() {
        obviel.i18n.load().done(function() {
            obviel.i18n.setLocale('nl_NL').done(function() {
                fakeTodosHttpServer.enable();
                conn.init(todos).done(function() {
                    $('#app').render(todos);
                });
            });
        });
    });
}(jQuery, obviel));
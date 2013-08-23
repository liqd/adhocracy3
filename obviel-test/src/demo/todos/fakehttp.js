/* a fake http server for todos */

var fakeTodosHttpServer = {};

(function(module) {
    
    var todos = [{id: 1, title: 'Hello'}];
    
    var json_headers = { "Content-Type": "application/json"};

    var todoIds = 100;
    
    module.enable = function() {
        var server = sinon.fakeServer.create();
        server.autoRespond = true;
        
        server.respondWith('GET', '/todos', function(request) {
            var i, todo;
            console.log("GET /todos");
            for (i = 0; i < todos.length; i++) {
                todo = todos[i];
                // hack update url directly into todo item, but will work
                todo.updateUrl = '/todos/' + todo.id + '/update'; 
            }
            request.respond(200, json_headers,
                            JSON.stringify({
                                addUrl: '/todos/add',
                                removeUrl: '/todos/remove',
                                items: todos
                            }));
        });
        
        server.respondWith('POST', '/todos/add', function(request) {
            var item = JSON.parse(request.requestBody);
            console.log("POST /todos/add " + request.requestBody);
            todos.push(item);
            item.id = todoIds;
            todoIds++;
            item.updateUrl = '/todos/' + item.id + '/update';
            request.respond(200, json_headers,
                            JSON.stringify({
                                name: 'update',
                                obj: item
                            }));
        });
        
        server.respondWith('POST', '/todos/remove', function(request) {
            var i,
            ids = JSON.parse(request.requestBody),
            idSet = {},
            newTodos = [];
            console.log("POST /todos/remove " + request.requestBody);
            for (i = 0; i < ids.length; i++) {
                idSet[ids[i]] = true;
            }
            for (i = 0; i < todos.length; i++) {
                if (idSet[todos[i].id] !== undefined) {
                    continue;
                }
                newTodos.push(todos[i]);
            }
            todos = newTodos;
            request.respond(200, json_headers,
                            JSON.stringify([]));
        });
        
        server.respondWith('POST', /\/todos\/(\d+)\/update/, function(request, id) {
            var i, todo, key,
                updated = JSON.parse(request.requestBody);
            console.log("POST /todos/" + id + "/update " + request.requestBody);
            for (i = 0; i < todos.length; i++) {
                todo = todos[i];
                if (todo.id === id) {
                    for (key in updated) {
                        todo[key] = updated[key];
                    }
                }
            }
            request.respond(200, json_headers,
                            JSON.stringify({}));
        });
    };
        
}(fakeTodosHttpServer));

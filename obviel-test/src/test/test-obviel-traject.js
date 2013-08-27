/*global buster:false, obviel:false */

var assert = buster.assert;
var refute = buster.refute;

var traject = obviel.traject;

var trajectTestCase = buster.testCase("traject tests", {
    "simple steps": function() {
        assert.equals(traject.parse('a/b/c'), ['a', 'b', 'c']);
    },

    "simple steps starting slash": function() {
        assert.equals(traject.parse('/a/b/c'), ['a', 'b', 'c']);
    },
    
    "steps with variable": function() {
        assert.equals(traject.parse('a/$B/c'), ['a', '$B', 'c']);
    },
    
    "steps with double variable": function() {
        assert.exception(function() {
            traject.parse('foo/$a/baz/$a');
        }, 'ParseError');
    },
    
    "subpatterns": function() {
        assert.equals(traject.subpatterns(['a', '$B', 'c']),
                  [['a'],
                   ['a', '$B'],
                   ['a', '$B', 'c']]);
    },
    
    "patterns resolve full path": function() {
        var patterns = new traject.Patterns();

        var lookup = function(variables) {
            return {iface: 'obj', 'b': variables.b, 'd': variables.d};
        };

        patterns.register('a/$b/c/$d', lookup);

        var root = { iface: 'root'};
        
        var obj = patterns.resolve(root, 'a/B/c/D');

        assert.equals(obj.trajectName, 'D');
        assert.equals(obj.iface, 'obj');
        assert.equals(obj.b, 'B');
        assert.equals(obj.d, 'D');
        
        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'c');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'B');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'a');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.iface, 'root');
    },

    "custom default lookup": function() {
        var patterns = new traject.Patterns();
        patterns.setDefaultLookup(function() {
            return {iface: 'customDefault'};
        });
        
        var lookup = function(variables) {
            return {iface: 'obj', 'b': variables.b, 'd': variables.d};
        };

        patterns.register('a/$b/c/$d', lookup);

        var root = { iface: 'root'};
        
        var obj = patterns.resolve(root, 'a/B/c/D');

        assert.equals(obj.trajectName, 'D');
        assert.equals(obj.iface, 'obj');
        assert.equals(obj.b, 'B');
        assert.equals(obj.d, 'D');
        
        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'c');
        assert.equals(obj.iface, 'customDefault');

        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'B');
        assert.equals(obj.iface, 'customDefault');

        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'a');
        assert.equals(obj.iface, 'customDefault');

        obj = obj.trajectParent;
        assert.equals(obj.iface, 'root');

    },

    "patterns resolve stack full path": function() {
        var patterns = new traject.Patterns();

        var lookup = function(variables) {
            return {iface: 'obj', 'b': variables.b, 'd': variables.d};
        };

        patterns.register('a/$b/c/$d', lookup);

        var root = { iface: 'root'};

        var l = ['a', 'B', 'c', 'D'];
        l.reverse();
        
        var obj = patterns.resolveStack(root, l);

        assert.equals(obj.trajectName, 'D');
        assert.equals(obj.iface, 'obj');
        assert.equals(obj.b, 'B');
        assert.equals(obj.d, 'D');
        
        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'c');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'B');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'a');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.iface, 'root');
    },

    "patterns consume stack full path": function() {
        var patterns = new traject.Patterns();

        var lookup = function(variables) {
            return {iface: 'obj', 'b': variables.b, 'd': variables.d};
        };

        patterns.register('a/$b/c/$d', lookup);

        var root = { iface: 'root'};

        var l = ['a', 'B', 'c', 'D'];
        l.reverse();
        
        var r = patterns.consumeStack(root, l);

        assert.equals(r.unconsumed, []);
        assert.equals(r.consumed, ['a', 'B', 'c', 'D']);

        var obj = r.obj;
        
        assert.equals(obj.trajectName, 'D');
        assert.equals(obj.iface, 'obj');
        assert.equals(obj.b, 'B');
        assert.equals(obj.d, 'D');
        
        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'c');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'B');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'a');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.iface, 'root');
    },

    "patterns resolve partial path": function() {
        var patterns = new traject.Patterns();

        var lookup = function(variables) {
            return {iface: 'obj', 'b': variables.b, 'd': variables.d};
        };

        patterns.register('a/$b/c/$d', lookup);

        var root = { iface: 'root'};
        
        var obj = patterns.resolve(root, 'a/B/c');

        assert.equals(obj.trajectName, 'c');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'B');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'a');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.iface, 'root');
    },


    "patterns consume stack partial": function() {
        var patterns = new traject.Patterns();

        var lookup = function(variables) {
            return {iface: 'obj', 'b': variables.b, 'd': variables.d};
        };

        patterns.register('a/$b/c/$d', lookup);

        var root = { iface: 'root'};

        var l = ['a', 'B', 'c'];
        l.reverse();
        
        var r = patterns.consumeStack(root, l);

        assert.equals(r.unconsumed, []);
        assert.equals(r.consumed, ['a', 'B', 'c']);

        var obj = r.obj;

        assert.equals(obj.trajectName, 'c');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'B');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.trajectName, 'a');
        assert.equals(obj.iface, 'default');

        obj = obj.trajectParent;
        assert.equals(obj.iface, 'root');
    },

    "patterns resolve impossible path": function() {
        var patterns = new traject.Patterns();

        var lookup = function(variables) {
            return {iface: 'obj', 'b': variables.b, 'd': variables.d};
        };

        patterns.register('a/$b/c/$d', lookup);

        var root = { iface: 'root'};

        assert.exception(function() {
            patterns.resolve(root, 'B/c/D');
        }, 'ResolutionError');
    },

    "patterns resolve stack impossible path": function() {
        var patterns = new traject.Patterns();

        var lookup = function(variables) {
            return {iface: 'obj', 'b': variables.b, 'd': variables.d};
        };

        patterns.register('a/$b/c/$d', lookup);

        var root = { iface: 'root'};

        var l = ['B', 'c', 'D'];
        l.reverse();

        assert.exception(function() {
            patterns.resolveStack(root, l);
        }, 'ResolutionError');
        
    },

    "patterns consume stack impossible path": function() {
        var patterns = new traject.Patterns();

        var lookup = function(variables) {
            return {iface: 'obj', 'b': variables.b, 'd': variables.d};
        };

        patterns.register('a/$b/c/$d', lookup);

        var root = { iface: 'root'};

        var l = ['B', 'c', 'D'];
        l.reverse();
        
        var r = patterns.consumeStack(root, l);

        assert.equals(r.obj, root);
        assert.equals(r.unconsumed, ['D', 'c', 'B']);
        assert.equals(r.consumed, []);
    },

    "resolve to lookup that returns null": function() {
        var patterns = new traject.Patterns();

        var lookup = function(variables) {
            var result = parseInt(variables.id, 10);
            if (isNaN(result)) {
                return null;
            }
            return {iface: 'obj', id: result};
        };

        patterns.register('models/$id', lookup);
        var root = {iface: 'root'};
        
        assert.exception(function() {
            patterns.resolve(root, 'models/notAnInt');
        }, 'ResolutionError');
    },

    "resolve to lookup that returns undefined": function() {
        var patterns = new traject.Patterns();

        var data = {
            'a': {iface: 'something'},
            'b': {iface: 'something'}
        };
        
        var lookup = function(variables) {
            return data[variables.id]; // will return undefined if not found
        };

        patterns.register('models/$id', lookup);
        var root = {iface: 'root'};

        assert.same(patterns.resolve(root, 'models/a'), data.a);
        
        assert.exception(function() {
                patterns.resolve(root, 'models/unknown');
        }, 'ResolutionError');

    },

    "consume to lookup that returns null": function() {
        var patterns = new traject.Patterns();

        var lookup = function(variables) {
            var result = parseInt(variables.id, 10);
            if (isNaN(result)) {
                return null;
            }
            return {iface: 'obj', id: result};
        };

            patterns.register('models/$id', lookup);
        var root = {iface: 'root'};
        
        var r = patterns.consume(root, 'models/notAnInt');

        assert.equals(r.unconsumed, ['notAnInt']);
        assert.equals(r.consumed, ['models']);
            assert.equals(r.obj.trajectName, 'models');
            assert.equals(r.obj.trajectParent, root);
        
    },

    "multiple registrations resolve to child": function() {
        var patterns = new traject.Patterns();

        var departmentLookup = function(variables) {
            return {iface: 'department', departmentId: variables.departmentId};
        };
        
        var employeeLookup = function(variables) {
            return {
                iface: 'employee',
                departmentId: variables.departmentId,
                employeeId: variables.employeeId
                };
        };
        
        patterns.register(
            'departments/$departmentId',
            departmentLookup);
        patterns.register(
            'departments/$departmentId/employees/$employeeId',
            employeeLookup);

        var root = {iface: 'root'};

        var obj = patterns.resolve(root, 'departments/1/employees/10');

        assert.equals(obj.iface, 'employee');
            assert.equals(obj.departmentId, '1');
        assert.equals(obj.employeeId, '10');
    },


    "multiple registrations consume to child with extra": function() {
        var patterns = new traject.Patterns();

        var departmentLookup = function(variables) {
            return {iface: 'department', departmentId: variables.departmentId};
        };
        
        var employeeLookup = function(variables) {
            return {
                iface: 'employee',
                departmentId: variables.departmentId,
                employeeId: variables.employeeId
            };
        };
        
        patterns.register(
            'departments/$departmentId',
            departmentLookup);
        patterns.register(
            'departments/$departmentId/employees/$employeeId',
            employeeLookup);

            var root = {iface: 'root'};

            var r = patterns.consume(root, 'departments/1/employees/10/index');

        assert.equals(r.unconsumed, ['index']);
        assert.equals(r.consumed, ['departments', '1', 'employees', '10']);
        
        var obj = r.obj;
        assert.equals(obj.iface, 'employee');
        assert.equals(obj.departmentId, '1');
        assert.equals(obj.employeeId, '10');
    },

    "multiple registrations resolve to parent": function() {
        var patterns = new traject.Patterns();

        var departmentLookup = function(variables) {
            return {iface: 'department', departmentId: variables.departmentId};
        };
        
        var employeeLookup = function(variables) {
            return {
                iface: 'employee',
                departmentId: variables.departmentId,
                employeeId: variables.employeeId
            };
        };
        
        patterns.register(
                'departments/$departmentId',
                departmentLookup);
        patterns.register(
            'departments/$departmentId/employees/$employeeId',
            employeeLookup);

        var root = {iface: 'root'};

        var obj = patterns.resolve(root, 'departments/1');

        assert.equals(obj.iface, 'department');
        assert.equals(obj.departmentId, '1');
    },


    "multiple registrations consume to parent with extra": function() {
        var patterns = new traject.Patterns();

        var departmentLookup = function(variables) {
            return {iface: 'department', departmentId: variables.departmentId};
        };
        
        var employeeLookup = function(variables) {
            return {
                iface: 'employee',
                departmentId: variables.departmentId,
                    employeeId: variables.employeeId
            };
        };
        
        patterns.register(
            'departments/$departmentId',
            departmentLookup);
        patterns.register(
            'departments/$departmentId/employees/$employeeId',
            employeeLookup);

        var root = {iface: 'root'};

        var r = patterns.consume(root, 'departments/1/index');

        assert.equals(r.unconsumed, ['index']);
        assert.equals(r.consumed, ['departments', '1']);
        
        var obj = r.obj;
        assert.equals(obj.iface, 'department');
        assert.equals(obj.departmentId, '1');
    },


    "multiple registrations resolve to nonexistent": function() {
        var patterns = new traject.Patterns();

        var departmentLookup = function(variables) {
            return {iface: 'department', departmentId: variables.departmentId};
        };
        
        var employeeLookup = function(variables) {
            return {
                iface: 'employee',
                departmentId: variables.departmentId,
                employeeId: variables.employeeId
            };
        };
        
        patterns.register(
            'departments/$departmentId',
            departmentLookup);
        patterns.register(
            'departments/$departmentId/employees/$employeeId',
            employeeLookup);

        var root = {iface: 'root'};

        assert.exception(function() {
            patterns.resolve(root, 'foo/1/bar');
        }, 'ResolutionError');
        
    },


    "overlapping patterns": function() {
        var patterns = new traject.Patterns();

        var departmentLookup = function(variables) {
            return {iface: 'department', departmentId: variables.departmentId};
        };
        
        var employeeLookup = function(variables) {
            return {
                iface: 'employee',
                departmentId: variables.departmentId,
                employeeId: variables.employeeId
            };
        };

        var specialDepartmentLookup = function(variables) {
            return {
                iface: 'specialDepartment'
            };
        };

        var specialEmployeeLookup = function(variables) {
                return {
                    iface: 'specialEmployee',
                    employeeId: variables.employeeId
                };
        };

        patterns.register(
                'departments/$departmentId',
            departmentLookup);
        patterns.register(
            'departments/$departmentId/employees/$employeeId',
            employeeLookup);
        patterns.register('departments/special',
                          specialDepartmentLookup);
        
        var root = {iface: 'root'};

        var obj = patterns.resolve(root, 'departments/1/employees/10');
        assert.equals(obj.iface, 'employee');

        obj = patterns.resolve(root, 'departments/1');
        
        assert.equals(obj.iface, 'department');

        obj = patterns.resolve(root, 'departments/special');
        assert.equals(obj.iface, 'specialDepartment');

        assert.exception(function() {
            patterns.resolve(root, 'departments/special/employees/10');
        }, 'ResolutionError');

        // now register sub path for special

        patterns.register('departments/special/employees/$employeeId',
                          specialEmployeeLookup);

        obj = patterns.resolve(root, 'departments/special/employees/10');
        assert.equals(obj.iface, 'specialEmployee');
        assert.equals(obj.employeeId, '10');
        
    },

/* XXX bunch of tests to do with interface overrides; registering for
   a sub-interface of root definitely won't do anything yet at the moment

   testLookupOverride
   testLookupOverrideRootStaysTheSame
   testLookupExtraPath
   testLookupExtraPathAbsentWithRoot
   testLookupOverrideInMidPath
   testLookupOriginalInMidPath
   testOverrideVariableNames
   testConflictInOverrideVariableNames
   testResolvedConflictInOverrideVariableNames
   testRegisterPatternOnInterface
*/

    "conflicting variable names": function() {
        var patterns = new traject.Patterns();
        
            var departmentLookup = function(variables) {
                return {iface: 'department', departmentId: variables.departmentId};
            };
        
        var employeeLookup = function(variables) {
            return {
                iface: 'employee',
                departmentId: variables.departmentId,
                employeeId: variables.employeeId
            };
        };
        
        patterns.register(
            'departments/$departmentId', departmentLookup);
        
        assert.exception(function() {
            patterns.register('departments/$otherId', departmentLookup);
        }, 'RegistrationError');
        
        assert.exception(function() {
            patterns.register('departments/$otherId/employees/employeeId',
                              employeeLookup);
        }, 'RegistrationError');
    },

    "conflicting converters": function() {
            var patterns = new traject.Patterns();

            var departmentLookup = function(variables) {
                return {iface: 'department', departmentId: variables.departmentId};
            };

        var employeeLookup = function(variables) {
            return {
                iface: 'employee',
                departmentId: variables.departmentId,
                employeeId: variables.employeeId
            };
        };

        patterns.register('departments/$departmentId', departmentLookup);
        assert.exception(function() {
            patterns.register('departments/$departmentId:int',
                              departmentLookup);
        }, 'RegistrationError');

        assert.exception(function() {
            patterns.register(
                'departments/$departmentId:int/employees/$employeeId',
                    employeeLookup);
        }, 'RegistrationError');
        
    },

    "match int": function() {
        var patterns = new traject.Patterns();

        var lookup = function(variables) {
            return {iface: 'obj', v: variables.v};
        };

        patterns.register('a/$v:int', lookup);

        var root = {iface: 'root'};

        var obj = patterns.resolve(root, 'a/1');

        assert.same(obj.v, 1);

        assert.exception(function() {
            patterns.resolve(root, 'a/notAnInt');
        }, 'ResolutionError');
        
    },

    "consume mismatch int": function() {
        var patterns = new traject.Patterns();

        var lookup = function(variables) {
            return {iface: 'obj', v: variables.v};
        };

        patterns.register('a/$v:int', lookup);

        var root = {iface: 'root'};

        var r = patterns.consume(root, 'a/notAnInt');

            assert.equals(r.unconsumed, ['notAnInt']);
        assert.equals(r.consumed, ['a']);
        assert.equals(r.obj.trajectName, 'a');
        assert.equals(r.obj.trajectParent, root);
        
    },

    "unknown converter": function() {
        var patterns = new traject.Patterns();

        var lookup = function(variables) {
            return {iface: 'obj', v: variables.v};
        };

        assert.exception(function() {
            patterns.register('a/$v:foo', lookup);
        }, 'RegistrationError');
        
    },

    "new converter": function() {
        var patterns = new traject.Patterns();
        patterns.registerConverter('float', function(v) {
            var result = parseFloat(v);
            if (isNaN(result)) {
                return null;
            }
            return result;
        });
            
        var lookup = function(variables) {
            return {iface: 'obj', v: variables.v};
        };

        patterns.register('a/$v:float', lookup);

        var root = {iface: 'root'};
        
        var obj = patterns.resolve(root, 'a/1.1');
        assert.same(obj.v, 1.1);
    },

    "converter locate": function() {
        var patterns = new traject.Patterns();

        var lookup = function(variables) {
            return {iface: 'obj', v: variables.v};
            };

            patterns.register('a/$v:int', lookup);

        var args = function(obj) {
            return {'v': obj.v };
        };

        patterns.registerInverse('obj', 'a/$v:int', args);
        
        var root = {iface: 'root'};

        var obj = {iface: 'obj', v: 3};

        patterns.locate(root, obj);

        assert.same(obj.trajectName, '3');
    }

});

    
var _departments = null;
var _department = {};
var _employees = null;
var _employee = {};
var _calls = [];

var identityDepartments = function(variables) {
    _calls.push("departments");
    if (_departments !== null) {
        return _departments;
    }
    _departments = { iface: 'departments'};
    return _departments;
};

var identityDepartment = function(variables) {
    _calls.push('department ' + variables.departmentId);
    var department = _department[variables.departmentId];
    if (department === undefined) {
        department = _department[variables.departmentId] = {
            iface: 'department',
            departmentId: variables.departmentId
        };
    }
    return department;
};

var identityEmployees = function(variables) {
    _calls.push("employees " + variables.departmentId);
    if (_employees !== null) {
        return _employees;
    }
    _employees = {
        iface: 'employees',
        departmentId: variables.departmentId
    };
    return _employees;
};

var identityEmployee = function(variables) {
    _calls.push('department ' + variables.departmentId +
                ' employee ' + variables.employeeId);
    var employee = _employee[variables.employeeId];
    if (employee === undefined) {
        employee = _employee[variables.employeeId] = {
            iface: 'employee',
            departmentId: variables.departmentId,
            employeeId: variables.employeeId
        };
    }
    return employee;
};

var departmentsArguments = function(departments) {
    return {};
};

var departmentArguments = function(department) {
    return {
        departmentId: department.departmentId
    };
};

var employeesArguments = function(employees) {
    return {
        departmentId: employees.departmentId
    };
};

var employeeArguments = function(employee) {
    return {
        departmentId: employee.departmentId,
        employeeId: employee.employeeId
    };
};


var getIdentityPatterns = function() {
    var patterns = new traject.Patterns();
    

    patterns.register(
        'departments', identityDepartments);
    patterns.register(
        'departments/$departmentId',
        identityDepartment);
    patterns.register(
        'departments/$departmentId/employees', identityEmployees);
    patterns.register(
        'departments/$departmentId/employees/$employeeId',
        identityEmployee);
    
    patterns.registerInverse(
        'departments',
        'departments',
        departmentsArguments);
    patterns.registerInverse(
        'department',
        'departments/$departmentId',
        departmentArguments);
    patterns.registerInverse(
        'employees',
        'departments/$departmentId/employees',
        employeesArguments);
    patterns.registerInverse(
        'employee',
        'departments/$departmentId/employees/$employeeId',
        employeeArguments);
    return patterns;
};

var trajectInverseTestCase = buster.testCase("traject inverse tests", {
    setUp: function() {
        _departments = null;
        _department = {};
        _employees = null;
        _employee = {};
        _calls = [];
    },
    tearDown: function() {
    },
    
    "inverse": function() {
        var patterns = getIdentityPatterns();
            var root = { iface: 'root'};
            
        var employee = {iface: 'employee', departmentId: 1, employeeId: 2};
        
        patterns.locate(root, employee);
        
            assert.equals(employee.trajectName, '2');
        var employees = employee.trajectParent;
            assert.equals(employees.trajectName, 'employees');
        var department = employees.trajectParent;
        assert.equals(department.trajectName, '1');
        var departments = department.trajectParent;
        assert.equals(departments.trajectName, 'departments');
            assert.equals(departments.trajectParent, root);
    },

    "identity": function() {
            var patterns = getIdentityPatterns();
        var root = {iface: 'root'};

        var employee1 = patterns.resolve(
            root, 'departments/1/employees/2');
        var employee2 = patterns.resolve(
            root, 'departments/1/employees/2');
        assert.same(employee1, employee2);
        var employee3 = patterns.resolve(
            root, 'departments/1/employees/3');
        refute.equals(employee1, employee3);
        },

    "no recreation": function() {
        var patterns = getIdentityPatterns();
        var root = {iface: 'root'};

        var employee = identityEmployee({departmentId: '1',
                                         employeeId: '2'});
        patterns.locate(root, employee);
        assert.equals(_calls, ['department 1 employee 2',
                           'employees 1',
                           'department 1',
                           'departments']);
        _calls = [];

        // won't create anything next time
            patterns.locate(root, employee);
        assert.equals(_calls, []);
    },

    "cannot locate": function() {
        var patterns = getIdentityPatterns();
        var root = {iface: 'root'};

        var foo = {iface: 'foo'};
        assert.exception(function() {
            patterns.locate(root, foo);
        }, 'LocationError');

    },


    "no recreation of departments": function() {
        var patterns = getIdentityPatterns();
        var root = {iface: 'root'};

        var department = identityDepartment({departmentId: '1'});
        patterns.locate(root, department);

        _calls = [];
        // it won't recreate departments the second time as it'll
        // find a department object with a parent
        var employee = identityEmployee({departmentId: '1',
                                         employeeId: '2'});
        patterns.locate(root, employee);
        assert.equals(_calls, ['department 1 employee 2',
                           'employees 1',
                           'department 1']);
    },

    "no recreation of department": function() {
        var patterns = getIdentityPatterns();
        var root = {iface: 'root'};

        var employees = identityEmployees({departmentId: '1'});
        patterns.locate(root, employees);

        _calls = [];
        // it won't recreate department the second time as it'll
        // find a employees object with a parent
        var employee = identityEmployee({departmentId: '1',
                                         employeeId: '2'});
        patterns.locate(root, employee);
        assert.equals(_calls, ['department 1 employee 2', 'employees 1']);
    },

    "no recreation of department after resolve": function() {
            var patterns = getIdentityPatterns();
        var root = {iface: 'root'};

        patterns.resolve(root, 'departments/1/employees');
        
        _calls = [];
        // it won't recreate department the second time as it'll
        // find a employees object with a parent
        var employee = identityEmployee({departmentId: '1',
                                         employeeId: '2'});
        patterns.locate(root, employee);
        assert.equals(_calls, ['department 1 employee 2', 'employees 1']);
    },

    "inverse non string name": function() {
        var patterns = getIdentityPatterns();

        var root = {iface: 'root'};

        // use integers here, not strings
        var employee = identityEmployee({departmentId: 1,
                                             employeeId: 2});

        patterns.locate(root, employee);
        assert.equals(employee.trajectName, '2');
    },

    "inverse twice": function() {
        var patterns = getIdentityPatterns();

        var root = {iface: 'root'};
        
        var employee = identityEmployee({departmentId: '1',
                                         employeeId: '2'});
        var otherEmployee = identityEmployee({departmentId: '1',
                                              employeeId: '3'});
        
        patterns.locate(root, employee);
        patterns.locate(root, otherEmployee);
        
        assert.equals(employee.trajectName, '2');
            assert.equals(otherEmployee.trajectName, '3');
    },

    "generate path": function() {
        var patterns = getIdentityPatterns();

        var root = {iface: 'root'};
        
        var employee = identityEmployee({departmentId: '1',
                                         employeeId: '2'});

            var path = patterns.path(root, employee);
        assert.equals(path, 'departments/1/employees/2');
    },

    "patterns method": function() {
        var departments = {
            alpha: { iface: 'department', title: 'Alpha'},
            beta: {iface: 'department', title: 'Beta'},
            gamma: {iface: 'department', title: 'Gamma'}
        };
        
        var getDepartment = function(variables) {
            return departments[variables.departmentName];
        };

        var getDepartmentVariables = function(department) {
            for (var departmentName in departments) {
                if (department === departments[departmentName]) {
                    return {departmentName: departmentName};
                }
            }
            return null;
        };
        
            var patterns = new traject.Patterns();
        
        patterns.pattern(
            'department',
            'departments/$departmentName',
            getDepartment,
            getDepartmentVariables);


        var root = {iface: 'root'};
        
        assert.same(patterns.resolve(root, 'departments/alpha'),
                    departments.alpha);
        assert.equals(patterns.path(root, departments.alpha),
                      'departments/alpha');
        assert.equals(patterns.path(root, departments.beta),
                      'departments/beta');
        
    },

    "inverse not found": function() {
        var departments = {
            alpha: { iface: 'department', title: 'Alpha'},
            beta: {iface: 'department', title: 'Beta'},
            gamma: {iface: 'department', title: 'Gamma'}
        };
        
        var getDepartmentVariables = function(department) {
            for (var departmentName in departments) {
                if (department === departments[departmentName]) {
                    return {departmentName: departmentName};
                }
            }
            return null;
        };
        
        var patterns = new traject.Patterns();
        
        patterns.registerInverse(
            'department',
            'departments/$departmentName',
            getDepartmentVariables);


        var root = {iface: 'root'};

        assert.exception(function() {
            patterns.path(root, {iface: 'department'});
        }, 'LocationError');
    
    }

});
                                     

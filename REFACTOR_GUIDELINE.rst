Refactor guideline
==================

For refactoring we follow mostly the rules from the chapter "Smells and hints"
from the book "Clean Code" by Robert C. Martin, 2008.
Every new developer should read this book.

Clean Code short summary:
-------------------------

Common Principles:
++++++++++++++++++

* Single Responsibility principle (SRP): only one reason to change behavior/code
* Open closed Principle (OCP): open for extensions (new classes,..), closed for modification
* Don't repeat yourself (DRY)
* Separation of Concern
* follow/create standards for naming, code structure and styles
* You ain't gonna need it (YAGNI)

Readability:
++++++++++++
    * easy to understand and extend by others
    * readable code instead of comments
    * less code
    * good placed and clear responsibility (place code where the reader expect it)

Variable naming:
++++++++++++++++

     * explicit, show intention and maybe context information
     * no misleading names
     * distinction between concepts (get, append, add,..)

Variables:
++++++++++

     * define close to where there are uses
     
function name/arguments:
++++++++++++++++++++++++

    * verb * Noun (explain abstraction level and if possible arguments)
      not not long, you may use  good keyword arguments instead
    * prefer 0 or 1 argument, max 3
    * kwargs for optional arguments, never use them like positional arguments

functions:
++++++++++

    * short
    * max 2 indention level
    * do only "one thing"
        * one level of abstraction (can you divded sections? or extract a helper function with different name?=
        * one down story of to paragraphs (TO X do a, TO X do b,.. X == function name)
        * one return statement,
        * no switch [only deep buried polymorphism: abstract class, factory,..)]
        * Command Query Separation (no side effects, use descriptive naming):
            * change state object
            * query information
            * change/return argument
            * create object
        * separate error handling (easier to read and to extend)
    * prefer not to change the argument objects, never mutate default kwargs

class name:
+++++++++++

     * show responsibility
     * explicit distinction of generic "concepts", if needed domain specific concepts
     * no context information (for example domain specific suffix ("Adhocracy") or type ("String")

Classes:
++++++++

    * SRP, OCP
    * high cohesion: all methods should share the class variables, if not split class
    * small
    * private functions below first public function that depends on it

Objects:
++++++++

   * data structures: direct access to variables
   * objects: hide data structure, present public "behavior" methods for this objects

   * procedural: easy to add new functions
                 difficult to add new data structures (every functions need to check datatype, maybe Open/Close Principle violated
   * OO with polymorphic methods: easy to add new data structures
                                difficult to add new functions (need to extend all subclasses/implementer)
   * Law of Demeter: own variables / methods: ok
                     foreign data structures: ok
                     foreign object: use only public methods
                     no train wrecks: call().call()

Exceptions:
+++++++++++

   * do not return/accept None without need or accept wrong arguments (exeption: ease unit tests) (makes it hard to find/debug errors)
   * do not use Exception to handle special cases (use Wrapper Classes or throw exception)
   * exception class should make it easy for the caller to handle exception, give contect information, hide third party errors

3+Third party code:
+++++++++++++++++++

    * make Facade to access, catch errors
    * Learning Test to play around and test new versions

Unit_Tests:
+++++++++++

    * first draft +> test success +> refactor code and tests
    * first test with simplest statement +> code +> more tests +> code,.. (only what is needed to pass test)

    * clean code, Domain Specific Test+API
    * structure: Given When Then
    * assert one thing

System:
+++++++

     * Separation of concern
     * Split Creation (factories, start application) , Running (assume every thing is alread created)



Separation of Responsibility for adhocracy packages
---------------------------------------------------

::

    views*
    --------------------------------------------------------------------------------------
    registry* (provide resource/isheet metadata, create resources/isheet, ...)
    -------------------------------------------------------------------------------------------
    base| folder | resources |  sheets  | subscriber* | user management* | search*  | graph*
    -------------------------------------------------------------------------------------------
    interfaces |  utils  | events | schema

    Note: Responsibility for metadata is not yet fully supported by the registry
         * = drop in dependency
         every module:
            must not import from upper level
            must not import from same level
            may import from bottom level
            may import interfaces
         exceptions:
            resource can import from folder/base

separation of concerns or adhocracy
-----------------------------------

::

    running application
    ------------------------------------------------------------------------------------------------------
    start application | drop in dependencies | provide resource/isheet metadata | create resources/isheets

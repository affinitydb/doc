pathSQL Basics: Control
=======================

<!-- TODO: review to make sure conventional terminology is used for each section (event handling, rules, CEP, FSM etc.) -->
<!-- TODO: review examples with singletons, when possible -->
<!-- TODO: augment with more examples, more services etc.; reduce to the most expressive examples -->
<!-- TODO: make sure to start with simple examples (ease in to the topic) -->

*pathSQL* is the name of a dialect of SQL defined for Affinity:
*path* refers to the ease with which chains of relationships can be built, traversed, queried, modified etc.
The result is a language that preserves the declarative (non-procedural) qualities of SQL,
with its well known syntax, but also integrates a very natural, flexible addressing model.

This flexible addressing model is one of the foundations of the new control layer in AffinityNG.
It facilitates the configuration of complex communication stacks, network topologies etc.
And it helps writing event handlers with enough flexibility to express complex logic -
as fluidly and easily as in a standard programming language (no relationship tables, unique keys,
joins, temporary tables etc.).

The examples below demonstrate how within a few declarations ("lines of code"),
one can configure communication channels with sensors, actuators or web services; or
manage state machines, express rules taking other inputs into consideration,
handle complex events, etc.  The resulting code and configurations can be inspected and
grouped by query, modified dynamically, attached by reference or by value to log entries
(e.g. for critical problem reporting and tracking), disseminated to other nodes etc.

These running examples can also be used as a starting point to write your own
applications.

For a review of the database basics, please visit the [pathSQL basics: data](./pathSQL basics [data].md) page.

For a more systematic survey of pathSQL and its commands, please visit the [reference](./pathSQL reference.md).  

To execute an example on this page, either click on it (this will redirect you to the online console),
or click on the blue button in front of it (this will produce results in-place on this page). <div class="pathsql_button_fake">v</div>  

To setup your own runtime environment, please visit this [link](./getting started.md).  

Global Events
-------------

The following small program gives a quick overview of the possibilities opened up by AffinityNG's class event handlers. It creates a class for all
objects containing the `example:signal` property.  It annotates them with the time at which they occurred, and also inserts
a trace object containing additional information (such as a pointer to the event that occurred just before, in `example:"signal/previous"`).

  <code class='pathsql_snippet'>&nbsp;SET PREFIX example: 'http://example';<br>
      CREATE CLASS example:reaction AS SELECT &#42; WHERE EXISTS(example:signal)<br>
      &nbsp;SET afy:onEnter={<br>
      &nbsp;&nbsp;&#36;{UPDATE @self ADD example:"occurred/at"=CURRENT_TIMESTAMP},<br>
      &nbsp;&nbsp;&#36;{INSERT example:"occurred/at"=@self.example:"occurred/at", example:what=@self, example:previous=@class.example:"signal/previous"},<br>
      &nbsp;&nbsp;&#36;{UPDATE @class SET example:"signal/previous"=@self}},<br>
      &nbsp;example:"signal/previous"=0;<br>
      INSERT example:signal=1;<br>
      INSERT example:signal=2;<br>
      INSERT example:signal=3;<br>
      SELECT &#42; WHERE EXISTS(example:"occurred/at");
  </code>

A more substantial code example can be studied via the [pacman](../promo/demos/pacman/pacman.html) demo.

Finite-State Machines (FSMs)
----------------------------

Finite-state machines will provide a more specific context for event detection and handling,
and provide an easy way to connect together a set of decisions and processes.
We will soon update this section with examples.

<!-- TODO: fill with a few examples when FSM data model is finalized -->
<!-- TODO: provide a link to the graphical editor, to show those examples in that form as well -->

Complex Event Processing (CEP)
------------------------------

Built on top of basic events and [FSMs](#finite-state-machines-fsms), CEP enriches the set of events available for
the expression of rules and higher-order FSMs. CEP is not available yet in the alpha release of AffinityNG.

Rules
-----

In a very near future, AffinityNG will provide a new interface to create rules from
a library of conditions and actions. This will provide a higher-level layer in the
programming model, akin to business rules engines. The intent is to make it easy
for non-programmer professionals to adjust and customize their system.

  <code class='pathsql_inert'>
    SET PREFIX model: 'http://example/model/x102';<br>
    RULE model:HeatAlarm :<br>
    &nbsp;model:OutsideTmpChk(25dC) AND model:InsideTmpChk(20dC) -><br>
    &nbsp;model:Pause(INTERVAL'00:15:00'), model:Report('HeatAlarm');
  </code>

<!-- TODO: expand when ready, plus cover the namespace aspects -->
<!-- TODO: show code and provide a live link to visual editor -->

Timers
------

Timers constitute entry points of pure-pathSQL programs (analogous to the thread entry points of traditional C or java programs).

  <code class='pathsql_snippet'>CREATE TIMER _mytimer INTERVAL '00:00:20' AS INSERT _at=CURRENT_TIMESTAMP</code>

  <code class='pathsql_snippet'>
    SET PREFIX control: 'http://example/control';<br>
    SET PREFIX simulation: 'http://example/simulation';<br>
    /\* Declare a base class of signalable entities, triggered by a single timer, below \*/<br>
    CREATE CLASS control:"rt/signalable" AS SELECT * WHERE EXISTS(control:"rt/time/signal");<br>
    /\* Declare a sub-class with a specific event handler \*/<br>
    CREATE CLASS control:"step/handler/on.off.572ef13c" AS SELECT * FROM control:"rt/signalable"<br>
    &nbsp;WHERE control:"sensor/model"=.simulation:"sensor/on.off.572ef13c"<br>
    &nbsp;SET afy:onUpdate={<br>
    &nbsp;&nbsp;&#36;{UPDATE @self SET simulation:tmp1=(SELECT control:"rt/time/signal" FROM @self)},<br>
    &nbsp;&nbsp;&#36;{INSERT<br>
    &nbsp;&nbsp;&nbsp;simulation:"rt/value"=(SELECT simulation:"offset/value" FROM @self) + SIN(@self.simulation:tmp1),<br>
    &nbsp;&nbsp;&nbsp;control:"sensor/model"=(SELECT control:"sensor/model" FROM @self),<br>
    &nbsp;&nbsp;&nbsp;control:handler=(SELECT afy:objectID FROM @class),<br>
    &nbsp;&nbsp;&nbsp;control:at=CURRENT_TIMESTAMP}};<br>
    /\* Declare a few signalable entities \*/<br>
    INSERT control:"rt/time/signal"=0, control:"sensor/name"='sensor A',<br>
    &nbsp;control:"sensor/model"=.simulation:"sensor/on.off.572ef13c", simulation:"offset/value"=100;<br>
    INSERT control:"rt/time/signal"=0, control:"sensor/name"='sensor B',<br>
    &nbsp;control:"sensor/model"=.simulation:"sensor/on.off.572ef13c", simulation:"offset/value"=1000;<br>
    /\* Trigger all signalable entities \*/<br>
    CREATE TIMER control:"rt/source/timer" INTERVAL '00:00:01' AS UPDATE control:"rt/signalable" SET<br>
    &nbsp;control:"rt/time/signal"=EXTRACT(SECOND FROM CURRENT_TIMESTAMP), control:"rt/time"=CURRENT_TIMESTAMP;<br>
  </code>

External Services
-----------------

<!-- Note: here, emphasize specific purpose of services, and configurability; leave service stack and global purpose to 'communication' below -->
<!-- TODO: pre-seed the joyent server with just enough services and demo files for this to actually work online :) -->
<!-- TODO: use PIN URI when fully available -->
<!-- TODO: more examples; either cover all existing services here as a mini-ref, or add a real ref for services... need to cover things like mDNS, HTTP, NFC etc. at least to a usable state; need to document what's not working or unfinished also -->

  <code class='pathsql_snippet'>
    INSERT afy:objectID=.srv:XML, afy:load='xmlservice';<br>
    INSERT afy:service={.srv:IO, .srv:XML}, srv:"XML/config/roots"={'item'}, afy:address(READ_PERM)='rss_sports_01.xml', toto=1;<br>
    INSERT SELECT * WHERE(toto=1);<br>
    UPDATE * SET afy:position=0u WHERE(toto=1);<br>
  </code>

  <code class='pathsql_snippet'>
    INSERT afy:objectID=.srv:XML, afy:load='xmlservice';<br>
    INSERT afy:service={.srv:XML, .srv:IO}, srv:"XML/config/output/qname/prefixes"={'http://purl.org/dc/terms'->'dcterms'}, afy:address=2, toto=2;<br>
    UPDATE * SET afy:content=(SELECT *) WHERE(toto=2);<br>
  </code>

  <code class='pathsql_snippet'>
    INSERT afy:objectID=.srv:http, afy:load='http';<br>
    INSERT afy:objectID=.srv:webapp, afy:load='webapp';<br>
    INSERT afy:objectID=.mywebapp, afy:address='127.0.0.1:4040', afy:listen={.srv:sockets, .srv:HTTPRequest, .srv:webapp, .srv:HTTPResponse, .srv:sockets}, srv:"webapp/config/paths"={'/media/truecrypt1/src/server/src/www/'}, srv:"webapp/config/modes"=WEBAPPMODES#FILE;<br>
  </code>

Communication
-------------

  [Communication PINs](./pathSQL reference [definition].md#communication-pins) are primarily defined by
  their "service stack", i.e. a permutation of [services](./terminology.md#service) with their configuration.
  Services are either endpoints (e.g. sockets, file IO, serial, zigbee), servers (e.g. REST, p2p) or transformations.
  Higher-level communication patterns can be built on top of the four basic types of service stacks:

  1. write stack, e.g.

     <code class='pathsql_snippet'>
       /\* Load the XML external service. \*/<br>
       INSERT afy:objectID=.srv:XML, afy:load='xmlservice';<br>
       /\* Service stack converting to protobuf and sending to file /tmp/output.proto. \*/<br>
       INSERT afy:service={.srv:protobuf, .srv:IO}, afy:address(CREATE_PERM,WRITE_PERM,READ_PERM)='/tmp/output.proto', docsample_key=1000;<br>
       /\* Service stack converting to xml and sending to file /tmp/output.xml. \*/<br>
       INSERT afy:service={.srv:XML, .srv:IO}, afy:address(CREATE_PERM,WRITE_PERM,READ_PERM)='/tmp/output.xml', docsample_key=1001;<br>
       /\* Some example data. \*/<br>
       INSERT x=10, y=20, somename='Fred';<br>
       INSERT x=11, y=21, somename='Tony';<br>
       /\* Send data to the two communication PINs defined in this example. \*/<br>
       UPDATE * SET afy:content=(SELECT * WHERE EXISTS(somename)) WHERE docsample_key={1000, 1001};<br>
     </code>

  2. read stack, e.g

     <code class='pathsql_snippet'>
       /\* Service stack reading protobuf from file /tmp/output.proto. \*/<br>
       INSERT afy:service={.srv:IO, .srv:protobuf}, afy:address(READ_PERM)='/tmp/output.proto', docsample_key=1010;<br>
       /\* Service stack reading xml from file /tmp/output.xml. \*/<br>
       INSERT afy:service={.srv:IO, .srv:XML}, afy:address(READ_PERM)='/tmp/output.xml', docsample_key=1011;<br>
       /\* Just in case, reset seek pointer at the beginning. \*/<br>
       UPDATE * SET afy:position=0u WHERE docsample_key={1010, 1011};<br>
       /\* Read from both communication PINs (protobuf and xml). \*/<br>
       SELECT * WHERE docsample_key={1010, 1011};<br>
     </code>

  3. server stack, e.g.

     <code class='pathsql_snippet'>
       /\* Service stack for a server/listener interpreting a pathSQL request and returning the result as protobuf. \*/<br>
       INSERT x=12, y=22, somename='Jack';<br>
       INSERT x=13, y=23, somename='Ann';<br>
       CREATE LISTENER docsample_listener_protobuf ON '127.0.0.1:8090'<br>
       &nbsp;AS {.srv:sockets, .srv:pathSQL, .srv:affinity, .srv:protobuf, .srv:sockets};<br>
     </code>

     <code class='pathsql_snippet'>
       /\* Service stack for a server/listener interpreting a pathSQL request and returning the result as xml. \*/<br>
       INSERT afy:objectID=.srv:XML, afy:load='xmlservice';<br>
       CREATE LISTENER docsample_listener_xml ON '127.0.0.1:8091'<br>
       &nbsp;AS {.srv:sockets, .srv:pathSQL, .srv:affinity, .srv:XML, .srv:sockets};<br>
     </code>

     <code class='pathsql_snippet'>
       INSERT afy:objectID=.srv:webapp, afy:load='webapp';<br>
       INSERT afy:objectID=.srv:http, afy:load='http';<br>
       INSERT afy:objectID=.docsample_webapp, afy:address='127.0.0.1:8092',<br>
       &nbsp;afy:listen={.srv:sockets, .srv:HTTPRequest, .srv:webapp, .srv:HTTPResponse, .srv:sockets},<br>
       &nbsp;srv:"webapp/config/paths"={'/tmp/www'}, srv:"webapp/config/modes"=WEBAPPMODES#FILE;<br>
     </code>  

  4. request stack, e.g.

     <code class='pathsql_snippet'>
       /\* Service stack for a client request in pathSQL returning the server's result as protobuf. \*/<br>
       INSERT afy:service={.srv:pathSQL, .srv:sockets, .srv:protobuf}, afy:address='127.0.0.1:8090',<br>
       &nbsp;afy:request=${SELECT * WHERE EXISTS(somename)}, docsample_key=1020;<br>
     </code>

     <code class='pathsql_snippet'>
       INSERT afy:objectID=.srv:XML, afy:load='xmlservice';<br>
       /\* Service stack for a client request in pathSQL returning the server's result as xml. \*/<br>
       INSERT afy:service={.srv:pathSQL, .srv:sockets, .srv:XML}, afy:address='127.0.0.1:8091',<br>
       &nbsp;afy:request=${SELECT * WHERE EXISTS(somename)}, docsample_key=1021;<br>
     </code>

     <code class='pathsql_snippet'>
       /\* Read the server via our client request. \*/<br>
       SELECT * WHERE docsample_key={1020 /\*,1021*\/ };<br>
     </code>

<!-- TODO: more complex/varied stacks (refs/structs, more config, more services, server without response etc.) -->
<!-- TODO: more detail / more specific references to complete doc -->
<!-- TODO: FSM integration (e.g. security nego) -->
<!-- TODO: review all existing material (test4mvsql, tests, ...) - make sure all is coverered -->

<!--
Synergy
-------

The very open nature of [PINs](./terminology.md#pin), combined with the way all active components
are configured, allows to merge together mutliple functionalities into a single PIN naturally,
with automatic handling in the kernel of implied aspects. 
In a next revision of the doc, we will provide concrete examples.
<!-- TODO agree on exact definition, scenarios, convincing examples --
-->

Code Querying
-------------

<!-- TODO: review (more meat) with FSMs -->
<!-- TODO: an example with FT search (MATCH AGAINST + an indexed prop; take that opportunity to review all usage of the modeling.py data model [indexing meta]) -->

  <code class='pathsql_snippet'>
    /\* Get all existing classes.\*/<br>
    SELECT * FROM afy:Classes;<br>
    /\* Get all existing classes of a package.\*/<br>
    SELECT * FROM afy:Classes WHERE BEGINS(afy:objectID, 'http://pacman1/');</br>
  </code>

  <code class='pathsql_snippet'>
    /\* Get all FSM states.\*/<br>
    SELECT * WHERE EXISTS(afy:transition);<br>
  </code>

  <code class='pathsql_snippet'>
    /\* Find all classes inspecting a property name containing 'square'. \*/<br>
    SELECT * FROM afy:Classes WHERE CONTAINS(afy:predicate, 'square');</br>
    /\* Find all timers inspecting a property name containing 'signal'. \*/<br>
    SELECT * FROM afy:Timers WHERE CONTAINS(afy:action, 'signal');</br>
  </code>

  The [FSM](../console.html#tab-fsm) and [Rule Assistant](../console.html#tab-ruleassistant) tabs of the web console
  make use of these capabilites to help the user narrow down and pinpoint relevant code visualizations,
  for a given circumstance (e.g. show all code using a certain [property](./terminology.md#property) or
  [class](./terminology.md#class)).

Logging
-------

The example provided [above](#global-events) gives a hint of how current time, current topology,
current state, current code etc. can be attached to a log entry, by reference or by value.
In the near future, we will provide a more significant example.

<!-- TODO: show how current time, current topology, current state, current code etc.
can be attached to a log entry, by ref or by value; easiest would be to attach to the timer above,
if bug #357 is fixed in time; otherwise, build a complete mini-example here (relatively trivial to do) -->

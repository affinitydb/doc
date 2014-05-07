pathSQL Basics: Control
=======================

<!-- TODO: review to make sure conventional terminology is used for each section (event handling, rules, CEP, FSM etc.) -->
<!-- TODO: review examples with singletons, when possible (to avoir errors on reruns, without extra code...) -->
<!-- TODO: augment with more examples, more services etc.; reduce to the most expressive examples -->
<!-- TODO: make sure to start with simple examples (ease in to the topic) -->

*pathSQL* is the name of a dialect of SQL defined for Affinity:
*path* refers to the ease with which chains of relationships can be built, traversed, queried, modified etc.
The result is a language that preserves the declarative (non-procedural) qualities of SQL,
with its well known syntax, while also integrating a very natural, flexible addressing model.

This flexible addressing model is one of the foundations of the new control layer in AffinityNG.
It facilitates the configuration of complex communication stacks and [FSMs](./terminology.md#fsm),
as well as the modeling of graphs (e.g. representation of a network topology).
It also helps writing event handlers, by providing enough flexibility to express complex logic -
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
      &nbsp;/\* Whenever a PIN containing the property 'example:signal' appears, it will trigger the action defined here. \*/<br>
      &nbsp;SET afy:onEnter={<br>
      &nbsp;&nbsp;/\* Mark the PIN with a timestamp (of when it was classified). \*/<br>
      &nbsp;&nbsp;&#36;{UPDATE @self ADD example:"occurred/at"=CURRENT_TIMESTAMP},<br>
      &nbsp;&nbsp;/\* Maintain a snapshot log of the chain of events. \*/<br>
      &nbsp;&nbsp;&#36;{INSERT example:"occurred/at"=@self.example:"occurred/at", example:what=@self,<br>
      &nbsp;&nbsp;&nbsp;example:previous=@ctx.example:"signal/previous"},<br>
      &nbsp;&nbsp;/\* Keep track of the last created event. \*/<br>
      &nbsp;&nbsp;&#36;{UPDATE @ctx SET example:"signal/previous"=@self}},<br>
      &nbsp;example:"signal/previous"=0;<br>
      /\* Generate a few events, for demonstration purposes. \*/<br>
      INSERT example:signal=1;<br>
      INSERT example:signal=2;<br>
      INSERT example:signal=3;<br>
      /\* Show the results. \*/<br>
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
the expression of rules and higher-order FSMs. CEP is not available yet in the alpha2 release of AffinityNG.

Rules
-----

Rules represent a higher-level layer in the programming model. They are typically used to hide implementation details,
by presenting the logic of a system in quasi-natural language (provided that names were chosen appropriately by the programmers).
The intent is to make it easy for non-programmer professionals to understand, adjust and customize their system.  

A rule is defined by a conjunction of conditions (i.e. a set of conditions that must all be met),
and a list of actions. Internally a rule functions very much like a [non-indexed class (aka simple event handler)](./terminology.md#class) 
(indeed, the rule declaration mechanism can be thought of as a templating or macro system for classes).
A rule reacts to changes on a PIN (n.b. all conditions of a rule relate to the same PIN;
for multi-PIN events, see the sections on [CEP](#complex-event-processing-cep) and [FSMs](#finite-state-machines-fsms)).
The `@self` variable in a rule's conditions and actions refers to the PIN being tested or processed by the rule.

A small example:

  <code class='pathsql_snippet'>
    /\* Internal implementation provided by the system programmer. \*/<br>
    SET PREFIX model: 'http://example/model/';<br>
    CREATE CONDITION model:OutsideTmpChk AS model:OutsideTemp > :0;<br>
    CREATE CONDITION model:InsideTmpChk AS (SELECT ABS(AVG(model:InsideTempReadings) - :0)) > 5dC;<br>
    CREATE ACTION model:Pause AS UPDATE @self SET model:PauseUntil=CURRENT_TIMESTAMP + :0,<br>
    &nbsp;model:PausedAt=CURRENT_TIMESTAMP;<br>
    CREATE ACTION model:Report AS INSERT model:GlobalMessage=:0, model:FromSample=@self;<br>
    &nbsp;<br>
    /\* Actual rule, visible to the non-programmer professional. \*/<br>
    RULE model:HeatAlarm :<br>
    &nbsp;model:OutsideTmpChk(25dC) AND model:InsideTmpChk(20dC) -><br>
    &nbsp;model:Pause(INTERVAL'00:15:00'), model:Report('HeatAlarm');<br>
    &nbsp;<br>
    /\* Demonstrating the behavior... \*/<br>
    INSERT model:sample=1, model:OutsideTemp=20dC, model:InsideTempReadings={18dC, 20dC, 21dC, 20.5dC};<br>
    INSERT model:sample=2, model:OutsideTemp=40dC, model:InsideTempReadings={18dC, 20dC, 21dC, 20.5dC};<br>
    INSERT model:sample=3, model:OutsideTemp=20dC, model:InsideTempReadings={48dC, 40dC, 21dC, 20.5dC};<br>
    INSERT model:sample=4, model:OutsideTemp=40dC, model:InsideTempReadings={48dC, 40dC, 21dC, 20.5dC};
  </code>

<!-- TODO: provide a live link to visual editor -->

Timers
------

Timers constitute entry points of pure-pathSQL programs (analogous to the thread entry points of traditional C or java programs).

  <code class='pathsql_snippet'>CREATE TIMER _mytimer INTERVAL '00:00:20' AS INSERT _at=CURRENT_TIMESTAMP</code>

  <code class='pathsql_snippet'>
    SET PREFIX control: 'http://example/control';<br>
    SET PREFIX simulation: 'http://example/simulation';<br>
    /\* Declare a base class of signalable entities, triggered by a single timer, below. \*/<br>
    CREATE CLASS control:"rt/signalable" AS SELECT &#42; WHERE EXISTS(control:"rt/time/signal");<br>
    /\* Declare a sub-class with a specific event handler. \*/<br>
    CREATE CLASS control:"step/handler/on.off.572ef13c" AS SELECT &#42; FROM control:"rt/signalable"<br>
    &nbsp;WHERE control:"sensor/model"=.simulation:"sensor/on.off.572ef13c"<br>
    &nbsp;SET afy:onUpdate={<br>
    &nbsp;&nbsp;&#36;{UPDATE @auto SET simulation:tmp1=(SELECT control:"rt/time/signal" FROM @self)},<br>
    &nbsp;&nbsp;&#36;{INSERT<br>
    &nbsp;&nbsp;&nbsp;simulation:"rt/value"=(SELECT simulation:"offset/value" FROM @self) + SIN(@auto.simulation:tmp1),<br>
    &nbsp;&nbsp;&nbsp;control:"sensor/model"=(SELECT control:"sensor/model" FROM @self),<br>
    &nbsp;&nbsp;&nbsp;control:handler=(SELECT afy:objectID FROM @ctx),<br>
    &nbsp;&nbsp;&nbsp;control:at=CURRENT_TIMESTAMP}};<br>
    /\* Declare a few signalable entities. \*/<br>
    INSERT control:"rt/time/signal"=0, control:"sensor/name"='sensor A',<br>
    &nbsp;control:"sensor/model"=.simulation:"sensor/on.off.572ef13c", simulation:"offset/value"=100;<br>
    INSERT control:"rt/time/signal"=0, control:"sensor/name"='sensor B',<br>
    &nbsp;control:"sensor/model"=.simulation:"sensor/on.off.572ef13c", simulation:"offset/value"=1000;<br>
    /\* Trigger all signalable entities. \*/<br>
    CREATE TIMER control:"rt/source/timer" INTERVAL '00:00:05' AS UPDATE control:"rt/signalable" SET<br>
    &nbsp;control:"rt/time/signal"=EXTRACT(SECOND FROM CURRENT_TIMESTAMP), control:"rt/time"=CURRENT_TIMESTAMP;
  </code>

External Services & Communications
----------------------------------

[Communication PINs](./pathSQL reference [definition].md#communication-pins), aka "CPINs", are primarily defined by
their "service stack".  The CPIN contains its service stack via either one of these properties: `afy:service` or `afy:listen`.
The former case represents passive CPINs (i.e. CPINs that will only do something when explicitly SELECT-ed or UPDATE-ed),
whereas listeners can be considered active or autonomous, in the sense that no SELECT or UPDATE on them is required
for them to produce changes.  A service stack is a collection of [services](./terminology.md#service),
complemented by additional configuration properties stored on the same CPIN.
Services in the stack can play different roles:

  * source or sink (e.g. sockets, file IO, MODBUS, BLE, serial, zigbee etc.)
  * request-response server (e.g. webapp, affinity)
  * transformation (e.g. XML, JSON, protobuf, HTTP request/response etc.)

Four basic types of service stacks, demonstrated below, emerge from these building blocks.
With these and the database kernel, a multitude of communication patterns can be implemented.

<span style='color:#444;'>
*Note:* Individual services and their configurations will be described in detail [here](./pathSQL reference [definition].md#services).  
*Note:* In the text that follows, comments in the code fragments complement the narrative.
</span>  

&nbsp;  

<!-- TODO: more examples, especially with VDEV and emergent GUI (i.e. a 'real' interaction with device and program); either cover all existing services here as a mini-ref, or add a real ref for services... need to cover things like mDNS, HTTP, NFC etc. at least to a usable state; need to document what's not working or unfinished also -->
<!-- TODO: more complex/varied stacks (refs/structs, more config, more services, server without response etc.) -->
<!-- TODO: FSM integration (e.g. security nego) -->

  0. Let's start with a common setup for all subsequent examples.  Note that these examples
     are inter-dependent; to avoid unexpected results, please execute them in their natural top-down sequence.  

  <code class='pathsql_snippet'>
    /\* Make sure the required services are loaded. \*/<br>
    CREATE LOADER _xml AS 'XML';<br>
    CREATE LOADER _http AS 'http';<br>
    CREATE LOADER _webapp AS 'webapp';<br>
    /\* Produce debugging traces in stdout (for demonstration purposes, when running locally). \*/<br>
    SET TRACE ALL COMMUNICATIONS;<br>
    /\* Gather some of the examples below together, to set a better example. \*/<br>
    CREATE CLASS docsamples AS SELECT &#42; WHERE docsample_key IN :0;
  </code>

  1. request stack  

  <code class='pathsql_snippet'>
    /\* Request example: setup a XML fetcher via HTTP client. \*/<br>
    /\* Here we read a CD catalog example from w3schools. \*/<br>
    /\* (Could be anything: RSS feed, accessing the REST interface of an online database, etc.). \*/<br>
    INSERT afy:objectID='my_xml_reader1', afy:service={.srv:HTTP, .srv:sockets, .srv:HTTP, .srv:XML},<br>
    &nbsp;afy:address='www.w3schools.com', http:url='/xml/cd_catalog.xml',<br>
    &nbsp;http:"request/fields"={'Accept'->'application/xml', 'Host'->'www.w3schools.com'}, XML:"config/roots"={'CD'};
  </code>

  <code class='pathsql_snippet'>
    /\* Run the request example. \*/<br>
    SELECT &#42; FROM #my_xml_reader1;
  </code>
  <!-- TODO: show INSERT SELECT, when it will be fixed (pending issue of cross references over output stream)... -->

  <code class='pathsql_snippet'>
    /\* Modify the URL fetched by the reader example. \*/<br>
    UPDATE RAW #my_xml_reader1 SET http:url='/xml/simple.xml', XML:"config/roots"={'food'};<br>
    /\* Fetch again. \*/<br>
    SELECT &#42; FROM #my_xml_reader1;
  </code>

  2. simple write stacks  

  <code class='pathsql_snippet'>
    /\* Writer example: transform PINs into a XML document and save to disk as a file, into /tmp. \*/<br>
    SET PREFIX testxml: 'http://test/xml';<br>
    INSERT afy:objectID='my_xml_writer1', afy:service={.srv:XML, .srv:IO},<br>
    &nbsp;afy:address(CREATE_PERM, WRITE_PERM)='/tmp/mytest.xml',<br>
    &nbsp;XML:"config/output/qname/prefixes"={'http://test/xml'->'testxml'},<br>
    &nbsp;docsample_key=1000;
  </code>

  <code class='pathsql_snippet'>
    /\* Create a few PINs and demonstrate, i.e. produce /tmp/mytest.xml. \*/<br>
    SET PREFIX testxml: 'http://test/xml';<br>
    INSERT (testxml:x, testxml:y, testxml:name) VALUES <br>
    &nbsp;(10,10,'Fred'), (20,20,'Jack'), (30,30,'Alicia'), (40,40,'Jane');<br>
    UPDATE #my_xml_writer1 SET afy:content=(SELECT &#42; WHERE EXISTS(testxml:name));
  </code>

  <code class='pathsql_snippet'>
    /\* Another example: transform PINs into protobuf this time. \*/<br>
    INSERT afy:service={.srv:protobuf, .srv:IO},<br>
    &nbsp;afy:address(CREATE_PERM, WRITE_PERM)='/tmp/mytest.proto',<br>
    &nbsp;docsample_key=1001;
  </code>

  <code class='pathsql_snippet'>
    /\* Demonstrate, i.e. produce /tmp/mytest.proto. \*/<br>
    /\* Note: By changing to 'FROM docsamples(@[1000, 1001]), \*/<br>
    /\*       one would simultaneously produce both mytest.xml and mytest.proto files. \*/<br>
    SET PREFIX testxml: 'http://test/xml';<br>
    UPDATE docsamples(1001) SET afy:content=(SELECT &#42; WHERE EXISTS(testxml:name));
  </code>

  3. server stacks  

  <code class='pathsql_snippet'>
    /\* Server example 1: a small web server serving files under /tmp, such as the one we just produced above. \*/<br>
    CREATE LISTENER my_http_server1 ON 4040 AS {.srv:sockets, .srv:HTTP, .srv:webapp, .srv:HTTP, .srv:sockets} SET<br>
    &nbsp;srv:"webapp/config/paths"={'/tmp/'},<br>
    &nbsp;srv:"webapp/config/modes"=WEBAPPMODES#FILE;<br>
    /\* A corresponding client, fetching and parsing the xml document we had produced in the previous example. \*/<br>
    INSERT afy:objectID='my_http_client1', afy:service={.srv:HTTP, .srv:sockets, .srv:HTTP, .srv:XML},<br>
    &nbsp;afy:address='127.0.0.1:4040', http:url='/mytest.xml',<br>
    &nbsp;http:"request/fields"={'Accept'->'&#42;/&#42;'}, http:method='GET';
  </code>

  <code class='pathsql_snippet'>
    /\* Demonstrate, i.e. fetch the document served by our server. \*/<br>
    SELECT &#42; FROM #my_http_client1;
  </code>

  <code class='pathsql_snippet'>
    /\* Server example 2: a server/listener interpreting a pathSQL request and returning the result as XML. \*/<br>
    CREATE LISTENER docsample_listener_protobuf ON 4041<br>
    &nbsp;AS {.srv:sockets, .srv:pathSQL, .srv:affinity, .srv:XML, .srv:sockets};<br>
    <br>
    /\* Server example 3: same as 2, but in protobuf. \*/<br>
    CREATE LISTENER docsample_listener_xml ON 4042<br>
    &nbsp;AS {.srv:sockets, .srv:pathSQL, .srv:affinity, .srv:protobuf, .srv:sockets};<br>
    <br>
    /\* Setup corresponding fetchers. \*/<br>
    SET PREFIX testxml: 'http://test/xml';<br>
    INSERT afy:service={.srv:pathSQL, .srv:sockets, .srv:XML}, afy:address='127.0.0.1:4041',<br>
    &nbsp;afy:request=&#36;{SELECT &#42; WHERE EXISTS(testxml:name)},<br>
    &nbsp;docsample_key=1010;<br>
    INSERT afy:service={.srv:pathSQL, .srv:sockets, .srv:protobuf}, afy:address=4042,<br>
    &nbsp;afy:request=&#36;{SELECT &#42; WHERE EXISTS(testxml:name)},<br>
    &nbsp;docsample_key=1011;
  </code>

  <code class='pathsql_snippet'>
    /\* Demonstrate server examples 2 and 3. \*/<br>
    SELECT &#42; FROM docsamples(@[1010, 1011]);
  </code>

  4. simple read stacks  

  <code class='pathsql_snippet'>
    /\* Reader example 1: to read mytest.xml, produced above. \*/<br>
    INSERT afy:service={.srv:IO, .srv:XML},<br>
    &nbsp;afy:address(READ_PERM)='/tmp/mytest.xml',<br>
    &nbsp;docsample_key=1020;<br>
    <br>
    /\* Reader example 2: to read mytest.proto, produced above. \*/<br>
    /\* Note: We could also reuse the same reader; here, we also want to demonstrate \*/<br>
    /\*       simultaneous reading of various formats. \*/<br>
    INSERT afy:service={.srv:IO, .srv:protobuf},<br>
    &nbsp;afy:address(READ_PERM)='/tmp/mytest.proto',<br>
    &nbsp;docsample_key=1021;
  </code>

  <code class='pathsql_snippet'>
    /\* Just in case, reset seek pointers at the beginning of the files. \*/<br>
    UPDATE docsamples(@[1020, 1021]) SET afy:position=0u;<br>
    /\* Demonstrate, i.e. read and parse those files, and produce corresponding PINs. \*/<br>
    SELECT &#42; FROM docsamples(@[1020, 1021]);<br>
    /\* Variation: actually insert the parsed result back into the database (producing clones here). \*/<br>
    -- INSERT SELECT &#42; FROM docsamples(@[1020, 1021]);
  </code>

Sensors & Actuators
-------------------

There are several [services](#external-services-communications) developed for Affinity,
that enable direct interactions with sensors and actuators (e.g. MODBUS, CoAP, BLE, Zigbee etc.),
following the same simple pattern where SELECT reads the latest state available from those sensors,
and where UPDATE writes (be it to trigger actuators, or to modify a sensor's internal state, e.g.
to enable/disable/configure the on-chip sample collection [e.g. turn on&off the sample collection
of a more power-hungry feature or component, on a battery-powered sensor unit]).  

In this section, we'll be using the VDEV virtual device service, a service that emulates
typical interactions with sensors and actuators, to illustrate some of the possibilities
and idioms.  Note: a similar scenario could be developed with real sensors, using something like
BLE instead of VDEV; the main changes would be in terms of configuration of those CPINs.

<span style='color:#444;'>
*Note:* In the text that follows, comments in the code fragments complement the narrative.
</span>  

&nbsp;  

<!-- TODO: could develop a number of representative stories here, e.g. typical PID stuff, robotics, motion, etc. -->
<!-- TODO: somewhere later in the flow, show a comparison with say BLE/MODBUS, to highlight similarities and differences with VDEV;
           emphasize that afy:address + evaluator is all it takes to get started -->

The first story-line we'll be using as an example is an alarm system.  

Let's imagine a contact sensor on a door, informing us of whether
the door is closed:  

  <code class='pathsql_snippet' dependencies='SET PREFIX alrm: &#39;http://example/alarm-system&#39;; SET PREFIX simul: &#39;http://example/alarm-system/simulation&#39;; CREATE LOADER _vdev AS &#39;VDEV&#39;; CREATE ENUMERATION alrm:OUTPUT_TYPES AS {&#39;BOOLEAN&#39;, &#39;REAL&#39;}; CREATE ENUMERATION alrm:DOOR_STATES AS {&#39;OPEN&#39;, &#39;CLOSED&#39;, &#39;LOCKED&#39;}; CREATE CLASS alrm:components AS SELECT &#42; WHERE alrm:"component/id" IN :0; CREATE CLASS simul:homes AS SELECT &#42; WHERE simul:"home/id" IN :0; INSERT simul:"home/id"=&#39;147C&#39;, simul:comment=&#39;Our home state&#39;;'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    SET PREFIX simul: 'http://example/alarm-system/simulation';<br>
    <br>
    /\* Create and configure our first VDEV sensor, which will report the OPEN/CLOSED state of door 1. \*/<br>
  	INSERT afy:service={.srv:VDEV}, afy:objectID=.alrm:my_first_sensor, VDEV:"read/evaluator"=<br>
    &nbsp;&#36;{SELECT simul:"door/state" FROM simul:homes('147C').simul:doors WHERE simul:"door/id"=1};<br>
    <br>
    /\* Add a corresponding virtual door to our environment. \*/<br>
    UPDATE simul:homes('147C') ADD simul:doors=<br>
    &nbsp;(INSERT simul:"door/id"=1, simul:"door/state"=alrm:DOOR_STATES#CLOSED);<br>
    <br>
    /\* Annotate our sensor with meta-data, for our demo app/GUI. \*/<br>
    UPDATE RAW #alrm:my_first_sensor SET alrm:"component/id"=1,<br>
    &nbsp;alrm:"sensor/output/type"=alrm:OUTPUT_TYPES#BOOLEAN;
  </code>

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    <br>
    /\* Test our sensor. \*/<br>
    SELECT &#42; FROM #alrm:my_first_sensor;
  </code>

Note that the virtual state of our environment will be contained in a PIN accessed via `simul:homes('147C')`.
For demonstration purposes, we'll simulate changes in the environment by modifying directly its simulated state.
Then, we'll assess the environment (as we would in real life), using our VDEV sensors.
For example, let's open the door:  

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    SET PREFIX simul: 'http://example/alarm-system/simulation';<br>
    <br>
    /\* This is a simulation step, forcing a door open. \*/<br>
    UPDATE simul:homes('147C').simul:doors SET simul:"door/state"=alrm:DOOR_STATES#OPEN WHERE simul:"door/id"=1;
  </code>

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    <br>
    /\* Here we assess the state of the door via our VDEV sensor. \*/<br>
    SELECT &#42; FROM #alrm:my_first_sensor;<br>
    /\* Same here, with a different (more general) access path to the same sensor. \*/<br>
    SELECT &#42; FROM alrm:components(1);
  </code>

A typical home alarm system may monitor the state of several doors,
windows and locks, as well as other safety parameters such as toxic gases,
fire (in the form of fine particles, or ambient temperature), heat near
the stove, water in the basement, etc.  Let's add more sensors:  

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    SET PREFIX simul: 'http://example/alarm-system/simulation';<br>
    <br>
    /\* Create and configure a few more VDEV sensors. \*/<br>
  	INSERT afy:service={.srv:VDEV}, alrm:"component/id"=2, VDEV:"read/evaluator"=<br>
    &nbsp;&#36;{SELECT simul:"door/state" FROM simul:homes('147C').simul:doors WHERE simul:"door/id"=2};<br>
  	INSERT afy:service={.srv:VDEV}, alrm:"component/id"=3, VDEV:"read/units"=0cm, VDEV:"read/evaluator"=<br>
    &nbsp;&#36;{SELECT simul:"window/state" FROM simul:homes('147C').simul:windows WHERE simul:"window/id"=1};<br>
  	INSERT afy:service={.srv:VDEV}, alrm:"component/id"=4, VDEV:"read/units"=0cm, VDEV:"read/evaluator"=<br>
    &nbsp;&#36;{SELECT simul:"window/state" FROM simul:homes('147C').simul:windows WHERE simul:"window/id"=2};<br>
  	INSERT afy:service={.srv:VDEV}, alrm:"component/id"=5, VDEV:"read/units"=0cm, VDEV:"read/evaluator"=<br>
    &nbsp;&#36;{SELECT simul:"window/state" FROM simul:homes('147C').simul:windows WHERE simul:"window/id"=3};<br>
  	INSERT afy:service={.srv:VDEV}, alrm:"component/id"=6, VDEV:"read/units"=0cm, VDEV:"read/evaluator"=<br>
    &nbsp;&#36;{SELECT simul:"window/state" FROM simul:homes('147C').simul:windows WHERE simul:"window/id"=4};<br>
  	INSERT afy:service={.srv:VDEV}, alrm:"component/id"=7, VDEV:"read/units"=0dC, VDEV:"read/evaluator"=<br>
    &nbsp;&#36;{SELECT simul:temperature FROM simul:homes('147C').simul:floors WHERE simul:floor=1};<br>
  	INSERT afy:service={.srv:VDEV}, alrm:"component/id"=8, VDEV:"read/units"=0dC, VDEV:"read/evaluator"=<br>
    &nbsp;&#36;{SELECT simul:temperature FROM simul:homes('147C').simul:floors WHERE simul:floor=2};<br>
  	INSERT afy:service={.srv:VDEV}, alrm:"component/id"=9, VDEV:"read/units"=0mg, VDEV:"read/evaluator"=<br>
    &nbsp;&#36;{SELECT simul:particles FROM simul:homes('147C').simul:floors WHERE simul:floor=2};<br>
  	INSERT afy:service={.srv:VDEV}, alrm:"component/id"=10, VDEV:"read/evaluator"=<br>
    &nbsp;&#36;{SELECT simul:water FROM simul:homes('147C').simul:floors WHERE simul:floor=1};<br>
    <br>
    /\* Add the corresponding virtual doors, windows etc. to our environment. \*/<br>
    UPDATE simul:homes('147C') ADD simul:doors=<br>
    &nbsp;(INSERT simul:"door/id"=2, simul:"door/state"=alrm:DOOR_STATES#CLOSED);<br>
    UPDATE simul:homes('147C') ADD simul:windows=(INSERT simul:"window/id"=1, simul:"window/state"=0cm);<br>
    UPDATE simul:homes('147C') ADD simul:windows=(INSERT simul:"window/id"=2, simul:"window/state"=5cm);<br>
    UPDATE simul:homes('147C') ADD simul:windows=(INSERT simul:"window/id"=3, simul:"window/state"=0cm);<br>
    UPDATE simul:homes('147C') ADD simul:windows=(INSERT simul:"window/id"=4, simul:"window/state"=20cm);<br>
    UPDATE simul:homes('147C') ADD simul:floors=(INSERT simul:floor=1, simul:temperature=22dC, simul:water=false);<br>
    UPDATE simul:homes('147C') ADD simul:floors=(INSERT simul:floor=2, simul:temperature=24dC, simul:particles=0.002mg);
  </code>  

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    <br>
    /\* Test all our sensors. \*/<br>
    SELECT &#42; FROM alrm:components(@[1,10]);
  </code>  

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    <br>
    /\* By simply adding RAW, show the configuration of all our sensors. \*/<br>
    SELECT RAW &#42; FROM alrm:components(@[1,10]);
  </code>  

An alarm system is typically implemented on a small CPU or microcontroller,
which could run with Affinity.  Let's sketch such an implementation.
First let's define some initial state for our alarm system's controller:  

  <code class='pathsql_snippet' dependencies='SET PREFIX alrm: &#39;http://example/alarm-system&#39;; CREATE ENUMERATION alrm:STATES AS {&#39;UNARMED&#39;, &#39;ARMED_PARTIAL&#39;, &#39;ARMED&#39;}; CREATE CLASS alrm:controllers AS SELECT &#42; WHERE alrm:"home/id" IN :0;'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    <br>
    /\* Create a state for our alarm controller. \*/<br>
    INSERT alrm:"home/id"='147C', alrm:state=alrm:STATES#UNARMED,<br>
    &nbsp;alrm:comment='The controller of our home alarm system for 147C';
  </code>

The alarm system would typically have some actuators, such as
a siren, and LEDs to inform of the current state (n.b. it may also take care of
other things, such as controlling lights and heating while the owners are away).
Let's add actuators to our system:  

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    SET PREFIX simul: 'http://example/alarm-system/simulation';<br>
    <br>
    /\* Create and configure the VDEV actuators. \*/<br>
  	INSERT afy:service={.srv:VDEV}, alrm:"component/id"=100, VDEV:"write/pin"=(SELECT FIRST @ FROM simul:homes('147C')),<br>
    &nbsp;VDEV:"write/property"=.simul:siren;<br>
  	INSERT afy:service={.srv:VDEV}, alrm:"component/id"=101, VDEV:"write/pin"=(SELECT FIRST @ FROM simul:homes('147C')),<br>
    &nbsp;VDEV:"write/property"=.simul:"doors/LED";<br>
  	INSERT afy:service={.srv:VDEV}, alrm:"component/id"=102, VDEV:"write/pin"=(SELECT FIRST @ FROM simul:homes('147C')),<br>
    &nbsp;VDEV:"write/property"=.simul:"windows/LED";<br>
  	INSERT afy:service={.srv:VDEV}, alrm:"component/id"=102, VDEV:"write/pin"=(SELECT FIRST @ FROM simul:homes('147C')),<br>
    &nbsp;VDEV:"write/property"=.simul:"fire/LED";<br>
  	INSERT afy:service={.srv:VDEV}, alrm:"component/id"=102, VDEV:"write/pin"=(SELECT FIRST @ FROM simul:homes('147C')),<br>
    &nbsp;VDEV:"write/property"=.simul:"water/LED";<br>
    <br>
    /\* Add the corresponding virtual state to our environment. \*/<br>
    UPDATE simul:homes('147C') SET<br>
    &nbsp;simul:siren=FALSE,<br>
    &nbsp;simul:"doors/LED"=FALSE,<br>
    &nbsp;simul:"windows/LED"=FALSE,<br>
    &nbsp;simul:"fire/LED"=FALSE,<br>
    &nbsp;simul:"water/LED"=FALSE;
  </code>

Let's try to trigger the `.simul:siren` actuator, and see how that gets reflected
in our virtual environment:  

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    SET PREFIX simul: 'http://example/alarm-system/simulation';<br>
    <br>
    /\* Verify the state of the siren in the virtual environment (should be FALSE). \*/<br>
    SELECT simul:siren FROM simul:homes('147C');<br>
    <br>
    /\* Trigger the siren actuator. \*/<br>
    UPDATE alrm:components(100) SET afy:content=TRUE;<br>
    <br>
    /\* Verify that this action got reflected in the virtual environment. \*/<br>
    SELECT simul:siren FROM simul:homes('147C');
  </code>

Now that we have demonstrated full access, via plain SELECT and UPDATE,
to the sensors and actuators deployed in our environment, it becomes very easy
to add logic to our controller.  For example, a basic behavior would be to
always report the effect of sensors on the corresponding LEDs, but only trigger
the siren when the system is armed.

Two approaches can be considered to monitor the state of our sensors:
polling them periodically or, if the underlying technology allows it, listen to
notifications they emit.  VDEV supports both scenarios, and so do real infrastructures
such as BLE.  In this introductory example let's explore polling:  

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    SET PREFIX simul: 'http://example/alarm-system/simulation';<br>
    <br>
    /\* In response to a time event, gather readings from all sensors, and apply the desired logic. \*/<br>
    CREATE CLASS alrm:"thread/entry" AS SELECT &#42; WHERE alrm:"thread/entry/event" IN :0<br>
    &nbsp;SET afy:onEnter={<br>
    &nbsp;&nbsp;/\* Check our doors sensors. \*/<br>
    &nbsp;&nbsp;&#36;{UPDATE @self SET lDoors=(SELECT VDEV:"read/property" FROM alrm:components(@[1, 2]))},<br>
    &nbsp;&nbsp;/\* Check our windows sensors. \*/<br>
    &nbsp;&nbsp;&#36;{UPDATE @self SET lWindows=(SELECT VDEV:"read/property" FROM alrm:components(@[3, 6]))},<br>
    &nbsp;&nbsp;/\* Check our thermometers. \*/<br>
    &nbsp;&nbsp;&#36;{UPDATE @self SET lThermometers=(SELECT VDEV:"read/property" FROM alrm:components(@[7, 8]))},<br>
    &nbsp;&nbsp;/\* Check our fumes particles. \*/<br>
    &nbsp;&nbsp;&#36;{UPDATE @self SET lFumes=(SELECT VDEV:"read/property" FROM alrm:components(9))},<br>
    &nbsp;&nbsp;/\* Check our water sensor in the basement. \*/<br>
    &nbsp;&nbsp;&#36;{UPDATE @self SET lWater=(SELECT VDEV:"read/property" FROM alrm:components(10))},<br>
    <br>
    &nbsp;&nbsp;/\* Always report alerts from our readings to our LED actuators. \*/<br>
    &nbsp;&nbsp;/\* (Reminder: the basic addressing model we had setup earlier assigned \*/<br>
    &nbsp;&nbsp;/\*            100=siren, 101=doors, 102=windows, 103=fire, 104=water). \*/<br>
    &nbsp;&nbsp;&#36;{UPDATE @self SET lWarnDoors=(SELECT alrm:DOOR_STATES#OPEN IN lDoors FROM @self)},<br>
    &nbsp;&nbsp;&#36;{UPDATE @self SET lWarnWindows=(SELECT MAX(lWindows) < 5cm FROM @self)},<br>
    &nbsp;&nbsp;&#36;{UPDATE @self SET lWarnFire=(SELECT MAX(lThermometers) < 32dC AND MIN(lThermometers) > 8dC AND MAX(lFumes) < 0.5mg FROM @self)},<br>
    &nbsp;&nbsp;&#36;{UPDATE @self SET lWarnWater=(SELECT TRUE IN lWater FROM @self)},<br>
    &nbsp;&nbsp;&#36;{UPDATE alrm:components(101) SET afy:content=@self.lWarnDoors},<br>
    &nbsp;&nbsp;&#36;{UPDATE alrm:components(102) SET afy:content=@self.lWarnWindows},<br>
    &nbsp;&nbsp;&#36;{UPDATE alrm:components(103) SET afy:content=@self.lWarnFire},<br>
    &nbsp;&nbsp;&#36;{UPDATE alrm:components(104) SET afy:content=@self.lWarnWater},<br>
    <br>
    &nbsp;&nbsp;/\* If the alarm system is armed, then trigger the siren; otherwise, shut it down. \*/<br>
    &nbsp;&nbsp;&#36;{UPDATE @auto SET lWarnAny=(SELECT lWarnDoors IS TRUE OR lWarnWindows IS TRUE OR<br>
    &nbsp;&nbsp;&nbsp;lWarnFire IS TRUE OR lWarnWater IS TRUE FROM @self)},<br>
    &nbsp;&nbsp;&#36;{UPDATE alrm:components(100) SET afy:content=@auto.lWarnAny}};<br>
  </code>

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    <br>
    /\* Collect and process one test sample, by triggering alrm:"thread/entry". \*/<br>
    INSERT afy:objectID='my_first_sample', alrm:"thread/entry/event"=CURRENT_TIMESTAMP;
  </code>

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    <br>
    /\* Create a timer that will collect samples every 5 seconds. \*/<br>
    CREATE TIMER alrm:thread INTERVAL '00:00:05' AS INSERT alrm:"thread/entry/event"=CURRENT_TIMESTAMP;
  </code>

In the previous code fragment, we chose to set lDoors, lWindows and so on on `@self`,
which means that each timer event will keep a history of the state of sensors
at that time.  Had we set those results on `@auto` instead, the same logic would have
operated without leaving a verbose trace.  Here's what we got from running so far:

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    SET PREFIX simul: 'http://example/alarm-system/simulation';<br>
    <br>
    /\* Show the run-time time events collected so far. \*/<br>
    SELECT &#42; FROM alrm:"thread/entry";
  </code>

<!-- Here introduce the UI allowing to play with the system -->

We could continue this example with more sophisticated logic, FSMs, rules,
reporting to the cloud via HTTPS, XMPP or other protocols, etc.  Hopefully
this introductory material will inspire you to try more fun things.

Note that to build the "Sensors & Actuators" section that you just read, we needed a few classes and
enumerations, the creation of which we didn't show (to get straight to the point).
Here are their definitions:  

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    SELECT &#42; FROM afy:Classes WHERE BEGINS(afy:objectID, 'http://example/alarm-system/');<br>
    SELECT &#42; FROM afy:Enumerations WHERE BEGINS(afy:objectID, 'http://example/alarm-system/');
  </code>  

<!-- Synergy
The very open nature of [PINs](./terminology.md#pin), combined with the way all active components
are configured, allows to merge together mutliple functionalities into a single PIN naturally,
with automatic handling in the kernel of implied aspects. 
In a next revision of the doc, we will provide concrete examples.
<!-- TODO agree on exact definition, scenarios, convincing examples --
-->

Introspection and Code Querying
-------------------------------

Being together a database, a runtime engine, and a communication hub spanning across
and tying together very diverse sources of information, with all information represented
in a uniform manner (via the PIN), Affinity provides an environment where it becomes easy
to obtain information by query, about states and behaviors that may be opaque, or require
much more labor-intensive inquiry processes in other environments.

For example, following the examples for [communication PINs](#external-services-communications)
in previous sections of this page, one may want to find out all CPINs dealing with XML:  

  <code class='pathsql_snippet'>
    /\* Get all CPINs dealing with XML. \*/<br>
    SELECT RAW &#42; WHERE (.srv:XML IN afy:service) OR (.srv:XML IN afy:listen);
  </code>

There are plenty of other available queries to explore code, data, and relationships
between them, such as:  

  <code class='pathsql_snippet'>
    /\* Get all existing classes. \*/<br>
    SELECT &#42; FROM afy:Classes;<br>
    /\* Get all existing classes of a package. \*/<br>
    SELECT &#42; FROM afy:Classes WHERE BEGINS(afy:objectID, 'http://pacman1/');
  </code>

  <code class='pathsql_snippet'>
    /\* Get all FSM states. \*/<br>
    SELECT &#42; WHERE EXISTS(afy:transition);
  </code>

  <code class='pathsql_snippet'>
    /\* Find all classes inspecting a property name containing 'docsample'. \*/<br>
    SELECT &#42; FROM afy:Classes WHERE CONTAINS(afy:predicate, 'docsample');</br>
    /\* Find all timers inspecting a property name containing 'signal'. \*/<br>
    SELECT &#42; FROM afy:Timers WHERE CONTAINS(afy:action, 'signal');
  </code>

The [FSM](../console.html#tab-fsm) and [Rule Assistant](../console.html#tab-ruleassistant) tabs of the web console
make use of these capabilites to help the user narrow down and pinpoint relevant code visualizations,
for a given circumstance (e.g. show all code using a certain [property](./terminology.md#property) or
[class](./terminology.md#class)).

<!-- TODO: review (more meat) with FSMs -->
<!-- TODO: an example with FT search (MATCH AGAINST + an indexed prop; take that opportunity to review all usage of the modeling.py data model [indexing meta]) -->

Logging
-------

The examples provided above ([events](#global-events) and [rules](#rules)) give a hint of how current time, current topology,
current state, current code etc. could be attached to a log entry (by reference or by value).
In the near future, we will provide a more significant example here.

<!-- TODO: show how current time, current topology, current state, current code etc.
can be attached to a log entry, by ref or by value; easiest would be to attach to the timer above,
if bug #357 is fixed in time; otherwise, build a complete mini-example here (relatively trivial to do) -->

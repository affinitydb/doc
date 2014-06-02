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

The following small program gives a quick overview of the possibilities opened up by AffinityNG's data event handlers. It creates a class for all
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
    CREATE CONDITION model:InsideTmpChk AS (ABS(AVG(model:InsideTempReadings) - :0)) > 5dC;<br>
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
    /\* Only sample 4 should trigger the model:HeatAlarm rule. \*/<br>
    INSERT model:sample=1, model:OutsideTemp=20dC, model:InsideTempReadings={18dC, 20dC, 21dC, 20.5dC};<br>
    INSERT model:sample=2, model:OutsideTemp=40dC, model:InsideTempReadings={18dC, 20dC, 21dC, 20.5dC};<br>
    INSERT model:sample=3, model:OutsideTemp=20dC, model:InsideTempReadings={48dC, 40dC, 21dC, 20.5dC};<br>
    INSERT model:sample=4, model:OutsideTemp=40dC, model:InsideTempReadings={48dC, 40dC, 21dC, 20.5dC};
  </code>

<!-- Review: (SELECT ABS(AVG(...))), or just (ABS(AVG(...)))? -->
<!-- TODO: provide a live link to visual editor -->

Timers
------

Timers constitute entry points of pure-pathSQL programs (analogous to the thread entry points of traditional C or java programs).

  <code class='pathsql_snippet'>CREATE TIMER _mytimer INTERVAL '00:00:30' AS INSERT _at=CURRENT_TIMESTAMP</code>

  <code class='pathsql_snippet'>
    SET PREFIX control: 'http://example/control';<br>
    SET PREFIX simulation: 'http://example/simulation';<br>
    /\* Declare a class to collect results \*/<br>
    CREATE CLASS simulation:results AS SELECT * WHERE EXISTS(simulation:"rt/value");<br>
    /\* Declare a base class of signalable entities, triggered by a single timer, below. \*/<br>
    CREATE CLASS control:"rt/signalable" AS SELECT &#42; WHERE EXISTS(control:"rt/time/signal");<br>
    /\* Declare a sub-class with a specific event handler. \*/<br>
    CREATE CLASS control:"step/handler/on.off.572ef13c" AS SELECT &#42; FROM control:"rt/signalable"<br>
    &nbsp;WHERE control:"sensor/model"=.simulation:"sensor/on.off.572ef13c"<br>
    &nbsp;SET afy:onUpdate={<br>
    &nbsp;&nbsp;&#36;{UPDATE @auto SET simulation:tmp1=(SELECT control:"rt/time/signal" FROM @self)},<br>
    &nbsp;&nbsp;&#36;{INSERT<br>
    &nbsp;&nbsp;&nbsp;simulation:"rt/value"=(SELECT simulation:"offset/value" FROM @self) + SIN(@auto.simulation:tmp1),<br>
    &nbsp;&nbsp;&nbsp;control:"sensor/name"=(SELECT control:"sensor/name" FROM @self),<br>
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

  <code class='pathsql_snippet'>
    SET PREFIX simulation: 'http://example/simulation';<br>
    <br>
    /\* Show results (evolving every 5 seconds... try rerunning this query a few times). \*/<br>
    SELECT * FROM simulation:results;
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
    /\* Note: \*/<br>
    /\* &nbsp;&nbsp;Here we use the PIN declaration form (with an afy:service property); \*/<br>
    /\* &nbsp;&nbsp;in following examples, we'll use CREATE COMMUNICATION PIPELINE instead. \*/<br>
    INSERT afy:objectID='my_xml_reader1', afy:service={.srv:HTTP, .srv:sockets, .srv:HTTP, .srv:XML},<br>
    &nbsp;afy:address='www.w3schools.com', http:url='/xml/cd_catalog.xml',<br>
    &nbsp;http:"request/fields"={'Accept'->'application/xml', 'Host'->'www.w3schools.com'}, XML:"config/roots"={'CD'};
  </code>

  <code class='pathsql_snippet'>
    /\* Run the request example (n.b. this may take a second or two). \*/<br>
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
    CREATE COMMUNICATION PIPELINE my_xml_writer1 AS {.srv:XML, .srv:IO} SET<br>
    &nbsp;afy:address(CREATE_PERM, WRITE_PERM, READ_PERM)='/tmp/mytest.xml',<br>
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
    CREATE COMMUNICATION PIPELINE AS {.srv:protobuf, .srv:IO} SET<br>
    &nbsp;afy:address(CREATE_PERM, WRITE_PERM, READ_PERM)='/tmp/mytest.proto',<br>
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
    CREATE COMMUNICATION PIPELINE my_http_client1 AS {.srv:HTTP, .srv:sockets, .srv:HTTP, .srv:XML} SET<br>
    &nbsp;afy:address='127.0.0.1:4040', http:url='/mytest.xml',<br>
    &nbsp;http:"request/fields"={'Accept'->'&#42;/&#42;'}, http:method='GET';
  </code>

  <code class='pathsql_snippet'>
    /\* Demonstrate, i.e. fetch the document served by our server. \*/<br>
    SELECT &#42; FROM #my_http_client1;
  </code>

  <code class='pathsql_snippet'>
    /\* Server example 2: a server/listener interpreting a pathSQL request and returning the result as XML. \*/<br>
    CREATE LISTENER docsample_listener_xml ON 4041<br>
    &nbsp;AS {.srv:sockets, .srv:pathSQL, .srv:affinity, .srv:XML, .srv:sockets};<br>
    <br>
    /\* Server example 3: same as 2, but in protobuf. \*/<br>
    CREATE LISTENER docsample_listener_protobuf ON 4042<br>
    &nbsp;AS {.srv:sockets, .srv:pathSQL, .srv:affinity, .srv:protobuf, .srv:sockets};<br>
    <br>
    /\* Setup corresponding fetchers. \*/<br>
    SET PREFIX testxml: 'http://test/xml';<br>
    CREATE COMMUNICATION PIPELINE AS {.srv:pathSQL, .srv:sockets, .srv:XML} SET afy:address='127.0.0.1:4041',<br>
    &nbsp;afy:request=&#36;{SELECT &#42; WHERE EXISTS(testxml:name)},<br>
    &nbsp;docsample_key=1010;<br>
    CREATE COMMUNICATION PIPELINE AS {.srv:pathSQL, .srv:sockets, .srv:protobuf} SET afy:address='127.0.0.1:4042',<br>
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
    CREATE COMMUNICATION PIPELINE AS {.srv:IO, .srv:XML} SET<br>
    &nbsp;afy:address(READ_PERM)='/tmp/mytest.xml',<br>
    &nbsp;docsample_key=1020;<br>
    <br>
    /\* Reader example 2: to read mytest.proto, produced above. \*/<br>
    /\* Note: We could also reuse the same reader; here, we also want to demonstrate \*/<br>
    /\*       simultaneous reading of various formats. \*/<br>
    CREATE COMMUNICATION PIPELINE AS {.srv:IO, .srv:protobuf} SET<br>
    &nbsp;afy:address(READ_PERM)='/tmp/mytest.proto',<br>
    &nbsp;docsample_key=1021;
  </code>

  <code class='pathsql_snippet'>
    /\* Just in case, reset seek pointers at the beginning of the files. \*/<br>
    UPDATE RAW docsamples(@[1020, 1021]) SET afy:position=0u;<br>
    /\* Demonstrate, i.e. read and parse those files, and produce corresponding PINs. \*/<br>
    SELECT &#42; FROM docsamples(@[1020, 1021]);<br>
    /\* Variation: actually insert the parsed result back into the database (producing clones here). \*/<br>
    -- INSERT SELECT &#42; FROM docsamples(@[1020, 1021]);
  </code>

<!-- Review: instead of UPDATE RAW, use WITH when it's ready; document those subtleties -->

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

  <code class='pathsql_snippet' loaders='CREATE LOADER _vdev AS &#39;VDEV&#39;;' dependencies='SET PREFIX alrm: &#39;http://example/alarm-system&#39;; SET PREFIX simul: &#39;http://example/alarm-system/simulation&#39;; CREATE ENUMERATION alrm:DOOR_STATES AS {&#39;OPEN&#39;, &#39;CLOSED&#39;, &#39;LOCKED&#39;}; CREATE CLASS alrm:components AS SELECT &#42; WHERE alrm:"component/id" IN :0; CREATE CLASS simul:homes AS SELECT &#42; WHERE simul:"home/id" IN :0; INSERT simul:"home/id"=&#39;147C&#39;, simul:comment=&#39;Our home state&#39;;'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    SET PREFIX simul: 'http://example/alarm-system/simulation';<br>
    <br>
    /\* Create and configure our first VDEV sensor, which will report the OPEN/CLOSED state of door 1. \*/<br>
    INSERT afy:service={.srv:VDEV}, afy:objectID=.alrm:my_first_sensor,<br>
    &nbsp;alrm:"component/id"=1, VDEV:"read/evaluator"=<br>
    &nbsp;&#36;{SELECT simul:"door/state" FROM simul:homes('147C').simul:doors WHERE simul:"door/id"=1};<br>
    <br>
    /\* Add a corresponding virtual door to our environment. \*/<br>
    UPDATE simul:homes('147C') ADD simul:doors=<br>
    &nbsp;(INSERT simul:"door/id"=1, simul:"door/state"=alrm:DOOR_STATES#CLOSED);
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
    /\* Add the corresponding virtual doors, windows etc. to our simulated environment. \*/<br>
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
    INSERT afy:service={.srv:VDEV}, alrm:"component/id"=103, VDEV:"write/pin"=(SELECT FIRST @ FROM simul:homes('147C')),<br>
    &nbsp;VDEV:"write/property"=.simul:"fire/LED";<br>
    INSERT afy:service={.srv:VDEV}, alrm:"component/id"=104, VDEV:"write/pin"=(SELECT FIRST @ FROM simul:homes('147C')),<br>
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

  <code class='pathsql_snippet' pathsql_send_at_completion='event_alarm_system_ready'>
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
    &nbsp;&nbsp;&#36;{UPDATE @self SET lWarnWindows=(SELECT MAX(lWindows) > 10cm FROM @self)},<br>
    &nbsp;&nbsp;&#36;{UPDATE @self SET lWarnFire=(SELECT MAX(lThermometers) > 32dC OR MIN(lThermometers) < 6dC OR MAX(lFumes) > 0.5mg FROM @self)},<br>
    &nbsp;&nbsp;&#36;{UPDATE @self SET lWarnWater=(SELECT TRUE IN lWater FROM @self)},<br>
    &nbsp;&nbsp;&#36;{UPDATE alrm:components(101) SET afy:content=@self.lWarnDoors},<br>
    &nbsp;&nbsp;&#36;{UPDATE alrm:components(102) SET afy:content=@self.lWarnWindows},<br>
    &nbsp;&nbsp;&#36;{UPDATE alrm:components(103) SET afy:content=@self.lWarnFire},<br>
    &nbsp;&nbsp;&#36;{UPDATE alrm:components(104) SET afy:content=@self.lWarnWater},<br>
    <br>
    &nbsp;&nbsp;/\* If the alarm system is armed, then trigger the siren; otherwise, shut it down. \*/<br>
    &nbsp;&nbsp;&#36;{UPDATE @auto SET lArmed=(SELECT FIRST alrm:state FROM alrm:controllers('147C'))},<br>
    &nbsp;&nbsp;&#36;{UPDATE @auto SET lWarnAny=FALSE},<br>
    &nbsp;&nbsp;&#36;{UPDATE @auto SET lWarnAny=(SELECT lWarnDoors IS TRUE OR lWarnWindows IS TRUE OR<br>
    &nbsp;&nbsp;&nbsp;lWarnFire IS TRUE OR lWarnWater IS TRUE FROM @self) WHERE @auto.lArmed<>alrm:STATES#UNARMED},<br>
    &nbsp;&nbsp;&#36;{UPDATE alrm:components(100) SET afy:content=@auto.lWarnAny}};
  </code>

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    <br>
    /\* Collect and process one test sample, by triggering alrm:"thread/entry". \*/<br>
    INSERT alrm:"thread/entry/event"=CURRENT_TIMESTAMP;
  </code>

  <code class='pathsql_snippet'>
    SET PREFIX alrm: 'http://example/alarm-system';<br>
    <br>
    /\* Create a timer that will collect samples every 3 seconds. \*/<br>
    CREATE TIMER alrm:thread INTERVAL '00:00:03' AS INSERT alrm:"thread/entry/event"=CURRENT_TIMESTAMP;
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

The little applet below lets you simulate changes in the environment,
and see how our alarm system reacts (*note:* the system will react asynchronously,
every 3 seconds, as per our `alrm:thread` declaration earlier).
You can combine those interactions with
queries from the console also, and observe the results:

  <code class='pathsql_applet' pathsql_listen_to='event_alarm_system_ready'>
    (function() { return new function(){
      var \_this = this;
      var \_pfxdef = "http://example/alarm-system/simulation";
      var \_pfx = "SET PREFIX simul: '" + \_pfxdef + "'; SET PREFIX alrm: 'http://example/alarm-system';";
      var \_renderHouse = function(pC2d, pO) { pC2d.strokeStyle = '#000'; pC2d.strokeRect(pO.x, pO.y + 20, pO.w, pO.h - 20); pC2d.beginPath(); pC2d.moveTo(pO.x, pO.y + 20); pC2d.lineTo(pO.x + pO.w * 0.5, 0); pC2d.lineTo(pO.x + pO.w, pO.y + 20); pC2d.stroke(); };
      var \_renderDoor = function(pC2d, pO) { pC2d.strokeRect(pO.x, pO.y, pO.w, pO.h); if (typeof(pO.state) == 'string' && pO.state.indexOf('CLOSED') >= 0) { pC2d.beginPath(); pC2d.arc(pO.x + 0.66 * pO.w, pO.y + 0.6 * pO.h, 2, 0, 2 * Math.PI, true); pC2d.stroke(); } else { pC2d.beginPath(); pC2d.moveTo(pO.x, pO.y); pC2d.lineTo(pO.x + pO.w * 0.5, pO.y + pO.h * 0.5), pC2d.lineTo(pO.x + pO.w * 0.5, pO.y + pO.h * 1.5); pC2d.lineTo(pO.x, pO.y + pO.h); pC2d.closePath(); pC2d.stroke(); pC2d.fill(); } };
      var \_renderWindow = function(pC2d, pO) { pC2d.strokeRect(pO.x, pO.y, pO.w, pO.h); var \_lH = pO.h - (pO.h * pO.state / 30); pC2d.fillRect(pO.x, pO.y, pO.w, \_lH); pC2d.moveTo(pO.x, pO.y + \_lH); pC2d.lineTo(pO.x + pO.w, pO.y + \_lH); pC2d.stroke(); };
      var \_renderThermo = function(pC2d, pO) { pC2d.fillStyle = '#000'; pC2d.fillText(Math.round(pO.state), pO.x - 10, pO.y); var \_lXc = pO.x + 0.5 * pO.w, \_lTpct = Math.min(40.0, Math.max(0.0, pO.state)) / 40.0, \_lTh = pO.h - 8; pC2d.beginPath(); pC2d.arc(\_lXc, pO.y + 5, 4, 0, Math.PI, true); pC2d.arc(\_lXc, pO.y + pO.h - 5, 4, Math.PI, 2 * Math.PI, true); pC2d.closePath(); pC2d.stroke(); pC2d.fillStyle = '#f00'; pC2d.strokeRect(\_lXc - 2, pO.y + 4, 4, \_lTh); pC2d.fillRect(\_lXc - 2, pO.y + 4 + (1 - \_lTpct) * \_lTh, 4, \_lTpct * \_lTh); };
      var \_renderParticules = function(pC2d, pO) { /\* TODO \*/ };
      var \_renderWater = function(pC2d, pO) { /\* TODO \*/ };
      var \_renderAlarm = function(pC2d, pO) { pC2d.fillStyle = '#000'; pC2d.fillText(pO.name, pO.x + 12, pO.y + 3); pC2d.fillStyle = pO.state ? '#f00' : '#0f0'; pC2d.beginPath(); pC2d.arc(pO.x + 5, pO.y, 3, 0, 2 * Math.PI, true); pC2d.closePath(); pC2d.stroke(); pC2d.fill(); };
      var \_renderArmed = function(pC2d, pO) { pC2d.fillStyle = '#000'; pC2d.fillText(pO.name, pO.x + 12, pO.y + pO.h); pC2d.fillStyle = pO.state ? '#f00' : '#eee'; pC2d.fillRect(pO.x, pO.y, pO.w, pO.h); pC2d.strokeRect(pO.x, pO.y, pO.w, pO.h); };
      var \_changeDoor = function(pO, pPos) { pO.state = ((typeof(pO.state) == 'string' && pO.state.indexOf('CLOSED') >= 0) ? 'alrm:DOOR\_STATES#OPEN' : 'alrm:DOOR\_STATES#CLOSED'); return \_pfx + 'UPDATE simul:homes(' + "'147C'" + ').simul:doors SET simul:"door/state"=' + pO.state + ' WHERE simul:"door/id"=' + pO.compId; };
      var \_changeWindow = function(pO, pPos) { pO.state = (30 * Math.min(pO.h, Math.max(0, pO.h - pPos.y + pO.y)) / pO.h); return \_pfx + 'UPDATE simul:homes(' + "'147C'" + ').simul:windows SET simul:"window/state"=' + pO.state + 'cm WHERE simul:"window/id"=' + (pO.compId - 2); };
      var \_changeTemp = function(pO, pPos) { var \_lTh = pO.h - 8; pO.state = 40.0 * (\_lTh - (pPos.y - pO.y - 4)) / \_lTh; return \_pfx + 'UPDATE simul:homes(' + "'147C'" + ').simul:floors SET simul:temperature=' + pO.state + 'dC WHERE simul:floor=' + (pO.compId - 6); };
      var \_changeParticules = function(pO, pPos) { return ''; /\* TODO \*/ };
      var \_changeWater = function(pO, pPos) { return ''; /\* TODO \*/ };
      var \_changeArmed = function(pO, pPos) { pO.state = !pO.state; return \_pfx + 'UPDATE alrm:controllers(' + "'147C'" + ') SET alrm:state=' + (pO.state ? 'alrm:STATES#ARMED' : 'alrm:STATES#UNARMED'); };
      var \_statesQuery = \_pfx + 'SELECT * FROM alrm:components(@[1,10]);'; /* small cheat: it's actually easier to read our sensors than our states */
      var \_alarmsQuery = \_pfx + 'SELECT alrm:state, simul:siren, simul:"doors/LED", simul:"windows/LED", simul:"fire/LED", simul:"water/LED" FROM simul:homes(' + "'147C'" + ');';
      var \_controllerQuery = \_pfx + 'SELECT alrm:state FROM alrm:controllers(' + "'147C'" + ');';
      var \_xh = 30;
      var \_objectList =
        [
          {name:'house\_frame', compId:undefined, x:\_xh, y:0, w:70, h:110, onRender:\_renderHouse},
          {name:'door1\_1', compId:1, x:\_xh+10, y:85, w:15, h:25, state:false, onRender:\_renderDoor, onClick:\_changeDoor},
          {name:'door1\_2', compId:2, x:\_xh+45, y:85, w:15, h:25, state:false, onRender:\_renderDoor, onClick:\_changeDoor},
          {name:'window1\_1', compId:3, x:\_xh+20, y:55, w:10, h:20, state:0.0, onRender:\_renderWindow, onClick:\_changeWindow},
          {name:'window1\_2', compId:4, x:\_xh+40, y:55, w:10, h:20, state:0.0, onRender:\_renderWindow, onClick:\_changeWindow},
          {name:'window2\_1', compId:5, x:\_xh+20, y:25, w:10, h:20, state:0.0, onRender:\_renderWindow, onClick:\_changeWindow},
          {name:'window2\_2', compId:6, x:\_xh+40, y:25, w:10, h:20, state:0.0, onRender:\_renderWindow, onClick:\_changeWindow},
          {name:'thermo1\_1', compId:7, x:12, y:70, w:15, h:35, state:23.0, onRender:\_renderThermo, onClick:\_changeTemp},
          {name:'thermo2\_1', compId:8, x:12, y:25, w:15, h:35, state:23.0, onRender:\_renderThermo, onClick:\_changeTemp},
          {name:'particules2\_1', compId:9, x:\_xh+90, y:25, w:10, h:10, state:0.0, onRender:\_renderParticules, onClick:\_changeParticules},
          {name:'water1\_1', compId:10, x:\_xh+90, y:55, w:10, h:10, state:false, onRender:\_renderWater, onClick:\_changeWater},
          {name:'siren', x:\_xh+100, y:35, w:10, h:10, state:false, onRender:\_renderAlarm},
          {name:'doors', x:\_xh+100, y:50, w:10, h:10, state:false, onRender:\_renderAlarm},
          {name:'windows', x:\_xh+100, y:65, w:10, h:10, state:false, onRender:\_renderAlarm},
          {name:'fire', x:\_xh+100, y:80, w:10, h:10, state:false, onRender:\_renderAlarm},
          {name:'water', x:\_xh+100, y:95, w:10, h:10, state:false, onRender:\_renderAlarm},
          {name:'ARMED', x:\_xh+100, y:10, w:10, h:10, state:true, onRender:\_renderArmed, onClick:\_changeArmed},
        ];
      this.processQueriesResults =
        function(pData)
        {
          var \_alrm = pData[0][0]['afy:value'];
          \_objectList[11].state = \_alrm[\_pfxdef + '/siren'] != 'false';
          \_objectList[12].state = \_alrm[\_pfxdef + '/doors/LED'] != 'false';
          \_objectList[13].state = \_alrm[\_pfxdef + '/windows/LED'] != 'false';
          \_objectList[14].state = \_alrm[\_pfxdef + '/fire/LED'] != 'false';
          \_objectList[15].state = \_alrm[\_pfxdef + '/water/LED'] != 'false';
          var \_controller = pData[2][0];
          \_objectList[16].state = !('http://example/alarm-system/state' in \_controller) || \_controller['http://example/alarm-system/state'].indexOf('UNARMED') < 0;
          var \_iO = 1;
          pData[1].forEach(function(\_r) { \_objectList[\_iO].state = \_r['http://affinityng.org/service/VDEV/read/property']; \_iO++; });
        };
      this.getQueries = function() { return \_alarmsQuery + \_statesQuery + \_controllerQuery; };
      this.getObjects = function() { return \_objectList; };
      this.getEvalRateInMs = function() { return 2000; };
    };})();
  </code>

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

Pull Model & DAGs
-----------------

###Why bother about a pull model?

AffinityNG is a platform, that aims at lowering the barrier of entry for the design and implementation of
inter-related agents (expected to multiply, in the bright near future of the Internet-of-Things).
To fulfill that promise, AffinityNG provides a flexible execution model, capable of integrating
common paradigms and execution patterns.

One of these common all-purpose patterns is the "pull model", allowing the dynamic construction
and representation of complex processing graphs (usually directed acyclic graphs [DAGs]).
These graphs combine source nodes, filtering nodes and merging nodes, each of which may be parametrizable,
and may need to execute arbitrarily complex tasks to produce its output (hence the presence of caches).

For example, this pattern is applicable to signal processing.  In an image or video processing
scenario for instance, source nodes may be raw or synthetic images; filtering nodes could
blur their input, colorize it, add noise to it, extract a matte, or identify features in it;
and merging nodes could apply various forms of blending (e.g. with or without an alpha channel).
Note that a DAG is most appropriate in this context (as opposed to a simple tree), because
the output of a same node may be reused by multiple nodes higher up the chain.

The pull model pattern is equally applicable to a multitude of other processing scenarios
involving animations, behaviors, simulations, circuits, spreadsheet-like active specifications, etc.
Any of them may be of interest for an agent of the IoT. 
In this section we'll briefly illustrate how to easily implement a pull model of evaluation
in AffinityNG.

###Pull model as an [EXPR](./pathSQL reference.md#expr-expression-definition) of [values](./terminology.md#value)

At a lower level, the [expression value type](./pathSQL reference.md#expr-expression-definition) in Affinity
already builds upon a very flexible and powerful tree of operators (`OP_*` in [affinity.h](./sources/affinity_h.html))
and operands, where operands are represented by an AffinityNG [value](./terminology.md#value).
Evaluating an expression can be thought of as pulling on its tree.  This evaluation
model can already be used to perform evolved computations, as briefly demonstrated
[here](./pathSQL basics [data].md#how-to-use-lambda-expressions).

###Pull model as a graph of [PINs](./terminology.md#pin)

But [PINs](./terminology.md#pin) and [services](./terminology.md#service) provide a higher-level solution (and more control),
to implement a pull model of evaluation.
On one hand, they allow to create, query and update a fully parametrized processing graph.
Note that in this instance the operands will be whole PINs, capable of holding together
their state/data, their processing code, as well as their relationships in the DAG.
On the other hand, services make it trivial to bind specialized (or even customized) processing units
to each node in the graph.  And [CPINs](./terminology.md#cpin) may also be used to
integrate remote nodes, fitting naturally in the pull model.

Let's illustrate with a concrete example.  We'll build a small DAG to process some bits
(*note: the actual processing is meaningless here, we're just sketching the structure*).
We'll also demonstrate how nodes in the DAG can notify each other when their parameters change.

  <code class='pathsql_staticschema'>
    (function() { return {
      aspect:1,
      instructions: [
        {type:'fillRect', t:0, x:0, y:0, w:1, h:1, fillStyle:'#e4e4e4'},
        /\* --- \*/
        {type:'stroke', t:0, x0:0.5, y0:0.2, x1:0.25, y1:0.45, thickness:0.02, strokeStyle:'#004400'},
        {type:'stroke', t:0, x0:0.5, y0:0.2, x1:0.75, y1:0.45, thickness:0.02, strokeStyle:'#004400'},
        {type:'stroke', t:0, x0:0.25, y0:0.45, x1:0.25, y1:0.75, thickness:0.02, strokeStyle:'#004400'},
        {type:'strokeCircle', t:0, x:0.5, y:0.2, radius:0.07, thickness:0.02, strokeStyle:'#004400', fillStyle:'#e4e4e4'},
        {type:'strokeCircle', t:0, x:0.25, y:0.45, radius:0.07, thickness:0.02, strokeStyle:'#004400', fillStyle:'#e4e4e4'},
        {type:'strokeCircle', t:0, x:0.25, y:0.75, radius:0.07, thickness:0.02, strokeStyle:'#004400', fillStyle:'#e4e4e4'},
        {type:'strokeCircle', t:0, x:0.75, y:0.45, radius:0.07, thickness:0.02, strokeStyle:'#004400', fillStyle:'#e4e4e4'},
        {type:'fillText', t:0, x:0.5, y:0.2, dx:-0.5, dy:0.1, fillStyle:'#000000', text:'blender', font:'12pt Helvetica'},
        {type:'fillText', t:0, x:0.25, y:0.45, dx:-0.5, dy:0.1, fillStyle:'#000000', text:'filter', font:'12pt Helvetica'},
        {type:'fillText', t:0, x:0.25, y:0.75, dx:-0.5, dy:0.1, fillStyle:'#000000', text:'source1', font:'12pt Helvetica'},
        {type:'fillText', t:0, x:0.75, y:0.45, dx:-0.5, dy:0.1, fillStyle:'#000000', text:'source2', font:'12pt Helvetica'},
        /\* --- \*/
        {type:'fillText', t:0.2, duration:0.4, x:0.05, y:0.1, fillStyle:'#000066', text:'pull', font:'bold 12pt Helvetica'},
        {type:'fillText', t:0.24, duration:0.36, x:0.7, y:0.65, dx:-0.5, fillStyle:'#000066', text:'request', font:'12pt Helvetica'},
        {type:'strokeThickArrow', t:0.24, duration:0.28, x:0.5-0.05, y:0.07, angle:90, thickness:0.02, strokeStyle:'#000066'},
        {type:'strokeThickArrow', t:0.28, duration:0.24, x:0.37-0.05, y:0.35-0.03, angle:135, thickness:0.02, strokeStyle:'#000066'},
        {type:'strokeThickArrow', t:0.28, duration:0.24, x:0.63+0.05, y:0.35-0.03, angle:45, thickness:0.02, strokeStyle:'#000066'},
        {type:'strokeThickArrow', t:0.32, duration:0.16, x:0.25-0.05, y:0.6, angle:90, thickness:0.02, strokeStyle:'#000066'},
        /\* --- \*/
        {type:'fillText', t:0.4, duration:0.2, x:0.7, y:0.75, dx:-0.5, fillStyle:'#006600', text:'response', font:'12pt Helvetica'},
        {type:'strokeThickArrow', t:0.48, duration:0.08, x:0.5+0.05, y:0.07, angle:-90, thickness:0.02, strokeStyle:'#006600'},
        {type:'strokeThickArrow', t:0.44, duration:0.12, x:0.37+0.03, y:0.35+0.02, angle:-45, thickness:0.02, strokeStyle:'#006600'},
        {type:'strokeThickArrow', t:0.4, duration:0.16, x:0.63-0.03, y:0.35+0.02, angle:-135, thickness:0.02, strokeStyle:'#006600'},
        {type:'strokeThickArrow', t:0.4, duration:0.16, x:0.25+0.05, y:0.6, angle:-90, thickness:0.02, strokeStyle:'#006600'},
        /\* --- \*/
        {type:'fillText', t:0.7, duration:0.2, x:0.05, y:0.1, fillStyle:'#440000', text:'invalidation', font:'bold 12pt Helvetica'},
        {type:'strokeThickArrow', t:0.78, duration:0.08, x:0.37+0.05, y:0.35, angle:-45, thickness:0.02, strokeStyle:'#440000'},
        {type:'strokeThickArrow', t:0.74, duration:0.12, x:0.63-0.05, y:0.35, angle:-135, thickness:0.02, strokeStyle:'#440000'},
        {type:'strokeThickArrow', t:0.74, duration:0.12, x:0.25+0.05, y:0.6, angle:-90, thickness:0.02, strokeStyle:'#440000'},
        {type:'strokeThickArrow', t:0.7, duration:0.16, x:0.12, y:0.75, angle:0, thickness:0.02, strokeStyle:'#440000'},
        {type:'strokeThickArrow', t:0.7, duration:0.16, x:0.12, y:0.45, angle:0, thickness:0.02, strokeStyle:'#440000'},
        {type:'strokeThickArrow', t:0.7, duration:0.16, x:0.88, y:0.45, angle:180, thickness:0.02, strokeStyle:'#440000'},
      ]
    };})();
  </code>  

In our code example, each node in the DAG will be represented by up to 3 distinct, inter-connected PINs:

  * the node itself, knowing its input nodes (`dag:input1` etc.), and also pointing to
    a ghost of itself (`dag:ghost`), as well as to a separate optional PIN for its
    parameters (`dag:parameters`); the node may also contain a cache of its last
    output evaluation (`dag:cache`)
  * the ghost knows its logical outputs (`dag:"ghost/parents"`), and thus forms a notification
    chain parallel to the actual DAG of nodes (*note:* this separation is essentially for convenience,
    to facilitate using `afy:onUpdate` for this purpose); the ghost also has a back-pointer to
    its `dag:"owner/node"`, as well as a `dag:"invalidation/id"`, which reflects the
    last logical time it was invalidated
  * the optional PIN to hold a node's parameters knows its owner (via `dag:parametrizes`),
    and thus can initiate a notification up the chain

First, let's produce a simple demonstration DAG, where the top node has 2 inputs,
its first input has 1, and its second input is directly a source.  Here we insert
the whole DAG in a single statement, for fun (in a real-life scenario this would
more likely be the result of a gradual construction).
The actual processing in the current example simply manipulates a bit array:

  <code class='pathsql_snippet' loaders='CREATE LOADER _vdev AS &#39;VDEV&#39;;' dependencies='SET PREFIX dag: &#39;http://example/pullmodel&#39;; SET TRACE ALL ACTIONS; SET TRACE ALL COMMUNICATIONS; INSERT afy:objectID=.dag:stdout, afy:service={.srv:IO}, afy:address=1;'>
    SET PREFIX dag: 'http://example/pullmodel';<br>
    <br>
    /\* =========================================== \*/<br>
    /\* ROOT NODE (A TWO-INPUT __BLENDER__ [NO PARAMS]) \*/<br>
    /\* =========================================== \*/<br>
    INSERT @:1 afy:service={.srv:VDEV},<br>
    &nbsp;afy:objectID=.dag:root,<br>
    &nbsp;dag:ghost=(INSERT @:10001 dag:"owner/node"=@:1, dag:"invalidation/id"=0),<br>
    &nbsp;VDEV:"read/evaluator"={<br>
    &nbsp;&nbsp;/\* Pull our inputs (caching their outputs at the same time). \*/<br>
    &nbsp;&nbsp;&#36;{UPDATE :0 SET dag:cache1=(SELECT FIRST VDEV:"read/property" FROM :0.dag:input1)},<br>
    &nbsp;&nbsp;&#36;{UPDATE :0 SET dag:cache2=(SELECT FIRST VDEV:"read/property" FROM :0.dag:input2)},<br>
    &nbsp;&nbsp;/\* Process our output: here, the bits of our first input minus the bits of our second. \*/<br>
    &nbsp;&nbsp;/\* Note: the result of our VDEV service is produced by its last statement. \*/<br>
    &nbsp;&nbsp;&#36;{UPDATE :0 SET dag:cache=(SELECT dag:cache1 & ~dag:cache2 FROM :0)},<br>
    &nbsp;&nbsp;&#36;{SELECT dag:cache FROM :0}},<br>
    &nbsp;VDEV:"evaluation/parameters"=<br>
    &nbsp;&nbsp;(INSERT<br>
    <br>
    &nbsp;&nbsp;&nbsp;dag:input1=<br>
    <br>
    &nbsp;&nbsp;&nbsp;&nbsp;/\* ================================================== \*/<br>
    &nbsp;&nbsp;&nbsp;&nbsp;/\* ROOT's INPUT1 (A PARAMETRIZED SINGLE-INPUT __FILTER__) \*/<br>
    &nbsp;&nbsp;&nbsp;&nbsp;/\* ================================================== \*/<br>
    &nbsp;&nbsp;&nbsp;&nbsp;(INSERT @:11 afy:service={.srv:VDEV},<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dag:ghost=(INSERT @:10011 dag:"owner/node"=@:11, dag:"ghost/parents"=@:10001, dag:"invalidation/id"=0),<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;VDEV:"read/evaluator"={<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/\* Pull our input. \*/<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#36;{UPDATE :0 SET dag:cache=(SELECT FIRST VDEV:"read/property" FROM :0.dag:input)},<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/\* &#36;{UPDATE #dag:stdout SET afy:content='=== Did produce cache of root input1 ==='},\*/<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/\* Process our output: the bits of our input shifted to the left. \*/<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#36;{SELECT dag:cache & dag:mask FROM :0}},<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;VDEV:"evaluation/parameters"=<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(INSERT<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dag:mask=X'FF00FF00FF00', /\* (Note: this is the filter's parameter) \*/<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dag:input=<br>
    <br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/\* ====================================== \*/<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/\* INPUT1's INPUT (A PARAMETRIZED __SOURCE__) \*/<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/\* ====================================== \*/<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(INSERT @:111 afy:service={.srv:VDEV},<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dag:ghost=(INSERT dag:"owner/node"=@:111, dag:"ghost/parents"=@:10011, dag:"invalidation/id"=0),<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;VDEV:"read/evaluator"=&#36;{SELECT dag:"source/bytes" FROM :0},<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;VDEV:"evaluation/parameters"=(INSERT dag:parametrizes=@:11, dag:"source/bytes"=X'010101010101')))),<br>
    <br>
    &nbsp;&nbsp;&nbsp;dag:input2=<br>
    <br>
    &nbsp;&nbsp;&nbsp;&nbsp;/\* ===================================== \*/<br>
    &nbsp;&nbsp;&nbsp;&nbsp;/\* ROOT's INPUT2 (A PARAMETRIZED __SOURCE__) \*/<br>
    &nbsp;&nbsp;&nbsp;&nbsp;/\* ===================================== \*/<br>
    &nbsp;&nbsp;&nbsp;&nbsp;(INSERT @:12 afy:service={.srv:VDEV},<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dag:ghost=(INSERT dag:"owner/node"=@:12, dag:"ghost/parents"=@:10001, dag:"invalidation/id"=0),<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;VDEV:"read/evaluator"=&#36;{SELECT dag:"source/bytes" FROM :0},<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;VDEV:"evaluation/parameters"=(INSERT afy:objectID=.dag:source2, dag:parametrizes=@:12, dag:"source/bytes"=X'000000001111')));<br>
  </code>  

Now let's see our DAG at work.  First, we'll just evaluate it in its present state:

  <code class='pathsql_snippet'>
    SET PREFIX dag: 'http://example/pullmodel';<br>
    SELECT VDEV:"read/property" FROM #dag:root;
  </code>  

It should have cached its own output (in `dag:cache`):

  <code class='pathsql_snippet'>
    SET PREFIX dag: 'http://example/pullmodel';<br>
    SELECT RAW &#42; FROM #dag:root.VDEV:"evaluation/parameters";
  </code>  

Let's define some notification logic, to automatically invalidate nodes in the DAG upon
changes in a node's parameters:

  <code class='pathsql_snippet'>
    SET PREFIX dag: 'http://example/pullmodel';<br>
    <br>
    /\* Starting a new notification chain, due to local changes. \*/<br>
    CREATE CLASS dag:"invalidation/initiator" AS SELECT &#42;<br>
    &nbsp;WHERE EXISTS(dag:parametrizes)<br>
    &nbsp;SET afy:onUpdate={<br>
    &nbsp;&nbsp;&#36;{UPDATE RAW @self.dag:parametrizes DELETE dag:cache},<br>
    &nbsp;&nbsp;&#36;{UPDATE RAW @self.dag:parametrizes.dag:ghost SET dag:"invalidation/id"+=1}};
    <br>
    /\* Walking up the notification chain. \*/<br>
    CREATE CLASS dag:"invalidation/propagator" AS SELECT &#42;<br>
    &nbsp;WHERE EXISTS(dag:"invalidation/id") AND EXISTS(dag:"owner/node")<br>
    &nbsp;SET afy:onUpdate={<br>
    &nbsp;&nbsp;/\* Determine if we have reached a root. \*/<br>
    &nbsp;&nbsp;&#36;{UPDATE @auto SET \_lIsRoot=(SELECT NOT EXISTS(dag:"ghost/parents") FROM @self)},<br>
    &nbsp;&nbsp;/\* If there's a parent node, keep invalidating upward. \*/<br>
    &nbsp;&nbsp;&#36;{UPDATE @auto SET \_lUpdateParents=<br>
    &nbsp;&nbsp;&nbsp;(UPDATE @self.dag:"ghost/parents" SET dag:"invalidation/id"+=1)<br>
    &nbsp;&nbsp;&nbsp;WHERE @auto.\_lIsRoot IS FALSE},<br>
    &nbsp;&nbsp;/\* Otherwise if we've reached the root, pull and cache result. \*/<br>
    &nbsp;&nbsp;&#36;{UPDATE RAW @self.dag:"owner/node" set dag:cache=<br>
    &nbsp;&nbsp;&nbsp;(SELECT VDEV:"read/property" FROM @self.dag:"owner/node")<br>
    &nbsp;&nbsp;&nbsp;WHERE @auto.\_lIsRoot IS TRUE}};<br>
  </code>  

Now, let's modify one of the sources:

  <code class='pathsql_snippet'>
    SET PREFIX dag: 'http://example/pullmodel';<br>
    UPDATE RAW #dag:root.VDEV:"evaluation/parameters".dag:input2.VDEV:"evaluation/parameters" SET dag:"source/bytes"=X'111100000000';
  </code>  

It should have triggered an automatic re-evaluation, so let's see if the output changed,
but without pulling on it this time (the fresh output should already be in `dag:cache`,
thanks to the notification logic we just put in place):

  <code class='pathsql_snippet'>
    SET PREFIX dag: 'http://example/pullmodel';<br>
    SELECT RAW &#42; FROM #dag:root.VDEV:"evaluation/parameters";
  </code>  

Introspection & Code Querying
-----------------------------

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

<!-- Synergy
The very open nature of [PINs](./terminology.md#pin), combined with the way all active components
are configured, allows to merge together mutliple functionalities into a single PIN naturally,
with automatic handling in the kernel of implied aspects. 
In a next revision of the doc, we will provide concrete examples.
<!-- TODO agree on exact definition, scenarios, convincing examples --
-->

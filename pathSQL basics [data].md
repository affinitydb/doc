pathSQL Basics: Data
====================

Although the [Affinity data model](./terminology.md#essential-concepts-data-model) is different
from relational databases, pathSQL is designed to be as close to SQL as possible. This document shows
**how to** insert, update, query and index data ([PINs](./terminology.md#pin)).  

For a more systematic survey of pathSQL and its commands, please visit the [reference](./pathSQL reference.md).  
For an overview of the communication and control extensions in pathSQL, please see the [pathSQL basics: control](./pathSQL basics [control].md) page.  

To execute an example on this page, either click on it (this will redirect you to the online console),
or click on the blue button in front of it (this will produce results in-place on this page). <div class="pathsql_button_fake">v</div>  

To setup your own runtime environment, please visit this [link](./getting started.md).  

How to insert data
------------------
There is no concept of table in Affinity: all data are inserted in global scope. Two styles can be used to
perform [PIN](./terminology.md#pin) inserts:

1. Affinity-specific syntax:

  <code class='pathsql_snippet'>INSERT property1 ='value1', property2 ='value2';</code>
  <code class='pathsql_snippet'>INSERT @{property1 ='value1a', property2 ='value2a'}, @{property1='value1b', property2='value2b'};</code>
  <code class='pathsql_snippet'>INSERT children={(INSERT property1 ='value1a', property2 ='value2a'), (INSERT property1='value1b', property2='value2b')};</code>  

2. SQL-like syntax:

  <code class='pathsql_snippet'>INSERT (property1, property2) VALUES ('value1','value2');</code>
  <code class='pathsql_snippet'>INSERT (property1, property2) VALUES ('value1a','value2a'), ('value1b','value2b');</code>  

<span class='pathsql_new'>NEW</span> 
PINs may contain sub-structures, e.g.

  <code class='pathsql_snippet'>INSERT<br>
      &nbsp;@{position3d={x=10.0m, y=12.2m, z=14.2m}},<br>
      &nbsp;@{position3d={x=50.3m, y=22.5m, z=4.7m}},<br>
      &nbsp;@{position3d={x=0.3m, y=22.5m, z=0.7m}};
  </code>

Different [data types](./pathSQL reference.md#data-types) have different input formats, e.g.

  <code class='pathsql_snippet'>INSERT<br>
      prop_string='string', prop_url=U'http://test/',<br>
      prop_binary_string=X'DEF5',<br>
      prop_int=128, prop_float=3.40282f, prop_double=3.40282, prop_bool=true,<br>
      prop_datatime=TIMESTAMP '2010-12-31 23:59:59', prop_internal=INTERVAL '-12:00:00',<br>
      prop_lambda=$(:0 > 50),<br>
      prop_collection={1,2,4},<br>
      prop_structure={radius=10, material='metal', weight=120lb},<br>
      prop_map={200 -> 'superior grade', 150 -> 'commercial grade', 100 -> 'consumer grade'};</code>  

Collections may contain heterogeneous data, e.g.

  <code class='pathsql_snippet'>INSERT prop_collection=<br>
      {'string', X'DEF5', U'http://test/', 128, 3.40282f, 3.40282, true, TIMESTAMP '2010-12-31 23:59:59', INTERVAL '-12:00:00'};</code>  

<span class='pathsql_new'>NEW</span> 
Sub-structures and associative arrays may also have heterogeneous data, e.g.

  <code class='pathsql_snippet'>INSERT prop_structure=<br>
      {p1='string', p2=X'DEF5', p3=U'http://test/', p4=128, p5=3.40282f, p6=3.40282, p7=true, p8=TIMESTAMP '2010-12-31 23:59:59', p9=INTERVAL '-12:00:00'};</code>
  <code class='pathsql_snippet'>INSERT prop_map=<br>
      {'string' -> X'DEF5', U'http://test/' -> 128, 3.40282f -> 3.40282, true -> TIMESTAMP '2010-12-31 23:59:59'};</code>  

<span class='pathsql_new'>NEW</span> 
Whole graphs with cycles may be inserted in one statement, using references and the `@:n` syntax, e.g.

  <code class='pathsql_snippet'>INSERT @:1 name='Fred', children={<br>
      &nbsp;(INSERT @:2 name='Joe', parent=@:1, siblings={@:3, @:4}),<br>
      &nbsp;(INSERT @:3 name='Christine', parent=@:1, siblings={@:2, @:4}),<br>
      &nbsp;(INSERT @:4 name='Sam', parent=@:1, siblings={@:2, @:3})}
  </code>

  <code class='pathsql_snippet'>INSERT @:1<br>
      name='Fred', bornin='France', email='fred@acme.org', livesin='Chicago', age=27,<br>
      friends=<br>
      &nbsp;{(INSERT @:2 name='Tony', bornin='Hungary', email='tony@acme.org', livesin='Calgary', age=76, friends={@:1, @:3}, photos=<br>
      &nbsp;&nbsp;&nbsp;{(INSERT photo_name='blue.jpg'), (INSERT photo_name='red.jpg'), (INSERT photo_name='green.jpg')}),<br>
      &nbsp;&nbsp;(INSERT @:3 name='Peter', bornin='Mexico', email='peter@acme.org', livesin='Mexico', age=45, friends={@:1, @:2}, photos=<br>
      &nbsp;&nbsp;&nbsp;{(INSERT photo_name='rose.jpg'), (INSERT photo_name='petunia.jpg'), (INSERT photo_name='orchid.jpg')})},<br>
      photos=<br>
      &nbsp;{(INSERT photo_name='Greece.jpg'), (INSERT photo_name='Germany.jpg'), (INSERT photo_name='USA.jpg'),<br>
      &nbsp;&nbsp;(INSERT photo_name='France.jpg'), (INSERT photo_name='Egypt.jpg')};
  </code>

  <code class='pathsql_snippet'>&nbsp;SET PREFIX simul: 'http://example/simul';<br>
      SET PREFIX control: 'http://example/control';<br>
      SET PREFIX world: 'http://example/world';<br>
      SET PREFIX meta: 'http://example/meta';<br>
      SET PREFIX inst: 'http://example/inst';<br>
      CREATE CLASS control:"rt/signalable" AS SELECT &#42; WHERE EXISTS(control:"rt/time/signal");<br>
      CREATE CLASS control:"rt/physical/samples" AS SELECT &#42; WHERE EXISTS(control:"rt/time/step") AND EXISTS(control:"rt/sensor");<br>
      CREATE TIMER control:"rt/source/timer" INTERVAl '00:00:20' AS UPDATE control:"rt/signalable"<br>
      &nbsp;SET control:"rt/time/signal"=EXTRACT(SECOND FROM CURRENT_TIMESTAMP), control:"rt/time"=CURRENT_TIMESTAMP;<br>
      INSERT @:1<br>
      &nbsp;meta:description='On/Off Simulated Sensor Template (572ef13c)',<br>
      &nbsp;afy:objectID=.simul:"template/sensor/on.off.572ef13c",<br>
      &nbsp;afy:predicate=&#36;{SELECT &#42; WHERE EXISTS(simul:"new/sensor/572ef13c")},<br>
      &nbsp;control:"template/sensor/step/handler"=<br>
      &nbsp;&nbsp;(CREATE CLASS control:"template/sensor/step/handler/on.off.572ef13c" AS SELECT &#42; FROM control:"rt/signalable"<br>
      &nbsp;&nbsp;&nbsp;WHERE control:"sensor/model"=.simul:"template/sensor/on.off.572ef13c" SET<br>
      &nbsp;&nbsp;&nbsp;control:"template/sensor"=@:1,<br>
      &nbsp;&nbsp;&nbsp;afy:onUpdate=&#36;{INSERT <br>
      &nbsp;&nbsp;&nbsp;&nbsp;simul:"rt/gen/spread"=(SELECT simul:"template/gen/spread" FROM @class.control:"template/sensor"),<br>
      &nbsp;&nbsp;&nbsp;&nbsp;simul:"rt/gen/min"=(SELECT simul:"template/gen/min" FROM @class.control:"template/sensor"),<br>
      &nbsp;&nbsp;&nbsp;&nbsp;simul:"rt/gen/max"=(SELECT simul:"template/gen/max" FROM @class.control:"template/sensor"),<br>
      &nbsp;&nbsp;&nbsp;&nbsp;simul:"rt/gen/jitter"=(SELECT simul:"template/gen/jitter" FROM @class.control:"template/sensor") &#42;<br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;EXTRACT(SECOND FROM CURRENT_TIMESTAMP),<br>
      &nbsp;&nbsp;&nbsp;&nbsp;simul:"rt/value/gen/id"=.simul:"value/gen/sinus",<br>
      &nbsp;&nbsp;&nbsp;&nbsp;control:"rt/sensor"=(SELECT control:sensor FROM @self),<br>
      &nbsp;&nbsp;&nbsp;&nbsp;control:"rt/sensor/model"=(SELECT control:"sensor/model" FROM @self.control:sensor),<br>
      &nbsp;&nbsp;&nbsp;&nbsp;control:"rt/time/step"=(SELECT control:"rt/time/signal" FROM @self), control:"rt/time"=CURRENT_TIMESTAMP}),<br>
      &nbsp;control:"template/sensor/conditions"={<br>
      &nbsp;&nbsp;(INSERT <br>
      &nbsp;&nbsp;&nbsp;meta:description='Condition: turned off a 572ef13c sensor',<br>
      &nbsp;&nbsp;&nbsp;afy:objectID=.control:"template/condition/572ef13c/off",<br>
      &nbsp;&nbsp;&nbsp;afy:predicate=&#36;{SELECT &#42; WHERE (@ IS A control:"rt/physical/samples" AND<br>
      &nbsp;&nbsp;&nbsp;&nbsp;control:"rt/sensor/model"=@:1.afy:objectID AND control:"rt/value" < 0.5)}),<br>
      &nbsp;&nbsp;(INSERT <br>
      &nbsp;&nbsp;&nbsp;meta:description='Condition: turned on a 572ef13c sensor',<br>
      &nbsp;&nbsp;&nbsp;afy:objectID=.control:"template/condition/572ef13c/on",<br>
      &nbsp;&nbsp;&nbsp;afy:predicate=&#36;{SELECT &#42; WHERE (@ IS A control:"rt/physical/samples" AND<br>
      &nbsp;&nbsp;&nbsp;&nbsp;control:"rt/sensor/model"=@:1.afy:objectID AND control:"rt/value" >= 0.5)}),<br>
      &nbsp;&nbsp;(INSERT <br>
      &nbsp;&nbsp;&nbsp;meta:description='Condition (optional): confirmed that a 572ef13c sensor was off',<br>
      &nbsp;&nbsp;&nbsp;afy:objectID=.control:"template/condition/572ef13c/off.confirmed",<br>
      &nbsp;&nbsp;&nbsp;afy:predicate=&#36;{SELECT &#42; WHERE (@ IS A world:appliances AND NOT EXISTS(control:"rt/emergency/time") AND (control:"rt/warning/time"[:LAST] - control:"rt/warning/time"[:FIRST] >= INTERVAL '00:00:05'))})},<br>
      &nbsp;simul:"template/sensor/generator"=(SELECT afy:pinID FROM afy:Classes WHERE afy:objectID=.simul:"value/gen/sinus"),<br>
      &nbsp;simul:"template/gen/type"='boolean', simul:"template/gen/jitter"=0,<br>
      &nbsp;simul:"template/gen/min"=0, simul:"template/gen/max"=100,<br>
      &nbsp;simul:"template/gen/spread"=1.5,<br>
      &nbsp;afy:onEnter=<br>
      &nbsp;&nbsp;&#36;{INSERT @:20<br>
      &nbsp;&nbsp;&nbsp;meta:description='On/Off Simulated Sensor Instance (572ef13c)',<br>
      &nbsp;&nbsp;&nbsp;control:"sensor/model"=(SELECT afy:objectID FROM @class),<br>
      &nbsp;&nbsp;&nbsp;control:"sensor/name"=(SELECT inst:name FROM @self),<br>
      &nbsp;&nbsp;&nbsp;control:appliance=(SELECT inst:appliance FROM @self),<br>
      &nbsp;&nbsp;&nbsp;simul:"sensor/signalable"=<br>
      &nbsp;&nbsp;&nbsp;&nbsp;(INSERT @:30<br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;meta:description='To generate samples for sensor',<br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;control:"rt/time/signal"=0,<br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;control:"sensor/model"=(SELECT afy:objectID FROM @class),<br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;control:sensor=@:20)};<br>
  </code>  

Values can also be lambda expressions, e.g.

  <code class='pathsql_snippet'>INSERT<br>
      &nbsp;trigo_sin=<br>
      &nbsp;&nbsp;&#36;(:0 - POWER(:0,3)/6 + POWER(:0,5)/120 - POWER(:0,7)/5040 + POWER(:0,9)/362880),<br>
      &nbsp;trigo_deg2rad=&#36;(3.141592654 &#42; (:0 % 360) / 180);<br>
      INSERT val_sin30=(SELECT trigo_sin(trigo_deg2rad(30)) WHERE EXISTS(trigo_sin));
  </code>

A few more simple examples:

  <code class='pathsql_snippet'>INSERT name='Jurgen', bornin='South Africa', email='jsmith@acme.org', livesin(FT_INDEX)='Boston', age=22;</code>  
  
  <code class='pathsql_snippet'>INSERT (name, bornin, email, livesin(FT_INDEX), age) VALUES ('Sonny', 'USA', 'sbrown@acme.org', 'Boston', 45);</code>  

  <code class='pathsql_snippet'>INSERT "http://acme.org/properties/length"=123,<br>
      "http://acme.org/properties/width"=456,<br>
      "http://acme.org/properties/name"='wonderful instrument';</code>  

  <code class='pathsql_snippet'>SET PREFIX acmep: 'http://acme.org/properties/';<br>
      INSERT acmep:"length"=123.1, acmep:width=456.1, acmep:name='great instrument';</code>  

How to classify data 
--------------------
All data are inserted in global scope, but applications can freely define specialized access paths for their data
(before or after the data is inserted), by creating [classes](./terminology.md#class).  Here's an example:

  <code class='pathsql_snippet'>CREATE CLASS class1 AS SELECT * WHERE bornin IS NOT NULL;</code>  

  <code class='pathsql_snippet'>CREATE CLASS class2 AS SELECT * WHERE name IN :0;</code>

How to update or delete data
----------------------------

  <code class='pathsql_snippet'>UPDATE * ADD livesin='Cambridge' WHERE name='Sonny';</code>  
        
  <code class='pathsql_snippet'>UPDATE * SET livesin[1]='USA' WHERE name='Sonny';</code>  

  <code class='pathsql_snippet'>UPDATE * SET age=(SELECT AVG(age) FROM *) WHERE name='Sonny';</code>

  <code class='pathsql_snippet'>UPDATE class1 ADD school='MIT' WHERE age > 25;</code>
        
  <code class='pathsql_inert'>UPDATE @50012 ADD school='MIT';</code>  

  <code class='pathsql_inert'>DELETE @50012;</code>  

How to query 
------------
Most of the querying syntax in Affinity is compatible with standard SQL: expressions, function calls, WHERE, ORDER BY,
UNION, INTERSECT, EXCEPT etc.  Here's an example:

  <code class='pathsql_snippet'>SELECT * FROM class1 WHERE LENGTH(bornin) > 5 ORDER BY livesin DESC NULLS FIRST;</code>  

Other examples:

  <code class='pathsql_snippet'>SELECT name, email WHERE EXISTS(livesin);</code>

  <code class='pathsql_snippet'>SELECT WHERE livesin='Boston' ORDER BY name ASC;</code>  
        
  <code class='pathsql_snippet'>SELECT * MATCH AGAINST('Boston');</code>  

<span class='pathsql_new'>NEW</span> 
Regular expressions in text manipulations:

  <code class='pathsql_snippet'>&nbsp;INSERT _retest='Hello';<br>
      INSERT _retest='Hello Mike';<br>
      INSERT _retest='How are you Mike';<br>
      INSERT _retest='Earth to Mike do you receive?';<br>
      SELECT _retest AS result1 WHERE _retest SIMILAR TO &#47;.&#42;Mike&#36;&#47;;<br>
      SELECT _retest AS result2 WHERE _retest SIMILAR TO &#47;.&#42;Mike&#47;;
  </code>

  and soon... <span style='color:red;'>TODO: probably convert this into an example using the regex service, once bug #405 is fixed</span>

  <code class='pathsql_inert'>INSERT CASE WHEN (SELECT ...) SIMILAR TO &#47;^value=([0-9]+), distance=([0-9]+), clock=([0-9]+)&#47;<br>
      THEN {sensor=@50005, movement=&#47;1, distance=CAST(&#47;2 AS m), time=CURRENT_TIMESTAMP, sclock=&#47;3}<br>
      ELSE NULL END;
  </code>

How to use joins
----------------
Affinity returns immutable PIN collections as query results. Here's an example:

  <code class='pathsql_snippet'>SELECT * FROM class1 AS c1 JOIN class2('Jurgen') AS c2 ON (c1.name = c2.name);</code>  

Affinity supports every kind of JOIN (LEFT/RIGHT/FULL/CROSS JOIN), except the Natural JOIN.

How to use [references](./terminology.md#pin-reference)
-----------------------
Relational databases use foreign keys to establish relationships between tables.  Affinity offers a powerful
alternative with [references](./terminology.md#pin-reference) (similar to object-oriented databases):

  <code class='pathsql_snippet'>UPDATE * ADD friends=(SELECT afy:pinID WHERE name='Fred') WHERE name='Jurgen';</code>  
  
  <code class='pathsql_snippet'>UPDATE * ADD friends=(SELECT friends[:FIRST] WHERE name='Jurgen') WHERE name='Sonny';</code>

  <code class='pathsql_inert'>INSERT mypinref=@50012;</code>

  <code class='pathsql_inert'>INSERT mypropref=@50012.friends;</code>

To leverage this information while querying, pathSQL offers the following syntax (path expression):  

  <code class='pathsql_snippet'>SELECT name, email, bornin FROM class1.friends[BEGINS(livesin, 'C')].friends;</code>  

  <code class='pathsql_snippet'>SELECT bornin FROM class2('Jurgen').friends{*}[BEGINS(livesin, 'C')];</code>

  <code class='pathsql_snippet'>SELECT age FROM class2('Jurgen').friends{+}[age > 30];</code>

  <code class='pathsql_snippet'>SELECT DISTINCT FROM class1.friends{*}.photos;</code>

Note that in the current release, path expressions are only available in the FROM clause.

How to use [collections](./terminology.md#collection)
------------------------
### 1. Add elements to a [collection](./terminology.md#collection)
#### 1.1 Insert a PIN with a collection property:

  <code class='pathsql_snippet'>INSERT (prop1, prop2) VALUES ({1, 'inserted', '3'}, 2);</code>  

#### 1.2 Update a property in a collection
Using "UPDATE ... SET ...", we can replace a property with a whole collection directly:  

  <code class='pathsql_inert'>UPDATE @50001 SET prop3={3, 'update set'};</code>  

Using "UPDATE ... ADD ...", we can convert a property from a scalar value to a collection:

  <code class='pathsql_inert'>UPDATE @50001 ADD prop2='update add';</code>  

### 2. Delete an element from a collection

  <code class='pathsql_inert'>UPDATE @50001 DELETE prop1[2];</code>  

### 3. Query on collections
Here are a few examples of queries that can be run against the PIN created in section 1.1:

>1. SELECT * WHERE 1 IN prop1;   
>2. SELECT * WHERE {1,2} IN prop1;  
>3. SELECT * WHERE 1 = prop1;  -- equivalent to example 1.
>4. SELECT * WHERE {1,2} = prop1;  -- equivalent to example 2.

How to index properties
-----------------------
Instead of simply allowing to create indexes ("CREATE INDEX" statement of relational databases), Affinity
emphasizes the declaration of categories, which may or may not imply the creation of underlying secondary indexes.
Here's an example:

  <code class='pathsql_snippet'>CREATE CLASS clsfml AS SELECT * WHERE age IN :0(int, desc, nulls first) AND name IN :1;</code>

This class [family](./terminology.md#family) will create an [index](./terminology.md#index) on prop1 and prop2. The prop1 will be sorted in descending order, and will order nulls first. When parameters are passed, 
the class family behaves like a CLASS. For example:

  <code class='pathsql_snippet'>SELECT * FROM clsfml(27, 'Fred');</code>  

  <code class='pathsql_snippet'>SELECT * FROM clsfml([50, 10], ['A', 'H']);</code>  

  <code class='pathsql_snippet'>SELECT * FROM clsfml;</code>  

  <code class='pathsql_inert'>SELECT * FROM clsfml(*, 'Fred');</code>  

  <code class='pathsql_inert'>SELECT * FROM clsfml(27, *);</code>  

pathSQL Primer
==============

pathSQL is the name of a dialect of SQL defined for Affinity. Although the [Affinity data model](./terminology.md#essential-concepts-data-model) is different
from relational databases, pathSQL is designed to be as close to SQL as possible. This document shows
**how to** insert, update, query and index data ([PINs](./terminology.md#pin)).  

For a more systematic survey of pathSQL and its commands, please visit the [reference](./pathSQL reference.md).  

To execute an example on this page, either click on it, or click on the purple button in front of it. <div class="pathsql_button_fake">v</div>  

To setup your own runtime environment, please visit this [link](./getting started.md).  

How to insert data
------------------
There is no concept of table in Affinity: all data are inserted in global scope. Two styles can be used to
perform [PIN](./terminology.md#pin) inserts:

1. Affinity-specific syntax:

  <code class='pathsql_snippet'>INSERT property1 ='value1', property2 ='value2';</code>  

2. SQL-like syntax:

  <code class='pathsql_snippet'>INSERT (property1, property2) VALUES ('value1','value2');</code>    

Different [data types](./pathSQL reference.md#data-types) may have different input formats, e.g.

  <code class='pathsql_snippet'>INSERT<br>
      prop_string='string', prop_url=U'http://test/',<br>
      prop_binary_string=X'DEF5',<br>
      prop_int=128, prop_float=3.40282f, prop_double=3.40282, prop_bool=true,<br>
      prop_datatime=TIMESTAMP '2010-12-31 23:59:59', prop_internal=INTERVAL '-12:00:00',<br>
      prop_collection={1,2,4};</code>  

Collections may contain heterogeneous data, e.g.

  <code class='pathsql_snippet'>INSERT prop_collection=<br>
      {'string', X'DEF5', U'http://test/', 128, 3.40282f, 3.40282, true, TIMESTAMP '2010-12-31 23:59:59', INTERVAL '-12:00:00'};</code>  

Whole graphs may be inserted in one statement, e.g.

  <code class='pathsql_snippet'>INSERT<br>
      name='Fred', bornin='France', email='fred@acme.org', livesin='Chicago', age=27,<br>
      friends=<br>
      &nbsp;{(INSERT name='Tony', bornin='Hungary', email='tony@acme.org', livesin='Calgary', age=76, photos=<br>
      &nbsp;&nbsp;&nbsp;{(INSERT photo_name='blue.jpg'), (INSERT photo_name='red.jpg'), (INSERT photo_name='green.jpg')}),<br>
      &nbsp;&nbsp;(INSERT name='Peter', bornin='Mexico', email='peter@acme.org', livesin='Mexico', age=45, photos=<br>
      &nbsp;&nbsp;&nbsp;{(INSERT photo_name='rose.jpg'), (INSERT photo_name='petunia.jpg'), (INSERT photo_name='orchid.jpg')})},<br>
      photos=<br>
      &nbsp;{(INSERT photo_name='Greece.jpg'), (INSERT photo_name='Germany.jpg'), (INSERT photo_name='USA.jpg'),<br>
      &nbsp;&nbsp;(INSERT photo_name='France.jpg'), (INSERT photo_name='Egypt.jpg')};</code>

More examples:

  <code class='pathsql_snippet'>INSERT name='Jurgen', bornin='South Africa', email='jsmith@acme.org', livesin='Boston', age=22;</code>  
  
  <code class='pathsql_snippet'>INSERT (name, bornin, email, livesin, age) VALUES ('Sonny', 'USA', 'sbrown@acme.org', 'Boston', 45);</code>  

  <code class='pathsql_snippet'>INSERT "http://acme.org/properties/length"=123,<br>
      "http://acme.org/properties/width"=456,<br>
      "http://acme.org/properties/name"='wonderful instrument';</code>  

  <code class='pathsql_snippet'>PREFIX acmep: 'http://acme.org/properties/'<br>
      INSERT acmep:"length"=123.1, acmep:width=456.1, acmep:name='great instrument';</code>  

How to update or delete data
----------------------------

  <code class='pathsql_snippet'>UPDATE ADD livesin='Cambridge' WHERE name='Sonny';</code>  
        
  <code class='pathsql_snippet'>UPDATE SET livesin[1]='USA' WHERE name='Sonny';</code>  

  <code class='pathsql_snippet'>UPDATE SET age=(SELECT AVG(age) FROM *) WHERE name='Sonny';</code>
        
  <code class='pathsql_inert'>UPDATE @50012 ADD school='MIT';</code>  

  <code class='pathsql_inert'>DELETE @50012;</code>  

How to classify data 
--------------------
All data are inserted in global scope, but applications can freely define specialized access paths for their data
(before or after the data is inserted), by creating [classes](./terminology.md#class).  Here's an example:

  <code class='pathsql_snippet'>CREATE CLASS class1 AS SELECT * WHERE bornin IS NOT NULL;</code>  

  <code class='pathsql_snippet'>CREATE CLASS class2 AS SELECT * WHERE name IN :0;</code>

How to query 
------------
Most of the querying syntax in Affinity is compatible with standard SQL: expressions, function calls, WHERE, ORDER BY,
UNION, INTERSECT, EXCEPT etc.  Here's an example:

  <code class='pathsql_snippet'>SELECT * FROM class1 WHERE LENGTH(bornin) > 5 ORDER BY livesin DESC NULLS FIRST;</code>  

Other examples:

  <code class='pathsql_snippet'>SELECT name, email WHERE EXISTS(livesin);</code>

  <code class='pathsql_snippet'>SELECT WHERE livesin='Boston' ORDER BY name ASC;</code>  
        
  <code class='pathsql_snippet'>SELECT * MATCH AGAINST('Boston');</code>  

How to use joins
----------------
Affinity returns immutable PIN collections as query results. Here's an example:

  <code class='pathsql_snippet'>SELECT * FROM class1 AS c1 JOIN class2('Jurgen') AS c2 ON (c1.name = c2.name);</code>  

Affinity supports every kind of JOIN (LEFT/RIGHT/FULL/CROSS JOIN), except the Natural JOIN.

How to use [references](./terminology.md#pin-reference)
-----------------------
Relational databases use foreign keys to establish relationships between tables.  Affinity offers a powerful
alternative with [references](./terminology.md#pin-reference) (similar to object-oriented databases):

  <code class='pathsql_snippet'>UPDATE ADD friends=(SELECT afy:pinID WHERE name='Fred') WHERE name='Jurgen';</code>  
  
  <code class='pathsql_snippet'>UPDATE ADD friends=(SELECT friends[:FIRST] WHERE name='Jurgen') WHERE name='Sonny';</code>

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

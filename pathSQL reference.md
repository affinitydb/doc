The pathSQL Language
====================
pathSQL is the name of a dialect of SQL defined for mvStore. The [mvStore data model](./terminology.md#essential-concepts-data-model) is very different
from the relational model, but pathSQL is designed to remain as close to SQL as possible. 
This page presents a thorough survey of the language. It covers the
elements of the [syntax](#pathsql-syntax), the [data types](#data-types) and the [operators](#functions-and-operators).
It also provides a formal [BNF description](#statements-bnf) of the [DDL](#ddl) and [DML](#dml).
For a quick practical overview, please visit the ["getting started"](./pathSQL getting started.md) section.

It's easy to test any of these commands in the online console. Direct links to the console are provided in the documentation.

pathSQL Syntax
--------------
### Lexical Structure
pathSQL supports the following token types: [keywords](#keywords), [identifiers](#identifiers), [qnames](#qnames), [constants](#constants), [operators](#operators), [comments](#comments), and [special characters](#special-characters).

#### Keywords
pathSQL's coverage of standard SQL keywords depends on functional areas.

pathSQL supports most of the keywords related to common [DML](#dml) (Database Manipulation Language): SELECT, UPDATE, DELETE, FROM, CAST, built-in functions etc.

pathSQL doesn't support the relational DDL (Data Definition Language) and DCL (Database Control Language): no table, no view, no primary or foreign key, no unique or check constraint.  However, mvStore introduces the [CLASS](#ddl) keyword.

pathSQL doesn't support any DSPL (Data Stored Procedure Language).  

_Note: Keywords are **case insensitive**. A common convention is to write keywords in upper case._

#### Identifiers 
Identifiers are used to designate mvStore entities such as [classes](./terminology.md#class), [properties](./terminology.md#property) etc.  Identifiers are **case sensitive**.  See also the
next section about [qnames](#qnames).

There are 2 types of identifiers:

1. plain identifiers: they begin with a letter (upper or lower case, including diacritical marks and non-latin characters) or an underscore (_), and subsequent characters can also be digits. 
2. quoted identifiers (aka delimited identifiers): they are formed by enclosing any arbitrary sequence of characters in double-quotes ("), except the character '\0'. A delimited identifier is never a keyword ("select" could be used to refer to a property named _select_).

_Note: To include a double quote, write two double quotes._  

_Note: A string which is enclosed in single quotes (') is a string constant, not an identifier._

Sample: [identifier.sql](./sources/pathsql/identifier.html)

#### QNames
QName stands for "qualified name", and follows the standard conventions defined in XML, RDF etc.
A QName is a prefix:name, where prefix and name are identifiers (prefix typically designates a [namespace](./terminology.md#namespace)).
In mvStore, all built-in properties use prefix "mv" (e.g. mv:pinID).

QNames allow to partition entities such as class names and property names, by namespace.
They help specify the semantic context in which a name should be interpreted,
and can prevent collisions among identical names with different semantic meanings.
This can be especially important when classification is taken into consideration.
Careful selection of prefixes (with clear, distinct and meaningful semantics) yields
better long-term interoperability with other applications.

#### Constants
pathSQL understands most common [value](./terminology.md#value) types.  Some standard constants are
associated with these value types, such as TRUE and FALSE.
Refer to [Data Types](#data-types) for more details.  

#### Operators
pathSQL supports most of the standard SQL operators (logic, comparison, arithmetic, aggregation, string manipulations, date and time manipulations etc.).
Refer to [Functions and Operators](#functions-and-operators) for more details.   

#### Comments
A comment is removed from the input stream before further syntax analysis.

pathSQL supports 3 styles of comments:

1. SQL-style: A sequence of characters beginning with double dashes (--) and extending to the end of the line, e.g.:   

        -- This is a standard SQL comment   

2. C-style: This syntax enables a comment to extend over multiple lines (the beginning and closing sequences need not be on the same line). The comment begins with /* and extends to the matching occurrence of */. These blocks can be nested, as specified in the SQL standard (but unlike C): one can comment out larger blocks of code that might contain existing block comments. For example:

        /* multiline comment
        * with nesting: /* nested block comment */
        */  

3. SPARQL-style: A sequence of characters beginning with number sign (\#) and extending to the end of the line, e.g.:

        # This is a SPARQL comment

#### Special Characters
Some non-alphanumeric characters have special meaning, without being [operators](#operators).

Some cases are extensions specific to pathSQL:

1. The dollar sign ($), followed by digits, is used to represent a positional [_property_](./terminology.md#property) in the body of a statement or class definition. Other uses are ${statement} and $(expression), to indicate a statement/expression variable. In other contexts the dollar sign can be part of an identifier or a dollar-quoted string constant.   
2. The colon (:), followed by digits, is used to represent a positional [_parameter_](./terminology.md#parameter) in the body of a statement or class definition. The colon is also used in [QNames](#qnames).   
3. The period (.) can be used to separate store, class, and property names (in path expression). It can also be part of numerical constants.   
4. Brackets ({}) are used to select the elements of a collection, or to create new collections.    
5. The at sign (@), followed by digits, is used to represent a [PIN ID](./terminology.md#pin-id-pid). In some instances, @ may stand alone and represent the currently processed PIN (e.g. in UPDATE statements and path expressions).  

Other cases are standard:

1. Parentheses (()) group expressions and enforce precedence. In some cases parentheses are required as part of the fixed syntax of a particular SQL command.   
2. Commas (,) are used in some syntactical constructs, to separate the elements of a list.   
3. The semicolon (;) terminates an SQL command. It cannot appear anywhere within a command, except within a string constant or quoted identifier.   
4. The asterisk (\*) is used in some contexts to denote all values of a property or all properties of a PIN or composite value. It also has a special meaning when used as the argument of an aggregate function, namely that the aggregate does not require any explicit parameter.   

### Path Expressions
Path expressions are an extension which is not found in SQL.

Path expressions define navigation paths along the relationships of the abstract schema. They specify both the scope and the results of a query. 
Path expressions support several navigation mechanisms, applicable to each segment of a path:

1. Property of a CLASS, e.g. if PINs in class "cls1" have property "prop1", then we can fetch the value of "prop1" for each PIN in this class with: `cls1.prop1`  
2. Dereference, e.g. if "pin1" has a property "emp_ref", of which the value is a PIN reference to "pin2" with property "name", then we can fetch the value of "pin2.name" with: `pin1.emp_ref.name`  
3. (future) Sub-structure, e.g. if the PIN "pin1" has a property "employee", and the property "employee" has a sub-property "name", then we can fetch the value of this sub-property with: `pin1.employee.name`  

In order to support more complex graph queries, mvStore provides regular expressions for each segment (or property) of the path. There are several options:

Format			Description
---------		-----------
{value}			Navigate along this segment for a number of "value" times (e.g. prop1{3} means "prop1.prop1.prop1").
{min, max}		Navigate along this segment, starting at the "min"-th instance and up to the "max"-th instance.
{*} 			Same as {0, infinity}.
{?}				Same as {0, 1}.
{+}				Same as {1, infinity}.

A predicate (i.e. WHERE clause in SQL) can be attached to each segment of a path expression. E.g. `pin1.emp_ref[name='Jack' AND EXISTS(age)]`. The at sign (@) can be used here to denote the PIN ID which is being processed.  

Path expressions are an important construct in the syntax of the query language. They will be supported in any of the main clauses of a query (SELECT, DELETE, HAVING, UPDATE, WHERE, FROM, GROUP BY, ORDER BY).
Note that in the current version, they can only appear in FROM.

### Value Expressions
Value expressions are expressions which can be executed and will return a value. Unlike relational databases, mvStore doesn't support table expressions (where the returned result is a table).  

Because value expressions evaluate to a value, they can be used in place of values, like when passing a parameter to a function, or when specifying the value of a property with INSERT or UPDATE, or in search conditions.  

A value expression is one of the following:  

1. A constant or literal value.  
2. A property reference, or a positional property reference, or a path expression.  
3. A positional parameter reference.  
4. An operator invocation.  
5. A function call.  

Most of them are similar to standard SQL or C/C++.

#### Positional Properties
Format: $digit  

A dollar sign ($) followed by digits is used to represent a positional property in the body of a statement or class (family) definition. 
In other contexts, the dollar sign can be part of an identifier (or a dollar-quoted string constant).   

This feature is not self-contained in pathSQL. It implies a special invocation of the underlying kernel functions 
(e.g. `IStmt::createStmt` or `IStmt::execute`), allowing to provide the property names separately.
Please refer to the [HTTP GET](./mvStore server.md#http-get-support) section of the server documentation.
This could be used to enhance efficiency, or to prevent SQL injection attacks.

#### Positional Parameters
Format:  

1. :digit  
2. :digit(type)  -- parameter with specific type, only used in class family definitions

The colon (:) followed by digits is used to represent a positional parameter in the body of a statement or class definition. E.g.

  <code class='pathsql_snippet'>INSERT (PROP_I, PROP_S) VALUES (23, 'str');</code>
  <code class='pathsql_snippet'>CREATE CLASS hasPropI AS SELECT * WHERE PROP_I IN :0(INT);</code>  

Here, :0 designates the first parameter defining class `hasPropI`'s index. This parameter could be specified at query time as follows:

  <code class='pathsql_snippet'>SELECT * FROM hasPropI(23);</code>  

Or like this, provided we used `IN` in the class definition:

  <code class='pathsql_snippet'>SELECT * FROM hasPropI([20, 30]);</code>  

#### REFID
[PIN reference](./terminology.md#pin-reference)  
Format: @XXXXX[!Identity]
Where XXXXX is a [PID](./terminology.md#pin-id-pid) where X is a hexadecimal digit. A PID can be obtained via the built-in property mv:pinID.   

PIN references can be specified in the WHERE condition or operation target of SELECT/UPDATE/DELETE queries. 

#### URIID
[Property reference](./terminology.md#pin-reference)  
Format: PIN_REF.Name  
Where name is a [property](./terminology.md#property) name, and PIN_REF is a [PIN reference](#refid).

Note that a [class](./terminology.md#class) name can be used in place of PIN_REF, to specify the set of references to all classified PINs.

#### IDENTITY: mvStore user
Format: !Identity  
where [Identity](./terminology.md#identity) is the user name.  

#### REFIDELT: Element of a [collection](./terminology.md#collection)
Format: @XXXXX[!Identity].Property[ElementID]   


Data Types
----------
mvStore offers most of the basic [value](./terminology.md#value) types common to all programming languages.
Unlike relational databases, mvStore doesn't require length or precision specifications for any data type
(e.g. there are no fixed-length strings or binary strings). mvStore doesn't support user-defined data types either, yet,
but it does allow to attach a [unit of measurement](#units-of-measurement) to a value.

The type names listed here use the pathSQL convention. In the [C++](./terminology.md#c-interface) and [protocol-buffer](./terminology.md#protocol-buffer) interfaces,
these names are prefixed with "VT_" (e.g. VT_INT).

Sample: [types.sql](./sources/pathsql/types.html).  

### STRING
A string constant in SQL is an arbitrary sequence of characters bounded by single quotes ('): 'This is a string'.   
To include a single-quote character within a string constant, write two adjacent single quotes, e.g., 'Dianne''s horse'.   

*Note*: a string which is enclosed in double-quote characters (") is an [identifier](#identifiers).  

#### Supported Encoding
mvStore supports the UTF-8 encoding exclusively. All string data should be converted to UTF-8 before being passed to mvStore.  

### BSTR(Binary String)
pathSQL supports hexadecimal values, written X'val' or x'val' (with explicit quotes), where val contains hexadecimal digits (0..9, A..F, a..f),
and is expected to contain an even number of digits (a leading 0 must be inserted manually for odd number of hexadecimal digits).  

### URL
Format: U'url_addr'  

### ENUM
Format: Not supported yet   

### Numeric Types
The numeric types in mvStore are closer to C/C++ numeric types.  

Numeric constants are accepted in these general forms:   

  digits [type-suffix]  
  digits[.digits][e[+-]digits] [type-suffix]  

where **digits** is _one or more_ decimal digit in ASCII (0 through 9) or Unicode.  
*Note*: There must be at least one digit before and after the decimal point (if one is used).  
*Note*: At least one digit must follow the exponent marker (e) (if one is present).  
*Note*: There cannot be any space or other character embedded in a numeric constant.  
*Note*: Any leading plus or minus sign is not actually considered part of the constant; it is an operator applied to the constant.  

<p id="typesuffix">
The **type-suffix** is an alphabetical character appended to the numeric constant, to specify its type. It can be used in
the context of bitwise operations, or to store data with a specific format. If it is not specified, then mvStore
will select a default representation matching the value; it may convert the number to the most space-efficient data type that can 
represent this value.  
</p>

#### UINT
32-bit unsigned number  
range is [0,4294967295]  
[type-suffix](#typesuffix): 'u'  

#### INT
32-bit signed number  
range is [-2147483648,2147483647]  
[type-suffix](#typesuffix): none  

#### UINT64
64-bit unsigned number  
range is [0,18446744073709551615]  
[type-suffix](#typesuffix): 'U'  

#### INT64
64-bit signed number  
range is [9223372036854775807,-9223372036854775808]  
[type-suffix](#typesuffix): none  

#### DECIMAL
Not implemented yet. It is used to be store arbitary percision and scale of numberic data.

#### FLOAT
a numeric representation of a real number, following the common IEEE 754 standard; may lose precision in various circumstances  
range is [1.17549e-038F, 3.40282e+038f]  
[type-suffix](#typesuffix): 'f'  

Note that the suffix 'F' is not allowed, as it collides with the 'farad' [unit of measurement](#units-of-measurement). 

#### DOUBLE
similar to FLOAT, but with higher precision; it is the default representation for real numbers  
range is [2.22507e-308, 1.79769e+308]  
[type-suffix](#typesuffix): none  

Note that numbers that have a [unit of measurement](#units-of-measurement) suffix are automatically of this type.

#### BOOL
TRUE or FALSE  

### DATE/TIME Types  
Currently, pathSQL does not expose time zone control.  

#### DATETIME
Format: TIMESTAMP 'YYYY-MM-DD HH:MM:SS.XXXXXX', where the time and fractional second parts are optional  
range is ['1601-01-01 00:00:00.000001', '9999-12-31 23:59:59.999999']  

#### INTERVAL
Format: INTERVAL 'HHHHHHH:MM:SS.XXXXXX', the first number is hours, then minutes, seconds and (optional) fractional seconds part.  
In the future, year-month-day will be supported as well.  

### EXPR (expression definition)
Format:  $(expression)  

EXPR is the compiled form of an EXPRTREE, which is mostly used internally by the database engine.
An EXPR can be stored as a [value](./terminology.md#value), but it is not evaluated automatically at INSERT/UPDATE execution time 
(the value of that property will always be the EXPR itself, never its evaluation).
However, properties with type EXPR are evaluated automatically when they're used in expressions. E.g.

<pre>
  mvcommand>INSERT prop1=3;
  PIN@0000000000050001(1):(<prop1|VT_INT>:3)
  1 PINs INSERTED.
  
  mvcommand> UPDATE @50001 ADD prop2=prop1-1, prop3=$(prop1-1);  
  PIN@0000000000050001(3):(<prop1|VT_INT>:3       <prop2|VT_INT>:2       <prop3|VT_EXPR>:$(prop1 - 1))
  1 PINs INSERTED.

  mvcommand> SELECT * FROM {@50001} WHERE prop3=prop2; 
  PIN@0000000000050001(3):(<prop1|VT_INT>:3       <prop2|VT_INT>:2       <prop3|VT_EXPR>:$(prop1 - 1))
  1 PINs INSERTED.
  
  mvcommand> UPDATE @50001 SET prop1=2;  
  PIN@0000000000050001(3):(<prop1|VT_INT>:2       <prop2|VT_INT>:2       <prop3|VT_EXPR>:$(prop1 - 1))
  1 PINs INSERTED.
  
  mvcommand> SELECT * FROM {@50001} WHERE prop3<>prop2; 
  PIN@0000000000050001(3):(<prop1|VT_INT>:2       <prop2|VT_INT>:2       <prop3|VT_EXPR>:$(prop1 - 1))
  1 PINs INSERTED.
</pre>

In the example just above, `prop2` is stored directly with the result of the evaluation (at UPDATE execution time), while `prop3` is stored as type EXPR, 
which is only evaluated when queried.  

It's also possible to invoke such a EXPR property with parameters (up to 254). E.g.

<pre>
  mvcommand>
  INSERT prop1=3, prop2=$(prop1-:0);
  PIN@0000000000050001(2):(<prop1|VT_INT>:3       <prop2|VT_EXPR>:$(prop1 - :0))
  1 PINs INSERTED.
  
  mvcommand>
  SELECT * WHERE prop2(1) = 2;
  PIN@0000000000050001(2):(<prop1|VT_INT>:3       <prop2|VT_EXPR>:$(prop1 - :0))
  1 PINs SELECTED.
</pre>

Note that mvstore can support missing or extraneous parameters.
  
### EXPRTREE
This is an internal, transient type used primarily in C++, to build expression trees before they are compiled by mvStore into
expressions (EXPR).

### QUERY (query statement)
Format:  ${statement}  

QUERY is similar to EXPR, but for a whole statement.

### ARRAY/CNAVIGATOR ([Collection](./terminology.md#collection)) 
Format:   

1. (elem1,...,elemN) -- SQL standard style. *Note*: (0) is a int (the parentheses in this case are not interpreted as defining a set)  
2. {elem1,...,elemN} -- pathSQL extension. *Note*: {0} specifies a one-element collection  

Please refer to the [definition of 'collection'](./terminology.md#collection).  

  <code class='pathsql_snippet'>INSERT (prop2,prop3) VALUES(123 ,{123, 'test', 120, 534});</code>
  <code class='pathsql_snippet'>SELECT * WHERE prop3[3] = 534;</code>  
  
Internally, smaller collections are stored with a representation similar to an array (the type is ARRAY).
Larger collections are stored in the B-tree (the type becomes CNAVIGATOR), enabling enormous collections
with fast retrieval of known eids. The transition between those two states is transparent, and applications
should not assume that a collection will be stored as an ARRAY.  

The transition between a scalar value and a collection is also designed to be relatively transparent
(with a core query syntax that applies to both cases indifferently).

For more information about collections, see [comparisons involving collections](#comparisons-involving-collections),
[value in collection](#value-in-collection) and [UPDATE ADD/SET](#update).  

*Note*: although mvStore doesn't support nested collections yet, it is possible to implement similar functionality by combining multiple PINs (or properties), e.g. by adding collection references to a collection.  

### Range
Format: [number1, number2]   
it can be used with keywork IN. The meaning is the same as BETWEEN number1 AND number2.  
*Note*: * is used here to denote the infinity number.

Examples: [between_in.sql](./sources/pathsql/between_in.html). 

### Reference types

Type Name      Description
---------      -----------
REF            A reference to another PIN by its IPIN*.
REFID          A reference to another PIN by its PID.
REFPROP        A reference to a value (property of this or another PIN) by its IPIN* and PropertyID.
REFIDPROP      A reference to a value (property of this or another PIN) by its PID and PropertyID.
REFELT         A reference to a collection element by its IPIN*, PropertyID and ElementID.
REFIDELT       A reference to a collection element by its PID, PropertyID and ElementID.

*Note*: The distinction between REF and REFID only applies to the [C++ interface](./terminology.md#c-interface). REF allows to specify directly an IPIN*.  
You can see the format of all there reference types is here: [Reference and Dereference Operators](#reference-and-dereference-operators).

### CURRENT
Not yet documented.

### STREAM
Not yet documented.

Units of Measurement
--------------------
mvStore allows to attach [units](./terminology.md#unit-of-measurement) to [double](#double)-precision floating point numbers, 
to enhance the self-descriptiveness of data, and interoperability. mvStore automatically converts values between different units 
when performing computations on compatible types.

The syntax simply requires to append the chosen unit suffix to a literal value (wherever a value is legal). Note that suffixes
are case-sensitive, and unit suffixes can not be used together with [type-suffixes](#typesuffix). 

*Note*:  In pathSQL, integers with a unit suffix will be converted to double/float automatically (only float/double 
values can have a unit suffix). That's because as soon as unit conversions are involved, whole integer values become
very unlikely (e.g. 1 inch = 0.0254 meter; 1 inch + 1 meter = 1.0254 meter).  

Sample: [units.sql](./sources/pathsql/units.html)

Here is a table of all units supported by mvStore.  

Suffix        Description
------        -----------  
m             meter  
kg            kilogram  
s             second  
A             ampere  
K             kelvin  
mol           mole  
cd            candela  
Hz            hertz  
N             newton  
Pa            pascal  
J             joule  
W             watt  
C             coulomb  
V             volt  
F             farad  
Ohm           ohm  
S             siemens  
Wb            weber  
T             tesla  
H             henri  
dC            degree Celsius  
rad           radian  
sr            steradian  
lm            lumen  
lx            lux  
Bq            becquerel  
Gy            gray  
Sv            sievert  
kat           katal  
dm            decimeter  
cm            centimeter  
mm            millimeter  
mkm           micrometer  
nm            nanometer  
km            kilometer  
in            inch  
ft            foot  
yd            yard  
mi            mile  
nmi           nautical mile  
au            astronomical unit  
pc            parsec  
ly            light year  
mps           meters per second  
kph           kilometers per hour  
fpm           feet per minute  
mph           miles per hour  
kt            knot  
g             gram  
mg            milligram  
mkg           microgram  
t             ton  
lb            pound  
oz            ounce  
st            stone  
m2            square meter  
cm2           square centimeter  
sqin          square inch  
sqft          square foot  
ac            acre  
ha            hectare  
m3            cubic meter  
l             liter  
cl            centiliter  
cm3           cubic centimeter  
cf            cubic foot  
ci            cubic inch  
floz          fluid once  
bbl           barrel  
bu            bushel  
gal           gallon  
qt            quart  
pt            pint  
b             bar  
mmHg          millimeters of mercury  
inHg          inches of mercury  
cal           calorie  
kcal          kilo-calorie
dF            degrees Fahrenheit  

Functions and Operators
-----------------------
mvStore supports many common functions and operators available in relational databases, and usage is almost the same.   

Internally mvStore regards all functions as operators, so here we discuss them together. 
 
Sample: [functions.sql](./sources/pathsql/functions.html).

### Logical Operators  

Operator       Description
--------       -----------  
NOT            logical not: NOT TRUE is FALSE; NOT FALSE is TRUE. 
OR             logical or:  return TRUE if one of the operands is TRUE; otherwise return FALSE. 
AND            logical and: return TRUE if both of the operands are TRUE; otherwise return FALSE. 


### Comparison Functions and Operators  

Functions and Operators Description   

Operator                    Description
--------                    -----------
<                           less than 
>                           greater than
<=                          less than or equal to  
>=                          greater than or equal to 
=                           equal  
<>                          not equal
expr BETWEEN min AND max    return (expr>=min and expr<= max) 
expr IN [min, max]          return (expr>=min and expr<= max). The [min, max] is a value with RANGE type.  
expr IN list                return whether or not expr is equal to one value of the list. 

These binary comparison operators can support not only single-value right-hand operands, but also a list of values with [ANY/SOME/ALL qualifier](#anysomeall-qualifier). 
The List can be a collection, or a list of values returned by sub-query. 

*Note*: The condition "PROP<>val" will not filter out PINs without property "PROP".

#### Comparisons Involving Collections  

1. value = collection 	-- same as  "value IN collection"    
2. collection1 IN collection2  -- for each element in collection1, check {the element's value IN collection2}  

The default behaviour for operator = is to check if ANY element is = the compared value, whereas for every other comparison operator, the default behavior is to check how ALL elements compare with the value.
Currently mvStore only exposes this default behavior.

### Arithmetic Operators

Operator     Description                                           Example        Result
--------     -----------                                           -------        ------
+            addition                                              2 + 3          5  
-            subtraction                                           2 - 3          -1 
*            multiplication                                        2 * 3          6  
/            division (integer division truncates the result)      4 / 2          2  
%            modulo (remainder)                                    5 % 4          1  
^            exponentiation                                        2.0 ^ 3.0      8  
&            bitwise AND                                           91 & 15        11 
|            bitwise OR                                            32 | 3         35 
#            bitwise XOR                                           17 # 5         20 
~            bitwise NOT                                           ~1             -2 
<<           bitwise shift left                                    1 << 4         16 
>>           bitwise shift right                                   -123 >> 63     -1 
>>>          bitwise unsigned shift right                          -123 >>> 63    1  


### Mathematical Functions (scalar)

Function                          Description
--------                          -----------
ABS(number)                       returns the absolute value of number
LN(number)                        natural logarithm
EXP(number)                       exponential
POWER(number a, number b)         a raised to the power of b        
SQRT(number)                      square root
FLOOR(number)                     largest integer not greater than argument
CEIL(number)                      smallest integer not less than argument

### Aggregation Functions:

Function                          Description
--------                          -----------
AVG(expression)                   Returns the average value of the values in expression.
MIN(expression)                   Returns the smallest value in expression. 
MAX(expression)                   Returns the largest value in expression.  
SUM(expression)                   Returns the sum of the in values in expression.
COUNT(expression)                 Returns the number of times expression was not null. Expression can be property name or a collection. If a collection is specified, returns the cardinality of the collection.
VAR_POP(expression)               Returns the biased variance (/n) of a set of numbers. The formula used to calculate the biased variance is: VAR_POP = SUM(X**2)/COUNT(X) - (SUM(X)/COUNT(X))**2
VAR_SAMP(expression)              Returns the sample variance (/n-1) of a set of numbers. The formula used to calculate the sample variance is: VAR_SAMP=(SUM(X**2)-((SUM(X)**2)/(COUNT(*))))/(COUNT(*)-1)
STDDEV_POP(expression)            Returns the biased standard deviation (/n) of a set of numbers. The formula used to calculate the biased standard deviation is: STDDEV_POP = SQRT(VAR_POP)
STDDEV_SAMP(expression)           Returns the sample standard deviation (/n-1) of a set of numbers. The formula used to calculate the sample standard deviation is: STDDEV_SAMP = SQRT(VAR_SAMP)

The 'expression' can be a list of values or a collection. If a collection is specified, the function will include all its elements in the calculation.
These functions can also support [DISTINCT/ALL qualifier](#distinctall-qualifier) to indicate whether or not duplicate values should be included in the expression, e.g. AVG(DISTINCT expression).

### String Operators

Operator              Description
--------              -----------
||                    string concatenation  

### String Functions

Function                                                                               Description
--------                                                                               -----------
LENGTH( {string|collection} )                                                          string length or collection cardinality.  
LOWER(string)                                                                          change all characters to lowercase.    
UPPER(string)                                                                          change all characters to uppercase.  
TONUM(string)                                                                          convert the value type of 'string' to number. 
TOINUM(string)                                                                         convert the value type of 'string' to integer format. 
POSITION(str, subStr)                                                                  return the position of subStr in str, or -1 if not found.
SUBSTR(str,[pos=0,]len)                                                                return a substring of str of length len, starting at pos. 
REPLACE(string, subStr, newSubStr)                                                     replace all occurences of subStr in string with newSubStr. 
PAD(string, length, padStr)                                                            pad string with padStr until the string length is length.
TRIM([{BOTH | LEADING | TRAILING} [remstr] FROM] str), TRIM([remstr FROM] str)         return str without the leading or trailing characters specified in remstr. BOTH is the default. If remstr is not specified, spaces are removed. 
CONTAINS(string, subStr)                                                               return whether string contains subStr or not.
BEGINS(string, prefix)                                                                 return whether or not the prefix is heading part of string.
ENDS(string, suffix)                                                                   return whether or not the suffix is ending part of string. 
REGEX                                                                                  not supported yet in mvStore.
CONCAT(str1,str2,...)                                                                  return the string that results from concatenating the arguments.
MATCH [(property list)] AGAINST(string)                                                full-text search for string in specified properties of PINs. If no property list is specified, then search all properties.

Sample: [full_text_search.sql](./sources/pathsql/full_text_search.html).  

### EXTRACT(unit FROM date) 
Extract the unit part of the date/time/timestamp.  
The possible units are: YEAR, MONTH, DAY, HOUR, MINUTE, SECOND.  

### CAST(expr AS type) 
Convert expr to the specified type.
The type name can be any type supported by mvStore.  

### COALESCE

.       -- class/property name separator   

### IN

Operator                    Description
--------                    -----------
expr IN [min, max]          return (expr>=min and expr<= max). The [min, max] is a value with RANGE type.  
expr IN list                return whether or not the val is equal to one value of the list. The List can be a collection, or a list of values returned by sub-query.  

### EXISTS

Operator                    Description
--------                    -----------
EXISTS(property)            return "property IS NOT NULL".
EXISTS(list)                return "COUNT(list)>0". The List can be a collection, or a list of values returned by sub-query.

Sample: [exists.sql](./sources/pathsql/exists.html)

### ANY/SOME/ALL qualifier
These qualifiers can only be used as right operands of the binary comparison operators. E.g.

Sample                   Description    
------                   -----------
val < ANY (list)         return true if val< any element of the list, otherwise return false.
val < SOME(list)         some as "val < ANY (list)"
val < ALL (list)         return true if val< all element of the list, otherwise return false.

Sample: [collection_operators.sql](./sources/pathsql/collection_operators.html)

### DISTINCT/ALL qualifier

Operator                         Description
--------                         -----------
DISTINCT list                    return the list of values after eliminating the duplicate values. In the case of a list of pins, comparison is based on PIDs.
DISTINCT VALUES pins             return the list of values after eliminating the duplicate values of PINs (excluding PIDs).
ALL list                         return the list of values without eliminating duplicates.

There are three contexts where to use these qualifiers:

  - SELECT list (e.g. `SELECT DISTINCT prop1 FROM class1`)  
  - Parameter passed to an aggregation function (e.g. `AVG(DISTINCT {1.0, 2.0})`)  
  - list of values returned by sub-query and used as operands of set operators (e.g. `query1 UNION DISTINCT(prop1,prop2) query2`)  
 
ISLOCAL
Not yet documented.

### Collection Functions and Operators

Function/Operator      Expression Sample              Description
-----------------      -----------------              -----------
[ ]                    property[position]             Fetch the value at the specified position in the collection. position can be a number (starts at 0) or one of these values: LAST_ELEMENT, FIRST_ELEMENT, SOME_ELEMENT, ALL_ELEMENTS.
COUNT                  COUNT(collection)              Return the cardinality of that collection.
IN                     val IN collection              Return whether or not the val is equal to one value of the collection. 
IN                     collection1 IN collection2     Return whether or not all values of collection1 are IN collection2.   


#### Value IN Collection
value1 IN value2 is interpreted by pathSQL to mean "is value1 part of the collection value2?".  

### Reference and Dereference Operators
Reference operator: &  
Dereference operator: *  

*Note*: & can have 2 meanings: "bitwise AND" and "dereference"; it depends on the context where it is used.   

A few examples (here X is a hexadecimal digit, XXXXXXXXXXXXXXXX is a PID):

Expression                            Meanning
----------                            --------
@XXXXXXXXXXXXXXXX                     Return the PIN reference.
*@XXXXXXXXXXXXXXXX                    Return the value of this pin, which is the value of the special mv:value property in this PIN (this values can be set; it can be an EXPR). 
@XXXXXXXXXXXXXXXX.prop                Return the value of prop in pin @XXXXXXXXXXXXXXXX.  
&@XXXXXXXXXXXXXXXX.prop               Return the reference to the prop in pin @XXXXXXXXXXXXXXXX.  
@XXXXXXXXXXXXXXXX.prop[0]             Return the element value of the prop in pin @XXXXXXXXXXXXXXXX.  
&@XXXXXXXXXXXXXXXX.prop[0]            Return the element reference of the prop in pin @XXXXXXXXXXXXXXXX.  

Additional examples: [reference.sql](./sources/pathsql/reference.html).  
  
### Precedence of Operators and Functions (in decreasing order)
Most operators have the same precedence and are left-associative.
The precedence and associativity of the operators is hard-coded in the parser.
To circumvent default precedence, just use parentheses.

Operator/Function     Associativity       Description
-----------------     -------------       -----------
any function,$()      right               any built-in function, expression
.                     left                class/property name separator
[ ]                   left                collection element selection 
&,*                   right               reference, dereference                   
-, ~                  right               unary minus, unary bit inversion 
^                     left                exponentiation
*,/,%                 left                multiplication, division, modulo
+,-                   left                addition, subtraction
||                    left                string concatenation
<<,>>,>>>             left                bitwise shift left, bitwise shift right, bitwise unsigned shift right 
&                     left                bitwise and
^                     left                bitwise xor (exclusive or)
|                     left                bitwise or (inclusive or)
IS A, IS NOT A        left                class membership check, e.g. mv:pinID IS A class_name
IS, IS NOT            left                IS TRUE, IS FALSE, IS UNKNOWN, IS NULL, 
IN                    left                collection membership
BETWEEN...AND...      left                range containment                        
<,<=,>, >=            left                less than, less than or equal to, greater than, greater than or equal to
=,<>                  left                equal, not equal
NOT                   right               logical negation 
AND                   left                logical conjunction 
OR                    left                logical disjunction
${}                   right               query


Statements (BNF)
----------------
In this section we describe the pathSQL BNF. Here are the display conventions used:

Expression                Meaning
----------                -------
UPPERCASE                 KEYWORD 
lowercase                 terminal or non-terminal fragment of statement 
[ ]                       optional fragment 
{A|B}                     choose fragment A or B 
...                       repeat the previous statement fragment type 

### Store Management Statements
Synopsis: 

  - CREATE STORE [IN 'directory'] [OPTIONS(...)], where options have format: NAME=value[,NAME=value..]
  - DROP STORE [IN 'directory']
  - MOVE STORE [FROM 'source directory'] TO 'destination directory'
  - OPEN STORE [IN 'directory'] [OPTIONS(...)]
  - CLOSE STORE

If 'directory' is not specified, mvstore defaults to the "current directory" (platform dependent).  

*Note*: The C++ API for these statements (`manageStores(...)`) is different from the API for other statements (`ISession.createStmt(...)`), because store management statements are not necessarily bound to a db connection.  

List of option names for OPEN and CREATE (case insensitive):  

  - NBUFFERS=number  
  - LOGBUFSIZE=number  
  - MAXFILES=number  
  - SHUTDOWNASYNCTIMEOUT=number  
  - PASSWORD='string'  
  - LOGDIRECTORY='directory' (mapped using call to IMapDir::map(SO_LOG...) if provided)  

Additional option names for CREATE:  

  - PAGESIZE=number  
  - FILEEXTENTSIZE=number  
  - OWNER='string'  
  - STOREID=number  
  - ENCRYPTED={TRUE|FALSE}  
  - MAXSIZE=number  
  - LOGSEGSIZE=number  
  - PCTFREE=floating or double number  

Options can be specified in any order.   


### DDL
Here's a description of pathSQL's Data Definition Language.

#### CREATE CLASS
Synopsis:  

  - CREATE CLASS class_name [OPTIONS( {VIEW|CLUSTERED|SOFT_DELETE} )] AS query_statement.

where the query_statement is a [SELECT QUERY](#query). Here's a description of the OPTIONS:  

  - DEFAULT: This is the default mode (all [PIDs](./terminology.md#pin-id-pid) will be indexed by this class).  
  - VIEW: Like view in relational db, it is just a query definition for usability.  
  - CLUSTERED: Using clustered index to maintain all [PIDs](./terminology.md#pin-id-pid), for increased performance. Not yet implemented.  
  - SOFT_DELETE: Create an index not only for normal pins, but also for those pins marked as deleted (but not purged).  

Examples: [class.sql](./sources/pathsql/class.html).   

The "IS A" operator can be used to check whether or not a pin belongs to a class. For example, those two statements are equivalent:  
 
        SELECT * WHERE mv:pinID IS A class1;  
        SELECT * FROM class1;  

#### Creating a [class family](./terminology.md#family)  

        CREATE CLASS clsfml11 AS select * where prop1 = :0 and prop2 = :1;    
        select * from clsfml11(*, 2);    

Here * indicates all values, including NULL. In this case, the [index](./terminology.md#index) is created with the composite key(prop1 and prop2)  

**Limitation 1**: The kernel uses a BTree to store indexes, and can't store a PIN whose properties are all NULL. 
NULL can be passed as a parameter to a class family only when the index for this class family is a multi-segment index.
Single-property indexex cannot support NULL parameters.
For performance reasons, it is recommended not to create a class family with only one parameter passed to the where clause, such as: `WHERE :0 is NULL`.

**Limitation 2**: There's a sytactic restriction on the order of parameters in class predicates. For example, mvStore cannot create an index for `:0 = value`,
but `value = :0` is fine.

*Note*: mvStore can ignore superfluous parameters, i.e. the user can pass more parameters than used in the predicate.

Please refer to the [class](./terminology.md#class), [family](./terminology.md#family) and [indexing](./terminology.md#index) descriptions for
a brief comparison with the relational DDL. Note that it is possible to declare multiple families with the same predicate, and different
type specifications:

        CREATE CLASS clsfml21 AS select * where prop1 = :0(int);  
        CREATE CLASS clsfml22 AS select * where prop1 = :0(String); 

In this case, if a PIN's prop1 is a string which cannot be converted into a number, then it won't be part of clsfml21.

If the parameter type is not specified, then the class family index is created with a typeless index, preserving
the original type of data items, and performing implicit coercions at evaluation time.  

All class options work for class families as well, except SOFT_DELETE. 

##### Indexing Of Collections 
For single-property indexes, all elements will be added to the index.  
For multi-segment indexes, all combinations will be added to the index (Cartesian product of all values of the indexed properties).  

##### How To Specify Key Value Order For Index
The available options are:  

  - ASC:  Sort keys in ascending order.  
  - DESC: Sort keys in descending order.  
  - NULLS FIRST: Order the null values (e.g. absent property) before any non-null value.  
  - NULLS LAST: Order the null values after any non-null value.  

Example:  

        CREATE CLASS clsfml5 AS select * where prop1 = :0(int, desc, nulls first)and prop2=:1(int);  

### DML
Here is a description of pathSQL's Data Manipulation Language.  

#### INSERT
Synopsis:  

  - INSERT (property [, ...]) VALUES ( expression [, ...] ) [, ...]   
  - INSERT property = expression [, ...]  
  - INSERT SELECT ...  

Examples: [insert.sql](./sources/pathsql/insert.html).

*Note*: pathSQL does not yet support the insertion of graphs (with cycles) in a single statement; the C++ interface does.  

#### UPDATE
Synopsis:  

  - UPDATE [{pin_reference|class_name| class_family_name({expression_as_param| *| NULL}, ...)}] actions [WHERE conditions]  

where *actions* can be:  

  - {SET|ADD} property = expression [, ...]  
  - DELETE property [, ...]   
  - RENAME property = new_property [, ...]  
  - MOVE collection_property[element_id] {BEFORE|AFTER|TO} {element_id|LAST_ELEMENT|FIRST_ELEMENT}  
  - EDIT ...  

and *pin_reference* can be:
  
  - a pin reference (@PID, e.g. @D001). *Note*: when the UPDATE statement is used as a value of a property of type QUERY, then the AT sign (@) can be used to denote the PIN ID which is being processed.  
  - a collection of pin references with format: { @PID[, ...] }, such as {@D001, @D002}.  

and *expression_as_param* can be any [expression](#value-expressions).  

Examples: [update.sql](./sources/pathsql/update.html).  

Notes:  

1. UPDATE {SET|ADD} a non-existing property: add a property   
2. UPDATE SET an existing property: change the value of that property (if the property is a collection, overwrite the whole collection)   
3. UPDATE ADD an existing property: append a new value to that property (if the property only has one value, then change the type to collection, and append the new value)  

Also pathSQL supports C-style operation-assignments `op=`, where op is one of +,-,*,/,%,&,|,^,<<,>>,>>>,min,max,||. For example:  
        
        UPDATE * SET prop+=1;

Any reference to a non-existing property will make the query return without any result set. In order to skip those PINs missing the property, you can use 
'!' modifiers in UPDATE, and only process those PINs which include that property using the '?' modifiers, such as:  
        
        UPDATE * SET prop!=0, prop?+=1;

This statement will update all PINs: for PINs without "prop" property, it will add this property; for PINs already having "prop", it will increment its value.

#### DELETE/UNDELETE/PURGE   
Synopsis:  

  - {DELETE|UNDELETE|PURGE}  
    [FROM {pin_reference|class_name| class_family_name({expression_as_param| *| NULL}, ...)}]  
    [WHERE conditions]  

where

  - DELETE:    Mark PINs in deleted status ("soft delete").  
  - UNDELETE:  Change from deleted status to normal active status.  
  - PURGE:     Permanently delete PINs from the physical disk (note: cannot remove PINs in deleted status).  
 
Examples: [delete.sql](./sources/pathsql/delete.html).  

### QUERY

Synopsis: 

  - SELECT [ * | {property_name [AS new_name] } [, ...] ]  
    [ FROM from_item [, ...] ]  
    [ WHERE conditions ]  
    [ GROUP BY {property_name | expression | position} [ASC | DESC][ NULLS { FIRST | LAST } ] [, ...] ]  
    [ HAVING conditions ]  
    [ { UNION | INTERSECT | EXCEPT } [ ALL ] select ]  
    [ ORDER BY {property_name | expression | position} [ ASC | DESC ] [ NULLS { FIRST | LAST } ] [, ...] ]  

where *from_item* can be one of:
  
  - pin_reference
  - class_name 
  - class_family_name({expression_as_param| *| NULL}, ...) 
  - path expression
  - from_item join_type from_item [ ON join_condition | USING ( join_column [, ...] ) ]
  - sub_query AS alias_name
  - from_item AS alias_name

and *join_type* can be one of:

  - [ INNER ] JOIN
  - LEFT [ OUTER ] JOIN
  - RIGHT [ OUTER ] JOIN
  - FULL [ OUTER ] JOIN
  - CROSS JOIN

#### Alias name in FROM clause
A substitute name for the FROM item containing the alias. An alias is used for brevity or to eliminate ambiguity for self-joins (where the same table is scanned multiple times). 
When an alias is provided, it completely hides the actual name of the class or family; for example given FROM foo AS f, the remainder of the SELECT must refer to this FROM item as f, not foo.

#### Order by
Examples: [orderBy.sql](./sources/pathsql/orderBy.html).   

  - ORDER BY must appear after ALL the unionsbut .  
  - ORDER BY is considered to apply to the whole UNION result (it's effectively got lower binding priority than the UNION).  

To order a subquery result, use parentheses around the subquery.  

*Notes*:  
1. In order to include null values, NULLS FIRST/LAST must be added to the ORDER BY clause. 
2. The default behavior is order by ASC, without NULL value PINs.

#### Group by
Examples: [groupBy.sql](./sources/pathsql/groupBy.html).   

#### Set Operators: UNION | INTERSECT | EXCEPT
Examples: [set_operator.sql](./sources/pathsql/set_operator.html).   

The functionality of all these set operators is similar to standard SQL, 
except that mvStore does not require that all operands have same number of properties or types. 
Duplicates are identified based on [PIN ID](./terminology.md#pin-id-pid) instead of property value, which is differnt from standard SQL.

The keyword DISTINCT/ALL can be used to eliminate duplicates.

#### Join
mvStore returns immutable PIN collections as query results.

        SELECT * FROM class1 as c1 join class1 as c2 on (c1.prop1 = c2.prop2);

mvStore supports every kind of JOIN (LEFT/RIGHT/FULL/CROSS JOIN), except the natural JOIN.

Examples: [join.sql](./sources/pathsql/join.html).   

#### Sub query in FROM clause
This is not yet supported.

In a future release, when a sub-SELECT appears in the FROM clause, it will act as though its output were created as a temporary table for the duration of this single SELECT command. 
Note that a sub-SELECT must be surrounded by parentheses. 

### Inheritance
mvStore's classification model lets a PIN belong to multiple classes, and also allows to define a hierarchy of classes, such as:

        CREATE CLASS Person AS SELECT * WHERE EXISTS(firstname) OR EXISTS(lastname);
        CREATE CLASS Taxpayer AS SELECT * FROM Person;

Examples: [inheritance.sql](./sources/pathsql/inheritance.html). 

#### How to query only PINs belonging to 2 classes

There are 2 ways:  

  - Using built-in property mv:pinID in WHERE CLAUSE, e.g. SELECT * WHERE class1.mv:pinID=class2.mv:pinID.
  - Using operator & for class names in FROM CLAUSE, e.g.  SELECT * FROM class1 & class2.

### TRANSACTIONS
mvStore not only supports basic transactions, but also sub-transactions.
The session holds a transaction stack.  Every sub-transaction can be rolled back independently (without affecting the state of the whole transaction).
Changes are committed to the database only when the outermost transaction in the stack is committed.  

Examples: [transaction_basic.sql](./sources/pathsql/transaction_basic.html).  

#### Start a Transaction
START TRANSACTION is used to start a transaction/sub-transaction block.

Synopsis: 

  - START TRANSACTION [ transaction_mode [, ...] ]

where transaction_mode is one of:  
 
  - ISOLATION LEVEL { READ UNCOMMITTED | READ COMMITTED | REPEATABLE READ  | SERIALIZABLE }   
  - READ ONLY |READ WRITE  

Examples:  
[transaction_readonly.sql](./sources/pathsql/transaction_readonly.html),
[transaction_sub.sql](./sources/pathsql/transaction_sub.html).   

Note:     
1. mvStore doesn't support isolation level READ UNCOMMITTED.  
2. When READ ONLY is specified, no operation in this transaction must write, otherwise the transaction will fail.  
3. When READ ONLY is specified, mvStore uses the Read-Only Multi-Version Concurrency Control (ROMV), which will not block (or be blocked by) any read/write transaction.  

#### End a Transaction
##### COMMIT
Synopsis: 

  - COMMIT [ALL]; 

If ALL is specified, then mvStore will commit the whole stack of transactions (started in the current session), otherwise it only commits the innermost transaction/sub-transaction block in the stack.    

##### ROLLBACK
Synopsis: 

  - ROLLBACK [ALL];  
    
If ALL is specified, then mvStore will rollback the whole stack of transactions (started in the current session), otherwise it only rolls back the innermost transaction/sub-transaction block in the stack.    

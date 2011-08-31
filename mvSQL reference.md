The mvSQL Language
==================
mvSQL is the name of a dialect of SQL defined for mvStore. The [mvStore data model](./terminology.md#essential-concepts-data-model) is very different
from the relational model, but mvSQL is designed to remain as close to SQL as possible. 
This page presents a thorough survey of the language. It covers the
elements of the [syntax](#mvsql-syntax), the [data types](#data-types) and the [operators](#functions-and-operators).
It also provides a formal [BNF description](#statements-bnf) of the [DDL](#ddl) and [DML](#dml).
For a quick practical overview, please visit the ["getting started"](./mvSQL getting started.md) section.

It's easy to test any of these commands in the [mvcommand](./terminology.md#mvcommand) console.  

_Note: The console itself offers a few additional keywords that are not part of mvSQL (see [mvcommand.doc](../../mvcommand/doc/README.txt))._  
_Note: The SQL used to talk to [mvEngine](./terminology.md#mvengine) in MySQL is unrelated with mvSQL._

mvSQL Syntax
------------
### Lexical Structure
mvSQL supports the following token types: [keywords](#keywords), [identifiers](#identifiers), [qnames](#qnames), [constants](#constants), [operators](#operators), [comments](#comments), and [special characters](#special-characters).

#### Keywords
mvSQL's coverage of standard SQL keywords depends on functional areas.

mvSQL supports most of the keywords related to common [DML](#dml) (Database Manipulation Language): SELECT, UPDATE, DELETE, FROM, CAST, built-in functions etc.

mvSQL doesn't support the relational DDL (Data Definition Language) and DCL (Database Control Language): no table, no view, no primary or foreign key, no unique or check constraint.  However, mvStore introduces the [CLASS](#ddl) keyword.

mvSQL doesn't support any DSPL (Data Stored Procedure Language).  

_Note: Keywords are **case insensitive**. A common convention is to write keywords in upper case._

#### Identifiers 
Identifiers are used to designate mvStore entities such as [classes](./terminology.md#class), [properties](./terminology.md#property) etc.  Identifiers are **case sensitive**.  See also the
next section about [qnames](#qnames).

There are 2 types of identifiers:

1. plain identifiers: they begin with a letter (upper or lower case, including diacritical marks and non-latin characters) or an underscore (_), and subsequent characters can also be digits. 
2. quoted identifiers (aka delimited identifiers): they are formed by enclosing any arbitrary sequence of characters in double-quotes ("), except the character '\0'. A delimited identifier is never a keyword ("select" could be used to refer to a property named _select_).

_Note: To include a double quote, write two double quotes._  

_Note: A string which is enclosed in single quotes (') is a string constant, not an identifier._

Sample: [identifier.sql](../../test4mvsql/test/identifier.sql)

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
mvSQL understands most common [value](./terminology.md#value) types.  Some standard constants are
associated with these value types, such as TRUE and FALSE.
Refer to [Data Types](#data-types) for more details.  

#### Operators
mvSQL supports most of the standard SQL operators (logic, comparison, arithmetic, aggregation, string manipulations, date and time manipulations etc.).
Refer to [Functions and Operators](#functions-and-operators) for more details.   

#### Comments
A comment is removed from the input stream before further syntax analysis.

mvSQL supports 3 styles of comments:

1. SQL-style: A sequence of characters beginning with double dashes (--) and extending to the end of the line, e.g.:   

		-- This is a standard SQL comment   

2. C-style: This syntax enables a comment to extend over multiple lines (the beginning and closing sequences need not be on the same line). The comment begins with /* and extends to the matching occurrence of */. These blocks can be nested, as specified in the SQL standard (but unlike C): one can comment out larger blocks of code that might contain existing block comments. For example:

    /* multiline comment
    * with nesting: /* nested block comment */
    */  

3. SPARQL-style: A sequence of characters beginning with number sign (\#) and extending to the end of the line, e.g.:

		\# This is a SPARQL comment

#### Special Characters
Some non-alphanumeric characters have special meaning, without being [operators](#operators).

Some cases are extensions specific to mvSQL:

1. The dollar sign ($), followed by digits, is used to represent a positional [_property_](./terminology.md#property) in the body of a statement or class definition. Other uses are ${statement} and $(expression), to indicate a statement/expression variable. In other contexts the dollar sign can be part of an identifier or a dollar-quoted string constant.   
2. The colon (:), followed by digits, is used to represent a positional [_parameter_](./terminology.md#parameter) in the body of a statement or class definition. The colon is also used in [QNames](#qnames).   
3. The period (.) can be used to separate store, class, and property names. It can also be part of numerical constants.   
4. Brackets ({}) are used to select the elements of a collection.    

Other cases are standard:

1. Parentheses (()) group expressions and enforce precedence. In some cases parentheses are required as part of the fixed syntax of a particular SQL command.   
2. Commas (,) are used in some syntactical constructs, to separate the elements of a list.   
3. The semicolon (;) terminates an SQL command. It cannot appear anywhere within a command, except within a string constant or quoted identifier.   
4. The asterisk (\*) is used in some contexts to denote all values of a property or all properties of a PIN or composite value. It also has a special meaning when used as the argument of an aggregate function, namely that the aggregate does not require any explicit parameter.   

### Value Expressions
Value expressions are expressions which can be executed and return a value. Unlike relational databases, mvStore doesn't support table expressions (where the returned result is a table).   

Because value expressions evaluate to a value, they can be used in place of values, like when passing a parameter to a function, or when specifying the value of a property with INSERT or UPDATE, or in search conditions. 

A value expression is one of the following:  

1. A constant or literal value  
2. A property reference or a positional property reference  
3. A positional parameter reference  
4. An operator invocation   
5. A function call   

Most of them are similar to standard SQL or C/C++.

<p style="color:red">
TODO (maxw): special expressions should be pointed out here
</p>

#### Positional Properties
Format: $digit  

A dollar sign ($) followed by digits is used to represent a positional parameter in the body of a statement or class (family) definition or a prepared statement. In other contexts the dollar sign can be part of an identifier or a dollar-quoted string constant.   

  mvcommand> PREPARE STATEMENT stmt1 WITH PROPERTIES (prop1, prop2) AS  
     SELECT * WHERE (CONTAINS($0,'pin') AND EXISTS($1));

This statement is supported in mvcommand (not in mvSQL). mvcommand will pass 'prop1' to mvSQL (replacing the positional property $0).  

There is no significant benefit in using positional properties, except to relieve the store from parsing property names, when one already knows a property ID (this applies mostly to C++ clients).

#### PARAM: Positional Parameters
Format:  

1. :digit  
2. :digit(type)  -- parameter with specific type, only used in class family definitions

The colon (:) followed by digits is used to represent a positional parameter in the body of a statement or class definition. E.g.

  mvcommand> INSERT (PROP_I, PROP_S) VALUES (23.1, 'str');    
  Committed one PIN successfully.   
    
  mvcommand> PREPARE STATEMENT stmt1 AS  
     SELECT * WHERE PROP_I=:0(INT);   
  Prepared statement "stmt1" successfully.  
      
  mvcommand> EXECUTE STATEMENT stmt1 WITH PARAMS(2);  
  PIN@327683(2):(<prop1|VT_STRING>:pin1	<prop2|VT_INT>:2)  
  1 PINs SELECTED.  

These statements are supported in mvcommand (not in mvSQL). mvcommand will pass parameter '2' to mvSQL (replacing the positional parameter :0).  

The benefit of positional parameters is obvious when executing a statement several times with different parameter values.

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
Unlike relational databases, mvStore doesn't support length or precision specifications for any data type
(e.g. there are no fixed-length strings or binary strings). mvStore doesn't support user-defined data types either,
although it does allow to attach a [unit of measurement](#unit-of-measurement) to a value.

The type names listed here use the mvSQL convention. In the [C++](./terminology.md#c-interface) and [protocol-buffer](./terminology.md#protocol-buffer) interfaces,
these names are prefixed with "VT_" (e.g. VT_INT).

Sample: [types.sql](../../test4mvsql/test/types.sql).  

### STRING
A string constant in SQL is an arbitrary sequence of characters bounded by single quotes ('): 'This is a string'.   
To include a single-quote character within a string constant, write two adjacent single quotes, e.g., 'Dianne''s horse'.   

*Note*: a string which is enclosed in double-quote characters (") is an [identifier](#identifiers).  

#### Supported Encoding
mvStore supports the UTF-8 encoding exclusively. All string data should be converted to UTF-8 before being passed to mvStore.  

### BSTR(Binary String)
mvSQL supports hexadecimal values, written X'val' or x'val' (with explicit quotes), where val contains hexadecimal digits (0..9, A..F, a..f),
and is expected to contain an even number of digits (a leading 0 must be inserted manually for odd number of hexadecimal digits).  

<p style="color:red">
REVIEW (maxw): ?? why even number of digits ?? what if it's missing ??
</p>

### URL
Format: U'url_addr'  

### ENUM
Format: Not supported yet   

### Numeric Types
The numeric types in mvStore are closer to C/C++ numeric types.  

Numeric constants are accepted in these general forms:   

  digits [type-suffix]  
  digits[.digits][e[+-]digits] [type-suffix]  

where **digits** is _one or more_ decimal digit in ASCII (0 through 9) or Unicode (０through９).  
*Note*: There must be at least one digit before and after the decimal point (if one is used).  
*Note*: At least one digit must follow the exponent marker (e) (if one is present).  
*Note*: There cannot be any space or other character embedded in a numeric constant.  
*Note*: Any leading plus or minus sign is not actually considered part of the constant; it is an operator applied to the constant.  

<p id="typesuffix">
The **type-suffix** is an alphabetical character appended to the numeric constant, to specify its type. It can be used when user want to do some 
bitwise operation for this numberic constant, or user want to store it with specific data type format on disk. If it is not specified, then mvStore
will select a default representation matching the value; it may convert the number to the most space-efficient data type that can represent this value.  
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

Note that the suffix 'F' is not allowed, as it collides with the 'farad' [unit of measurement](#unit-of-measurement). 

#### DOUBLE
similar to FLOAT, but with higher precision; it is the default representation for real numbers  
range is [2.22507e-308, 1.79769e+308]  
[type-suffix](#typesuffix): none  

Note that numbers that have a [unit of measurement](#unit-of-measurement) suffix are automatically of this type.

#### BOOL
TRUE or FALSE  

### DATE/TIME Types  
Currently, mvSQL does not expose time zone control.  

#### DATETIME
Format: TIMESTAMP 'YYYY-MM-DD HH:MM:SS.XXXXXX', where the time and fractional second parts are optional  
range is ['1601-01-01 00:00:00.000001', '9999-12-31 23:59:59.999999']  

#### INTERVAL
Format: INTERVAL 'HHHHHHH:MM:SS.XXXXXX', the first number is hours, then minutes, seconds and (optional) fractional seconds part.  
range is: ???  
In the future, year-month-day will be supported as well.  

### EXPR (expression definition)
Format:  $(expression)  

EXPR is the compiled form of an EXPRTREE, which is mostly used internally by the database engine.
An EXPR can be stored as a [value](./terminology.md#value), but it is not evaluated automatically at INSERT/UPDATE statment execution time.
(the value of that property will always be the EXPR itself, never its evaluation).
However properties with type EXPR are evaluated automatically when they’re used in expressions. E.g.

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

Here prop2 is stored directly with the value of that expression executed at UPDATE execution time, while prop3 is stored in type EXPR, 
which is evaluated when query.  

It’s also possible to invoke such a property with parameters (up to 254). E.g.

  mvcommand>
  INSERT prop1=3, prop2=$(prop1-:0);
  PIN@0000000000050001(2):(<prop1|VT_INT>:3       <prop2|VT_EXPR>:$(prop1 - :0))
  1 PINs INSERTED.
  
  mvcommand>
  SELECT * WHERE prop2(1) = 2;
  PIN@0000000000050001(2):(<prop1|VT_INT>:3       <prop2|VT_EXPR>:$(prop1 - :0))
  1 PINs SELECTED.

Note that now mvstore can support ignoring param, i.e. user can pass more parameters than the number should be used in the expression, 
because there is no parameter description when define the expression value.
  
### EXPRTREE
This is an internal, transient type used primarily in C++, to build expression trees before they are compiled by mvStore into
expressions (EXPR).

### QUERY (query statement)
Format:  ${statement}  

QUERY is similar to EXPR, but for a whole statement.

### ARRAY/CNAVIGATOR ([Collection](./terminology.md#collection)) 
Format:   
1. (elem1,...,elemN) -- SQL standard style. *Note*: (0) is a int (the parentheses in this case are not interpreted as defining a set)  
2. {elem1,...,elemN} -- mvSQL extension. *Note*: {0} specifies a one-element collection  

Please refer to the [definition of 'collection'](./terminology.md#collection).  

  mvcommand> insert (prop2,prop3) values(123 ,{123, 'test', 120, 534});   
  PIN@327684(2):(<prop2|VT_INT>:123	<prop3|VT_ARRAY(4)>:{<0|VT_INT>:123, <1|VT_STRING>:test, <2|VT_INT>:120, <3|VT_INT>:534})
  1 PINs INSERTED. 
    
  mvcommand> SELECT * WHERE prop4[3] = 534;   
  WARNING: Full scan query: SELECT *  
  WHERE prop4 [ 3] = 534  
  PIN@327684(2):(<prop2|VT_INT>:123	<prop3|VT_ARRAY(4)>:{<0|VT_INT>:123, <1|VT_STRING>:test, <2|VT_INT>:120, <3|VT_INT>:534})
  1 PINs found.  
  
Internally, smaller collections are stored with a representation similar to an array (the type is ARRAY).
Larger collections are stored in the B-tree (the type becomes CNAVIGATOR), enabling enormous collections
with fast retrieval of known eids. The transition between those two states is relatively transparent, and applications
should not assume that a collection will be stored as an ARRAY.  

The transition between a scalar value and a collection is also designed to be relatively transparent
(with a core query syntax that applies to both cases indifferently).
For more information about collections, see [comparison between collections](#comparison-between-collections),
[value in collection](#value-in-collection) and [UPDATE ADD/SET](#update).  

*Note*: although mvStore doesn't support nested collections, it is possible to implement similar functionality by combining multiple properties or PINs, by adding a collection reference to a collection.   
 
### Range
Format: [number1, number2]   
it can be used with keywork IN. The meaning is the same as BETWEEN number1 AND number2.  
*Note*: * is used here to denote the infinity number.

Examples: [between.sql](../../test4mvsql/test/between.sql). 

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

<p style="color:red">
TODO (maxw): TBD
</p>

### STREAM

<p style="color:red">
TODO (maxw): TBD
</p>

Unit of Measurement
--------------------
mvStore allows to attach [units](./terminology.md#unit-of-measurement) to [double](#double)-precision floating point numbers, 
to enhance the self-descriptiveness of data, and interoperability. mvStore automatically converts values between different units 
when performing computations on compatible types.

*Note*:  In mvSQL, integer with unit suffix will be converted to double/float automatically. Because in mvStore, only float/double 
value can support unit suffix. The design reason is the unit conversion which may lead to float/double result even we input integer.
E.g. 1 inch = 0.0254 meter, and even user input 1 inch and 1 meter, then the sum() result is: 1 inch and 1 meter = 1.0254 meter, which
can not be stored as a integer. 

The syntax simply requires to append the chosen suffix to a literal value (wherever a value is legal). Note that suffixes
are case-sensitive, and unit suffixes can not be used together with [type-suffix](#typesuffix). 

Sample: [units.sql](../../test4mvsql/test/units.sql)

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
 
Sample: [functions.sql](../../test4mvsql/test/functions.sql) and [operator.sql](../../test4mvsql/test/parse_operator.sql).

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
expr IN list                return whether or not the val is equal to one value of the list. 

These binary comparison operators can not only support single value right operants, but also a list of values with [ANY/SOME/ALL qualifier](#anysomeall-qualifier). 
The List can be a collection, or a list of values returned by sub-query. 

#### comparison between collections  
1. value = collection 	-- same as  "value IN collection"    
2. collection1 in collection2  -- for each element in collection1, check {the element's value IN collection2}  

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
These functions can also support [DISTINCT/ALL qualifier](#distinctall-qualifier) to indicate we should calculate the duplicate value in the expression or not, e.g. AVG(DISTINCT expression).

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

Sample: [full_text_search.sql](../../test4mvsql/test/full_text_search.sql).  

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

Sample: [exists.sql](../../test4mvsql/test/exists.sql)

### ANY/SOME/ALL qualifier
These qualifiers can only be used as right operant of the binary comparison operators. E.g.

Sample                   Description    
------                   -----------
val < ANY (list)         return true if val< any element of the list, otherwise return false.
val < SOME(list)         some as "val < ANY (list)"
val < ALL (list)         return true if val< all element of the list, otherwise return false.

Sample: [collection_operators.sql](../../test4mvsql/test/collection_operators.sql)

### DISTINCT/ALL qualifier

Operator                         Description
--------                         -----------
DISTINCT list                    return the list of values after eliminating the duplicate values
ALL list                         return the list of value without eliminating the duplicate.

There some 3 usage for these qualifier:

  - SELECT item. E.g. SELECT DISTINCT prop1 FROM class1.
  - Aggreation functions parameters. E.g. AVG( DISTINCT {1.0, 2.0})
  - list of values returned by subquery which is used as operants of set operators. e.g. query1 UNION DISTINCT(prop1,prop2) query2.
  
  
ISLOCAL

<p style="color:red">
REVIEW (maxw): obscure...
</p>

### Collection Functions and Operators

Function/Operator      Expression Sample              Description
-----------------      -----------------              -----------
[ ]                    property[position]             Fetch the value at the specified position in the collection. position can be a number (starts at 0) or one of these values: LAST_ELEMENT, FIRST_ELEMENT, SOME_ELEMENT, ALL_ELEMENTS.
COUNT                  COUNT(collection)              Return the cardinality of that collection.
IN                     val IN collection              Return whether or not the val is equal to one value of the collection. 
IN                     collection1 IN collection2     Return whether or not all values of collection1 are IN collection2.   


#### value in collection
value1 IN value2 is interpreted by mvSQL to mean "is value1 part of the collection value2?". In contrast, this would be considered an error in MySQL.  

### Reference and Dereference Operators
Reference operator: &  
Dereference operator: *  

*Note*: & has 2 meanings: "bitwise AND" and "dereference"; it depends on the context where it is used.   

A few examples (here X is a hexadecimal digit, XXXXXXXXXXXXXXXX is a PID):

Expression                            Meanning
----------                            --------
@XXXXXXXXXXXXXXXX                     Return the PIN reference.
*@XXXXXXXXXXXXXXXX                    Return the value of this pin, which is the value of the special mv:value property in this PIN (this values can be set; it can be an EXPR). 
@XXXXXXXXXXXXXXXX.prop                Return the value of prop in pin @XXXXXXXXXXXXXXXX.  
&@XXXXXXXXXXXXXXXX.prop               Return the reference to the prop in pin @XXXXXXXXXXXXXXXX.  
@XXXXXXXXXXXXXXXX.prop[0]             Return the element value of the prop in pin @XXXXXXXXXXXXXXXX.  
&@XXXXXXXXXXXXXXXX.prop[0]            Return the element reference of the prop in pin @XXXXXXXXXXXXXXXX.  

Additional examples: [reference.sql](../../test4mvsql/test/reference.sql).  

  
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
IS, IS NOT            left                IS TRUE, IS FALSE, IS UNKNOWN, IS NULL, IS A
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
In this section we describe the mvSQL BNF. Here are the display conventions used:

Expression                Meanings
----------                --------
UPPERCASE                 KEYWORD 
lowcase                   terminal or non-terminal fragment of statement 
[ ]                       optional fragment 
{A|B}                     choose fragment A or B 
...                       repeat the previous statement fragment type 

### Store management statement
Synopsis: 

		- CREATE STORE [IN 'directory'] [OPTIONS(...)], where options have format: NAME=value[,NAME=value..]
		- DROP STORE [IN 'directory']
		- MOVE STORE [FROM 'source directory'] TO 'destination directory'
		- OPEN STORE [IN 'directory'] [OPTIONS(...)]
		- CLOSE STORE

If 'directory' is not specified, mvstore assumes the "current directory" (platform dependent).
*Note*: The API for these statments(call manageStores(...)) is different from the API for other statments(ISession.createStmt(...)), because these statements can be executed before db connection established. 

List of option names (case insensitive):
a) for OPEN STORE and CREATE STORE:
        - NBUFFERS=number
        - LOGBUFSIZE=number
        - MAXFILES=number
        - SHUTDOWNASYNCTIMEOUT=number
        - PASSWORD='string'
        - LOGDIRECTORY='directory' (mapped using call to IMapDir::map(SO_LOG...) if provided)
b) for CREATE STORE only:
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
Here's a description of mvSQL's Data Definition Language.

#### CREATE CLASS
Synopsis:  

		CREATE CLASS class_name [OPTIONS( {VIEW|CLUSTERED|SOFT_DELETE} )] AS query_statement.

where the query_statement is a [SELECT QUERY](#query). Here's a description of the OPTIONS:  
1. DEFAULT: This is the default mode (all [PIDs](./terminology.md#pin-id-pid) will be indexed by this class). 
2. VIEW: Like view in relational db, it is just a query definition for usability.
3. CLUSTERED: Using clustered index to maintain all [PIDs](./terminology.md#pin-id-pid), for increased performance. Not yet supported.  
4. SOFT_DELETE: Not only create a index for normal pins, but also create another index for those pins which is marked in deleted status(Deleted PINs are not permanently deleted except that delete with option MODE_DELETED in C++ API or PURGE), and can be restored using mvSQL "UNDELETE". ).

Examples: [class.sql](../../test4mvsql/test/class.sql).   

#### Create [class family](./terminology.md#family)  

  CREATE CLASS clsfml11 AS select * where prop1 = :0 and prop2 = :1;    
  select * from clsfml11(*, 2);    

Here * indicates all values, including NULL. In this case, the [index](./terminology.md#index) is created with the composite key(prop1 and prop2)  
**Limitation 1**: Because kernel use BTree for index, we can't store a PIN whose properties is all NULL value. 
So NULL can be passed as a parameter to class family only when the index for this class family is a multi-segment index; Single property index cannot support NULL parameters.
For performance consideration, it is not suggested to create a class family with only one parameters which passed to where clause as: WHERE :0 is NULL.

**Limitation 2**: Now mvStore has a syntax restriction about parameter position in predicates. E.g. mvStore can not create index for ":0 = value", 
please using "value = :0" instead.

*Note*: now mvstore can support ignoring param, i.e. user can pass more parameters than the number should be used in the query, 
because there is no parameter description when define the class family.

Please refer to the [class](./terminology.md#class), [family](./terminology.md#family) and [indexing](./terminology.md#index) descriptions for
a brief comparison with the relational DDL. Note that it is possible to declare multiple families with the same predicate, but different
type specifications:

  CREATE CLASS clsfml21 AS select * where prop1 = :0(int);  
  CREATE CLASS clsfml22 AS select * where prop1 = :0(String); 

In this case, if a PIN's prop1 is a string which cannot be converted into a number, then it won't be part of clsfml21.
Note that if prop1 has a float value, then the float value will be truncated and converted into int before it's inserted as index key value.

If the parameter type is not specified, then class family index is created with the date type of the first PIN to match this class family.  
And all class options work for class family except that SOFT_DELETE. 

##### Indexing of collections 
For single-property indexes, all elements will be added to the index.  
For multi-segment indexes, all combinations will be added to the index (Cartesian product of all values of the indexed properties).  

##### How to specify key value order for index
The available options are:  
1. ASC:  Store key value in ascendent order.  
2. DESC: Store key value in decendent order.  
3. NULLS FIRST: Order the null value(i.e. there is no such a property) before any non-null value.  
4. NULLS LAST: Order the null value(i.e. there is no such a property) after any non-null value.  

		CREATE CLASS clsfml5 AS select * where prop1 = :0(int, desc, nulls first)and prop2=:1(int);  

### DML
Here is a description of mvSQL's Data Manipulation Language.

#### INSERT
Synopsis:  

  - INSERT (property [, ...]) VALUES ( expression [, ...] ) [, ...]   
  - INSERT property = expression [, ...]  
  - INSERT SELECT ...  

Examples: [insert.sql](../../test4mvsql/test/insert.sql).

Notes:  
1. mvSQL does not yet support the insertion of graphs of inter-connected pins.  
2. mvSQL does not yet support multiple pin insertion as suggested by the [, ...] in the first line of the synopsis.  
3. mvSQL does not yet support the third line of the synopsis.  

#### UPDATE
Synopsis:  

		UPDATE [{pin_reference|class_name| class_family_name({expression_as_param| *| NULL}, ...)}] actions [WHERE conditions]  

where *actions* can be:  

  - {SET|ADD} property = expression [, ...]  
  - DELETE property [, ...]   
  - RENAME property = new_property [, ...]  
  - MOVE collection_property[element_id] {BEFORE|AFTER|TO} {element_id|LAST_ELEMENT|FIRST_ELEMENT}  
  - EDIT ...  

and *pin_reference* can be:
  
  - a pin reference with format: @PID. E.g. @D001.
  - a collection of pin references with format: { @PID[, ...] }. E.g. {@D001, @D002}.

and *expression_as_param* can be any [expression](#value-expressions).  

Examples: [update.sql](../../test4mvsql/test/update.sql).  

Notes:  
1. UPDATE {SET|ADD} a non-existing property: add a property   
2. UPDATE SET an existing property: change the value of that property (if the property is a collection, overwrite the whole collection)   
3. UPDATE ADD an existing property: append a new value to that property (if the property only has one value, then change the type to collection, and append the new value)  

#### DELETE/UNDELETE/PURGE   
Synopsis:  

  {DELETE|UNDELETE|PURGE} 
  [FROM {pin_reference|class_name| class_family_name({expression_as_param| *| NULL}, ...)}] 
  [WHERE conditions]

DELETE:    Mark PINs in deleted status(soft delete).
UNDELETE:  Change from deleted status to normal active status.
PURGE:     Remove(permanently delete) PINs from the physical disk. It can not remove the PINs in deleted status.
 
Examples: [delete.sql](../../test4mvsql/test/delete.sql).  

### QUERY

Synopsis: 

  SELECT [ * ]  
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
When an alias is provided, it completely hides the actual name of the class or family; for example given FROM foo AS f, the remainder of the SELECT must refer to this FROM item as f not foo.

#### Order by
Examples: [orderBy.sql](../../test4mvsql/test/orderBy.sql).   

ORDER BY must appear after ALL the unions.  
ORDER BY is considered to apply to the whole UNION result (it's effectively got lower binding priority than the UNION).  
To order a subquery result, use parentheses around the subquery.  

*Note*:
1. In order to include null value for ordered property, NULLS FRIST/LAST should be added to order by clause. 
2. The default behavior is order by ASC without NULL value PINs.

#### Group by
Examples: [groupBy.sql](../../test4mvsql/test/groupBy.sql).   

#### Set operator: UNION | INTERSECT | EXCEPT
Examples: [set_operator.sql](../../test4mvsql/test/set_operator.sql).   

The functionality of all these set operators is similar to standard SQL, 
except that mvStore does not require that all operands have same property number or type. 
Duplicates are identified based on [PIN ID](./terminology.md#pin-id-pid) instead of property value, which is differnt from standard SQL.

The keyword DISTINCT/ALL can be used to specify the result should eliminate duplicates or not.

<p style="color:red">
<Ming> I think it is better to implement as below logic:  
distinct(property list)  -- will eliminate duplicate which is basing on the property list, not the PID. 
Moreover distinct(mv:pinID) can works as previous implemtation.
</p>

#### Join
mvStore returns immutable PIN collections as query results.  Presently, the join results are somewhat limited
(they only contain PINs from the left-hand class).

		SELECT * FROM class1 as c1 join class1 as c2 on (c1.prop1 = c2.prop2);

mvStore supports every kind of JOIN (LEFT/RIGHT/FULL/CROSS JOIN), except the Natural JOIN.

Examples: [join.sql](../../test4mvsql/test/join.sql).   

#### Sub query in FROM clause
A sub-SELECT can appear in the FROM clause. This acts as though its output were created as a temporary table for the duration of this single SELECT command. 
Note that the sub-SELECT must be surrounded by parentheses, and an alias must be provided for it. 

### Inheritence
Being different from relational DB, mvStore support a PIN which can be belongs to multiple classes, in this way user can implement some inheritant data.

Examples: [inheritance.sql](../../test4mvsql/test/inheritance.sql). 

#### How to query a PIN which belongs to 2 classes

There are 2 ways:  

  - Using built-in property mv:pinID in WHERE CLAUSE, e.g. SELECT * WHERE class1.mv:pinID=class2.mv:pinID.
  - Using operator & for class names in FROM CLAUSE, e.g.  SELECT * FROM class1 & class2.


### TRANSACTIONS
mvStore not only supports basic transactions, but also sub-transactions.
The session holds a transaction stack.  Every sub-transaction can be rolled back independently (without affecting the state of the whole transaction).
Changes are committed to the database only when the outermost transaction in the stack is committed.  

Examples: [transaction_basic.sql](../../test4mvsql/test/transaction_basic.sql).  

#### Start a Transaction
START TRANSACTION is used to start a transaction/sub-transaction block.

Synopsis: 

		START TRANSACTION [ transaction_mode [, ...] ]

where transaction_mode is one of:  
 
  - ISOLATION LEVEL { READ UNCOMMITTED | READ COMMITTED | REPEATABLE READ  | SERIALIZABLE }   
  - READ ONLY |READ WRITE  

Examples:  
[transaction_isolation.sql](../../test4mvsql/test/transaction_isolation.sql),     
[transaction_readonly.sql](../../test4mvsql/test/transaction_readonly.sql),
[transaction_sub.sql](../../test4mvsql/test/transaction_sub.sql).   

Note:     
1. mvStore doesn't support isolation level READ UNCOMMITTED.  
2. When READ ONLY is specified, no operation in this transaction must write, otherwise the transaction will fail.  
3. When READ ONLY is specified, mvStore uses the Read-Only Multi-Version Concurrency Control (ROMV), which will not block (or be blocked by) any read/write transaction.  

#### End a Transaction
##### COMMIT
Synopsis: 

		COMMIT [ALL]; 

If ALL is specified, then mvStore will commit the whole stack of transactions (started in the current session), otherwise it only commits the innermost transaction/sub-transaction block in the stack.    

##### ROLLBACK
Synopsis: 

		ROLLBACK [ALL];  
    
If ALL is specified, then mvStore will rollback the whole stack of transactions (started in the current session), otherwise it only rolls back the innermost transaction/sub-transaction block in the stack.    

<p style="color:red">
REVIEW (maxw): distinguish the mvcommand keywords visually, somehow  
REVIEW (maxw): I don't see anything about class inheritance (/pin[pin is ... and ...) - ah yes, there is test/inheritance.sql... must refer to it  - fixed  
REVIEW (maxw): why isn't JOIN part of the BNF for SELECT? - fixed  
REVIEW (maxw): I don't see any formal description of AS in cases like SELECT * FROM class2 as c2 WHERE 534 in c2.prop3;   - fixed  
REVIEW (maxw): no mention of DISTINCT keyword limitations, and actual model for distinct stuff, listValues etc. (n.b. incomplete right now)  - partial fixed.  
REVIEW (maxw): no mention of COUNT, LIMIT/OFFSET philosophy; also, mention @1234.prop syntax for counting collections  
REVIEW (maxw): actually, have a section just on counting things  
REVIEW (maxw): a section on path expressions for declarative traversal of collections (by query)  
REVIEW (maxw): clarify the meaning of {} in SELECT * FROM {@1234}; (vs absence of {} in SELECT * FROM @1234.users) - fixed  
REVIEW (maxw): clarify all the possible elisions/tricks when using families (e.g. with range var), vs possible parameters and meanings  
REVIEW (maxw): idioms (broader disc with J)  
</p>

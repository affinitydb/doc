## NAME

affinityd - embedded web server for CGI access to the Affinity db

## SYNOPSIS

`affinityd` [ <options>... ]

## DESCRIPTION

affinityd is an embedded web server which provides CGI access to the
Affinity store.  It also includes a minimal simple static web server
for its own internal purposes to serve basic web admin CGIs & ui.

(All CGIs are builtin, there is intentionally no support for user defined
CGIs.)

## USAGE NOTES

Affinity natively supports two query languages pathSQL and protobuf, plus a
native C++ api.  pathSQL is a SQL dialect.  protobuf is query/response
serialization defined with google protobuf.  The store server supports both
pathSQL and protobuf.

With pathSQL queries, the result is sent in JSON encoding by default.  (But
you can alternatively request protobuf encoded results.)

With protobuf encoded queries, the result is sent in protobuf by
default.  (At present the Affinity server does not support JSON encoded
results for protobuf encoded requests.)

Affinity supports both HTTP GET and HTTP POST CGIs and parameters.  With HTTP
GET the arguments must be URL encoded, and with HTTP POST both binary and
urlencoded parameters are supported.  The POST handling also supports
urlencoded url parameters (which is needed to avoid a bootstrap problem in
specifying the encoding of POST parameters).  

## OPTIONS

The flags that are supported by affinityd are as follows:

    `-d dir` document root for the web server.  Also the store file is
    read from this directory.  The docroot can also be specified using
    the DOCROOT environment variable.  The environment variable
    overrides the affinityd -d argument if both are present.  (Note: if
    affinityd is executed via afyEngine and the afyDaemon dll/so/dylib, the
    DOCROOT environment variable is the only way to set the document
    root).

    `-h` print usage help and exit.

    `-p port` web server port to listen on.  By default port 4560 is
    used.

    `-v` request more verbose logging, for debugging and increased
    visibility

    `-V` print software version and exit.

## HTTP GET support

The http arguments must be urlencoded and provided on the URL.  (The CGI web
standard is that multiple arguments are separated by &, and arguments are
separated from their value by =.  And argument values are urlencoded to
escape special characters.)

The built-in GET/POST CGI is named `/db`

Supported arguments are:

    `query=string` the pathSQL text query (only pathSQL query language is
    supported in GET, see HTTP POST below for support for protobuf
    encoded queries).

    The maximum HTTP header supported is 16KB, so the query + all HTTP
    headers must be less than this.  HTTP GET requests which are
    larger are rejected with an HTTP code 413 (Request Entity too
    Large) response code.

    `input=pathsql` if not specified, default is pathsql, so specifying
    the query language is redundant.

    `output=json|proto` default if not specified is JSON.  Protobuf
    encoded output is also supported.

    `type=count|plan|display|query` default if not specified is query.
    The type options mean briefly `query` executes the query, `count`
    instead counts the number of query result PINs, `plan` prints
    information about the query execution approach, `display`
    decompiles the query optimized query.

    `limit=<results>` if not specified the entire query result
    (unlimited) is displayed.  If given a maximum of <results> result
    PINs will be displayed.  To obtain the next result set `offset`
    (see below) maybe used.

    `offset=<start>` if not specified the result starts at result PIN
    1.  Starts the query result display from result PIN identified by
    <start>.

    `p<n>=<value>` query parameters.  Queries can include query
    parameters which are labeled ":<n>" in the pathSQL.  The
    corresponding value can be instantiated via the `p<n>` parameter.
    For example query parameter 1 ":1" can be instantiated with value
    "hello" with p1=hello.

## HTTP POST support

For POST either binary encoding or url-encoding is used.

URL-encoding is compatible with HTML forms (it is the encoding used by
browsers), but is currently limited to 1MB requests, whereas binary
encoding is not HTML form compatible but allows protobuf requests to
be streamed (and so to be of arbitrary size).

The default (and only currently supported) response format for
POST (request protobuf encoded) queries is protobuf encoding.

## URL-encoded POST

The HTTP POST request size maximum is 1MB.  Larger requests are rejected
with an HTTP code 413 (Request Entity too Large) response code.

The entire request is URL-encoded and the mime-type of the HTTP POST
must be application/x-www-form-urlencoded.  (This is default and
automatic for static HTML forms).

Other URL arguments can be specified as part of the html form itself
(or optionally via the CGI arguments to the POST URL).  The example
HTML form post.html shows an example of this.

## binary encoded POST

With binary-encoded POSTs there is only one POST argument which is the
unnamed protobuf encoded query.  The POST can also take normal
url-encoded arguments on the URL path as with GET requests.

All arguments other than the protobuf encoded query must be passed on
the URL line.

The mime-type for HTTP POST must be application/octet-stream.  The
Content-Length field is optional so a stream can be sent without knowning
its length a-priori.

## Static web server

Mime-types supported are html (.html/.htm), javascript (.js), icon
(.ico), GIF (.gif), JPEG (.jpg/.jpeg), PNG (.png), JSON (.json), CSS
(.css) and binary (.bin) the default for unhandled types is the same
as binary (application/octet-stream).

The document-root is specified via the `-d dir` argument documented above.

One default file is shipped which is the `favicon.ico` as graphical web
browsers commonly request this file to use as a site icon.

## HTTP features

HTTP keep-alive is supported.

## FILES

    `affinity.store` and `afy*.txlog`, in a sub-directory of the document-root,
    named after the basic-auth user connecting with the server
    (the default sub-directory name is `test` if no basic-auth header
    was specified).

## AUTHOR

Copyright GoPivotal <affinity-ng-privacy@gopivotal.com>

## SEE ALSO

libaffinity(7), http://affinityng.org/

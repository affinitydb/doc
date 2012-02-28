#Getting Started with Affinity

##Setup
The Affinity source code is hosted on github, from where it is released as a series of
open-source projects. With a properly configured personal github account,
just do:

      curl -s -k -B https://raw.github.com/affinitydb/setup/master/linux/setup.sh > affinity_setup.sh
      bash affinity_setup.sh

This will install and build the kernel, server, doc, client libraries etc., all from source files.

This procedure should work on linux and OSX.
A few confirmations will be requested during installation.

Presently, no automatic setup is provided for Windows or ARM-based devices.
These will be provided in a later release. In the meantime, it's possible to
clone, build and run all projects manually.

##Simple Access
The database [server](./terminology.md#server) process is called `affinityd`
and listens to HTTP requests on port `4560` by default. For more details on how to run
and parametrize `affinityd`, please refer to the [server](./Affinity server.md) page,
or run `affinityd -h`.

The server exposes a javascript online console at the root (e.g. `http://localhost:4560/`), 
which allows to navigate the contents of the store and modify data (same as what you find
[online](http://affinity.cloudfoundry.com)). Just open that URL
in a browser. The console can also help learning pathSQL.

##Quick pathSQL Guide
Please find a quick guide [here](./pathSQL primer.md).

##Binary Components
For an overview of the software components involved, please read this [page](./terminology.md#software-components).
Here's a short table summarizing the parts involved.  

File                             Description
---------------------------      -----------
affinity.dll / libaffinity.so    The Affinity [kernel](./terminology.md#kernel) library
affinityd[.exe]                  The database [server](./terminology.md#server)
server/src/www                   The server's online console
affinity-client.js               The client library for [node.js](./javascript.md)
affinity.py                      The client library for [python](./sources/affinity_py.html)

##Runtime Files
For each distinct store created by `affinityd`, one file named `affinity.db` will be created. This is the data file.
Additionally, any number of files following the pattern `afy*.txlog` may be created, containing transactional
logs for database logging & recovery. Upon a checkpoint or a clean shutdown, the `afy*.txlog` files are automatically deleted.

By default, `affinityd` puts those files in the parent folder of the docroot directory specified with the `-d` argument.

## Links to MSVCP100 DLL (Windows)
Microsoft redistributable libraries can be retrieved here.  Make sure that the version you obtain is compatible with Affinity binaries.  
[win64: MSVCP100.dll](http://www.microsoft.com/downloads/en/confirmation.aspx?FamilyID=bd512d9e-43c8-4655-81bf-9350143d5867)  
[win32: MSVCP100.dll](http://www.microsoft.com/downloads/en/details.aspx?displaylang=en&FamilyID=a7b7a05e-6de6-4d3a-a423-37bf0912db84#AffinityDownloads)  

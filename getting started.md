#Getting Started with ChaosDB

##Setup
ChaosDB is hosted on github, from where it will be released as a series of
open-source projects. Github requires these preliminary steps:

1. create a personal (free) user account in github (visit https://github.com/)
2. setup a ssh keypair (uploading the public key to that github account)

ChaosDB is not yet open to the public. For now, it resides in private projects.
Until ChaosDB becomes open-source, the procedure to install from github
will involve the following steps (on linux):

3. send your account's user name to maxw@vmware.com, to become a private collaborator
4. git clone git@github.com:ChaosDB/setup.git
5. bash ./setup/linux/setup.sh

This will install the kernel, server, nodejs, doc and other components of the release,
and start the database server.

<p style="color:red">
_Note: When ChaosDB becomes open-source, the procedure will be further simplified:
steps 3-5 will be replaced with a single step involving a publicly accessible setup script._  
_Note: A similar setup procedure for Windows is planned but not yet available._  
</p>

##Simple Access
The database [server](./terminology.md#server) process is called `chaosdbd`
and listens to HTTP requests on port `4560` by default. For more details on how to run
and parametrize `chaosdbd`, please refer to the [server](./ChaosDB server.md) page,
or run `chaosdbd -h`.

The server exposes a javascript online console at the root (e.g. `http://localhost:4560/`), 
which allows to navigate the contents of the store and modify data (same as what you find
[online](http://ChaosDB.cloudfoundry.com)). Just open that URL
in a browser. The console can also facilitate learning pathSQL.

##Quick pathSQL Guide
Please find a quick guide [here](./pathSQL primer.md).

##Binary Components
For an overview of the software components involved, please read this [page](./terminology.md#software-components).
Here's a short table summarizing the parts involved.  

File                             Description
---------------------------      -----------
chaosdb.dll / libchaosdb.so      The [ChaosDB kernel library](./terminology.md#chaosdb)
chaosdbd[.exe]                   The database [server](./terminology.md#server)
server/src/www                   The server's online console
chaosdb-client.js                The client library for [node.js](./ChaosDB js.md)
kscommand[.exe]                  (optional) A command-line app to interact with the db
ksclient.dll / libksclient.so    (optional) The http client library that kscommand uses to talk to the db
msvcp100.dll (windows only)      If not already present on your machine, it can be obtained [here](#links-to-msvcp100-dll)

##Runtime Files
For each distinct store created by `chaosdbd`, one file named `ks.store` will be created. This is the data file.
Additionally, any number of files following the pattern `ks*.txlog` may be created, containing transactional
logs for database logging & recovery. Upon a checkpoint or a clean shutdown, the `ks*.txlog` files are automatically deleted.

By default, `chaosdbd` puts those files in the parent folder of the docroot directory specified with the `-d` argument.

## Links to MSVCP100 DLL (windows)
Microsoft redistributable libraries can be retrieved here.  Make sure that the version you obtain is compatible with ChaosDB binaries.  
[win64: MSVCP100.dll](http://www.microsoft.com/downloads/en/confirmation.aspx?FamilyID=bd512d9e-43c8-4655-81bf-9350143d5867)  
[win32: MSVCP100.dll](http://www.microsoft.com/downloads/en/details.aspx?displaylang=en&FamilyID=a7b7a05e-6de6-4d3a-a423-37bf0912db84#AffinityDownloads)  

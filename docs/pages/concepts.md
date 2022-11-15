# Core Concepts

Launchbox provides a platform for running one or more **services**,
each of which may have multiple tenant **sites** that belong to it.
Services can provide **resources** to their sites (such as databases, caches, or object storage)
and utilize **plugins** to provide shared infrastructure to them.
Launchbox also has a built-in **Management Dashboard**,
a web app that provides a UI for managing sites and services. 

Let's look at each of these in some more detail.


## Services

Services are the heart of Launchbox.
In concrete terms, a service is any Git repository that provides a website –
whether that's a collection of static files or a database-backed application –
that Launchbox can clone and use to spin up a website.
Turning an existing repository into a Launchbox service can be as simple as
adding a `launch.yaml` file that tells Launchbox how to configure and run the service.

When a service is deployed for the first time or a new deployment is triggered to update the service code,
Launchbox will look at `launch.yaml` and do two things:
(1) set up any resources its sites may need, and
(2) run any necessary commands specified in the `setup` phase, such as migrating database schemas.

Services can be used to create _one or more_ sites that Launchbox will serve.
In cases where a service requires a database or other resources,
the application code will also need to be modified to
use a different database for each site that uses the service.

For more details, [see the Services page](../features/services/).


## Sites

A site is a single instance of a service, available at a unique hostname.
It may be the _only_ instance of a service (for example, a static documentation page),
or it may be one of hundreds (for example, an internal department site backed by a CMS).

Sites are created and managed on the Management Dashboard, where you can choose a service to use,
assign a hostname, and more, depending on what kind of service it uses.


## Resources

A Launchbox service's `launch.yaml` file can be configured
to create resources for each site that uses the service.
The three kinds of resources offered are:

- **Databases** (currently supporting PostgreSQL)
- **Caches** (currently supporting Redis)
- **Storage** (currently supporting Amazon S3, or services that follow S3 API)

For more details, [see the Resources page](../features/resources/).


## Plugins

Launchbox operators can install plugins to help services and sites integrate
with providers of things like identity, authentication, and SSL certificates.
For example, at JPL we have closed-source plugins that connect Launchbox to
our LDAP directory, SAML single-sign-on service, and internal SSL certificate generator.

For more details, [see the Plugins page](features/plugins/).


## The Management Dashboard

Running locally on <http://launchbox.run:8080>, this dashboard is where you can add and manage services, sites, and plugins.

_(insert image of dashboard homepage)_

_Additional description TK_

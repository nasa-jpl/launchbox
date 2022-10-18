# Services

Services are the heart of Launchbox.
In concrete terms, a service is any Git repository that provides a website –
whether that's a collection of static files or a database-backed application –
that Launchbox can clone and use to spin up a website.

Turning an existing repository into a Launchbox service can be as simple as
adding a `launch.yaml` file that tells Launchbox how to configure and run the service.

In the simplest case – a static site with no build process and the index.html file at the root of the repository –
here's what a minimal `launch.yaml` would look like:

```yaml
routes:
  site:
    route: /
    type: static
```

A dynamic, database-backed application would have a more extensive `launch.yaml`,
like this example that configures [the Wagtail Bakery demo site](https://github.com/wagtail/bakerydemo):

```yaml
env:
  base:
    DEBUG: true
    UWSGI_WSGI_FILE: bakerydemo/wsgi.py
    DJANGO_SETTINGS_MODULE: bakerydemo.settings.local
  # specific environments (augments/overrides base)
  production:
    DEBUG: false
resources:
  database:
    type: postgres
  cache:
    type: redis
  storage:
    type: s3
phases:
  setup:
    - pip3 install -r requirements/production.txt
    - cp bakerydemo/settings/local.py.example bakerydemo/settings/local.py
    - echo "DJANGO_SETTINGS_MODULE=bakerydemo.settings.local" > .env
  tenant:
    - python3 manage.py migrate --noinput
routes:
  site:
    route: /
    type: wsgi
    options:
      path: bakerydemo/wsgi.py
      var: application
```

> Q FOR THE GROUP: phases.setup is the only thing that happens on service deployment, right? Everything else happens on site deployment? Given that, would it make any sense to pull out `setup` and `tenant` to the top level, and move `setup` to the top of the file, to better mirror the order of operations?

## `launch.yaml` spec

> Q FOR THE GROUP: This is a "narrative" sort of spec. Should we have something more formalized?

### `env`

Creates environment variables with the specified values for each of this service's sites.
The `base` grouping is required for variables that should exist in all Launchbox environments.
Additional groupings can be created that will trigger creation of other environment variables
(or redefinition of base environment variables) when Launchbox's environment matches the name of that grouping.

For example, given the `env` configuration:

```yaml
env:
  base:
    DEBUG: true
    UWSGI_WSGI_FILE: bakerydemo/wsgi.py
    DJANGO_SETTINGS_MODULE: bakerydemo.settings.local
  # specific environments (augments/overrides base)
  production:
    DEBUG: false
```

if the environment variable named `ENVIRONMENT` is set to `production` where Launchbox is running,
sites created for this service will have their `DEBUG` environment variables set to `false` instead of `true`.

### `resources`

Creates infrastructure resources for each of this services sites.

```yaml
resources:
  database1:
    type: postgres
  cache1:
    type: redis
  storage1:
    type: s3
```

Within the `resources` section, create objects with your identifier of choice
(like `database1` above) for each resource you need.
Each must have a `type` property that tells Launchbox what kind of resource to create.

The three kinds of resources offered are:

- **Databases** (currently supporting PostgreSQL)
- **Caches** (currently supporting Redis)
- **Storage** (currently supporting Amazon S3, or services that follow S3 API)

For more details on resource usage, [see the Resources page](../resources/).

### `phases`

The `phases` section is used to specify commands that should be run on service and site deployments.

```yaml
phases:
  setup:
    - pip3 install -r requirements/production.txt
    - cp bakerydemo/settings/local.py.example bakerydemo/settings/local.py
    - echo "DJANGO_SETTINGS_MODULE=bakerydemo.settings.local" > .env
  tenant:
    - python3 manage.py migrate --noinput
```

Commands given in the `setup` subsection will be run after a service repository is cloned
(both the first time and when it is updated), from that service's folder on the container filesystem.

Commands given in the `tenant` subsection will be run each time
one of this service's sites is deployed (or redeployed).

!!! tip
    Python services are automatically given their own virtual environment
    that both `setup` and `tenant` commands are run from, 
    so feel free to install whatever packages you require directly.

Both `setup` and `tenant` sections are not required; some services may only need one or the other. 

### `routes`

The `routes` section tells Launchbox how NGINX should route traffic to this service.
It is the only **required** section of the `launch.yaml` file.
Services can have multiple routes, if needed.

```yaml
routes:
  api:
    route: /
    type: wsgi
    options:
      path: app/api.py
      var: app
  pages:
    route: /pages/
    type: static
    options:
      path: pages
  assets:
    route: /static/data.json
    type: static
    options:
      path: static/data.json
```

Each child object of `routes` can be named with an identifier of your choice.
Within each, there are three required properties: `route` (the path under the hostname),
`type` (either `wsgi` or `static`), and `options`.

If `type` is `wsgi`, `options.path` should point to the Python module where the WSGI application is initialized
and `options.var` should be the variable that application is assigned to inside that module.

If `type` is `static`, `options.path` should point to the location (in the repository)
of the file/folder you want to serve (at the route given above).

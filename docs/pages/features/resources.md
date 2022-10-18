# Resources

A Launchbox service's `launch.yaml` file can be configured
to create resources for each site that uses the service.
You specify what resources your application requires and
configuration details will be provided to each site via environment variables.

The three kinds of resources offered are:

- **Databases** (currently supporting PostgreSQL)
- **Caches** (currently supporting Redis)
- **Storage** (currently supporting Amazon S3, or services that follow S3 API)


## Configuration

In your `launch.yaml` file, add a top-level `resources` object with a number of
resource objects that are named with an identifier of your choosing.
Each entry must have a `type` property, which can be either `postgres`, `redis`, or `s3`.
You can specify multiple resources of the same type, if needed.

### Example

```yaml
...
resources:
  database1:
    type: postgres
  database2:
    type: postgres
  cache1:
    type: redis
  storage1:
    type: s3
...
```

## Usage

When Launchbox encounters the `resources` object in the `launch.yaml` file of a service or site it's deploying,
it will create those services (or verify that they are already present)
and create the environment variables that are unique to each site.

Given the example configuration above, each site using this service would be given the following variables:

- Postgres databases:
    - `LB_database1_type`
    - `LB_database1_hostname`
    - `LB_database1_port`
    - `LB_database1_name`
    - `LB_database1_username`
    - `LB_database1_password`
    - `LB_database2_type`
    - `LB_database2_hostname`
    - `LB_database1_port`
    - `LB_database2_name`
    - `LB_database2_username`
    - `LB_database2_password`
- Redis cache:
    - `LB_cache1_type`
    - `LB_cache1_url`
    - `LB_cache1_prefix`
- S3 storage:
    - `LB_storage1_type`
    - `LB_storage1_bucket`

Service applications can then use these environment variables in their code
to ensure that each site can access its own individual resources.  

For example, a Django application would want to set its `DATABASES` setting like so:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("LB_database1_hostname"),
        "PORT": os.environ.get("LB_database1_port"),
        "NAME": os.environ.get("LB_database1_name"),
        "USER": os.environ.get("LB_database1_username"),
        "PASSWORD": os.environ.get("LB_database1_password"),
    },
}
```

!!! tip
    **Django users** – for even easier integration with Django,
    check out our [django-launchbox](https://github.com/nasa-jpl/django-launchbox) helper package!

### Additional notes

- For services where `postgresql` resources are configured,
  Launchbox will create a separate database for each site that uses the service.
- For services where `s3` resources are configured,
  Launchbox will create a separate bucket for each site that uses the service.

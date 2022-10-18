# Dashboard Routes

``` yaml title="Auth"
- /auth/login
- /auth/logout
```

``` yaml title="Home"
# Overview
- /
```

``` yaml title="API Spec"
# Display API spec
- /spec
```

``` yaml title="Deploys"
# List all deploys
- /deploys
```

``` yaml title="Services"
# List all services
- /services

# Add service
- /add/service

# View service
- /services/<service_id>
- /services/<service_id>/deploys
- /services/<service_id>/events
- /services/<service_id>/manage
```

``` yaml title="Settings"
# Basic settings
- /settings

# Plugins (Auth, Identity, etc)
- /settings/plugins
- /add/plugin

# Providers (connect Github, etc)
- /settings/providers
- /add/provider
```

``` yaml title="Sites"
# List all sites
- /sites

# Add site
- /add/site

# View site
- /sites/<site_id>
- /sites/<site_id>/events
- /sites/<site_id>/hostnames
- /sites/<site_id>/notes
- /sites/<site_id>/resources
- /sites/<site_id>/manage
```

``` yaml title="Status"
# View cluster status
- /status/overview
- /status/advanced
```

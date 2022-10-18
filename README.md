# Launchbox

Launchbox is a platform for rapid deployment of multitenant web products.
It currently supports Python-based webapps and static websites.

:warning: This is currently a **beta** product. **Do not use in production!**


## Use cases

Here are some examples of how Launchbox could be used:

- Add a CMS with a custom theme and let anyone in your organization create their own website from a shared codebase with no coding necessary
- As a local development environment, rapidly spin up local test sites with isolated databases
- Consolidated hosting of any number of static sites – like a self-hosted GitHub Pages kind of service


## Quickstart

```sh
git clone https://github.com/nasa-jpl/launchbox.git
cd launchbox
cp .env.dist .env
make start
make dashboard
```


## Documentation

[Visit our documentation website](https://nasa-jpl.github.io/launchbox/) for full details on installation and usage.


## Contributing

See the [contributing guide](CONTRIBUTING.md) for detailed instructions on how to contribute to Launchbox.

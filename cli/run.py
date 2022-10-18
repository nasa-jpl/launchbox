from .util import LBCLI

if __name__ == "__main__":
    # Prepare
    cli = LBCLI("Launchbox")
    cli.arg("status")
    cli.arg("create", "service", str)
    cli.arg("update", "service", "json", "Format: {service_id: {attr: value}}")
    # Parse
    if parsed := cli.parse():
        arg, value = parsed
        print(arg, value)
    else:
        cli.help()

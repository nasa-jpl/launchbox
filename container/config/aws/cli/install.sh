#!/bin/bash

function evlog() {
    echo "[aws.cli.install]: ${1}: ${2}"
}

# Check Arch
# ----------
if [ "${TARGETARCH}" = "arm64" ]; then
    evlog "Architecture" "Unsupported"
    exit 0
else
    evlog "Architecture" "Supported"
fi

# Work Dir
# --------
cd /tmp

# AWS CLI
# -------
evlog "Download" "CLI"
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip

evlog "Unzip" "CLI"
unzip awscliv2.zip

evlog "Install" "CLI"
./aws/install

evlog "Cleanup" "CLI"
rm -rf awscliv2.zip /aws

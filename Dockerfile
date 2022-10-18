FROM public.ecr.aws/lts/ubuntu:22.04

# Create: User
RUN useradd --create-home manager

# Working Directory
WORKDIR /usr/src/app

# Arguments
ARG DEBIAN_FRONTEND=noninteractive
ARG TARGETARCH

# Environment
ENV PYTHONUNBUFFERED=1

# --------

# Install: OS Dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    ca-certificates \
    build-essential \
    curl \
    dh-autoreconf \
    git \
    ldap-utils \
    less \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    libxmlsec1-dev \
    nginx \
    postgresql-client \
    python3-dev \
    python3-setuptools \
    python3-pip \
    python3-venv \
    pkg-config \
    rsync \
    sudo \
    tzdata \
    uwsgi-emperor \
    uwsgi-plugin-python3 \
    unzip \
    vim \
    xmlsec1 \
 && rm -rf /var/lib/apt/lists/*

# --------

# Install: Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
RUN apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# --------

# Setup: Timezone
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# --------

# Nginx
COPY container/nginx/files/nginx.conf /etc/nginx/nginx.conf

RUN chown -R manager:manager /etc/nginx && \
    chown -R manager:manager /var/lib/nginx && \
    chown -R manager:manager /var/log/nginx

RUN touch /run/nginx.pid && \
    chown -R manager:manager /run/nginx.pid

# --------

# Switch: User
USER manager

# --------

# Install: AWS Tools
COPY --chown=manager container/config/aws config/aws
RUN ./config/aws/cli/install.sh

# --------

# Copy: Configuration Files
COPY --chown=manager container/config config

# --------

# Install: Python Modules
RUN pip3 install -r config/python/requirements.txt --no-warn-script-location

# --------

# Copy: Application Files
COPY --chown=manager container .

# --------

# Run: Entrypoint
ENTRYPOINT ["/usr/src/app/docker/entrypoint.sh"]

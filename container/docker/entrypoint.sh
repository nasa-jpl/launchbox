#!/bin/bash

function evlog() {
    local activity="$1"
    shift;

    echo "* [entrypoint] $activity...";

    set +o errexit
    eval "$@"
    local result=$?
    set -o errexit

    if [[ $result -ne 0 ]]; then
        echo "* [entrypoint] $activity failed (exit $result)"
        return 1;
    fi

    echo "* [entrypoint] $activity succeeded (exit $result)"
    return 0;
}

function setupManager() {
    evlog "Cleaning up uWSGI socket files..." rm ./uwsgi/sockets/*.sock 2>/dev/null || true
    evlog "Cleaning up uWSGI start files..." rm ./uwsgi/stats/*.sock 2>/dev/null || true
    evlog "Bootstrap Postgres" python3 -m manage.bootstrap
    evlog "Restarting Nginx" service nginx restart
    evlog "Starting LB jobs backend" python3 -m manage.jobs &
    evlog "Sync: Reset" python3 -m sync.reset
    evlog "Sync: Run" python3 -m sync.run &
    evlog "Sync: Listen" python3 -m sync.listen.plugins &
    evlog "Sync: Listen" python3 -m sync.listen.sites &
    evlog "Watching Python files for changes" python3 -m manage.watch &
    evlog "Starting uWSGI Emperor mode" uwsgi --emperor ./uwsgi/vassals
}

set -o errexit
set -o pipefail
set -o nounset

setupManager

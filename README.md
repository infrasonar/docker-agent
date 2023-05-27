[![CI](https://github.com/infrasonar/docker-agent/workflows/CI/badge.svg)](https://github.com/infrasonar/docker-agent/actions)
[![Release Version](https://img.shields.io/github/release/infrasonar/docker-agent)](https://github.com/infrasonar/docker-agent/releases)

# InfraSonar Docker agent

Documentation: https://docs.infrasonar.com/collectors/agents/docker/

## Environment variables

Environment                 | Default                       | Description
----------------------------|-------------------------------|-------------------
`TOKEN`                     | _required_                    | Token to connect to.
`ASSET_ID`                  | `/data/.asset.json`           | Asset Id _or_ file where the Agent asset Id is stored _(must be a volume mount)_.
`API_URI`                   | https://api.infrasonar.com    | InfraSonar API.
`CHECK_CONTAINERS_INTERVAL` | `300`                         | Interval for the docker containers check in seconds.
`CHECK_IMAGES_INTERVAL`     | `300`                         | Interval for the docker images check in seconds.
`CHECK_SYSTEM_INTERVAL`     | `300`                         | Interval for the docker system check in seconds.
`VERIFY_SSL`                | `1`                           | Verify SSL certificate, 0 _(=disabled)_ or 1 _(=enabled)_.
`LOG_LEVEL`                 | `warning`                     | Log level _(error, warning, info, debug)_.
`LOG_COLORIZED`             | `0`                           | Log colorized, 0 _(=disabled)_ or 1 _(=enabled)_.
`LOG_FMT`                   | `%y%m...`                     | Default format is `%y%m%d %H:%M:%S`.



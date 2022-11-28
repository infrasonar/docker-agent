# InfraSonar Docker agent


## Environment variables

Environment                 | Default                       | Description
----------------------------|-------------------------------|-------------------
`TOKEN`                     | _required_                    | Token to connect to.
`ASSET_ID_FILE`             | `/data/.asset.json`           | File where the Agent asset Id is stored _(must be a volume mount)_.
`API_URI`                   | https://api.infrasonar.com    | InfraSonar API.
`CHECK_CONTAINERS_INTERVAL` | `300`                         | Interval for the docker containers check in seconds.
`CHECK_IMAGES_INTERVAL`     | `300`                         | Interval for the docker images check in seconds.
`CHECK_SYSTEM_INTERVAL`     | `300`                         | Interval for the docker system check in seconds.
`VERIFY_SSL`                | `1`                           | Verify SSL certificate, 0 _(=disabled)_ or 1 _(=enabled)_.
`LOG_LEVEL`                 | `warning`                     | Log level _(error, warning, info, debug)_.
`LOG_COLORIZED`             | `0`                           | Log colorized, 0 _(=disabled)_ or 1 _(=enabled)_.
`LOG_FMT`                   | `%y%m...`                     | Default format is `%y%m%d %H:%M:%S`.

My systemd user service for managing minecraft. I used with `screen` for years but now decided to ditch it in favor for RCON or ingame commands.

change directories and name accordingly.

```shell
mkdir -p ~/.config/systemd/user/
vim ~/.config/systemd/user/simplycreate.service

systemctl --user daemon-reload
systemctl --user start simplycreate.service
systemctl --user status simplycreate.service
```

```systemd
[Unit]
Description=SimplyCreate Server
Wants=network-online.target
After=network-online.target

[Service]
WorkingDirectory=/home/mcserver/SimplyCreate/
ExecStart=/home/mcserver/SimplyCreate/run.sh

# sent SIGINT instead for graceful shutdown
ExecStop=/bin/kill -s SIGINT -$MAINPID & /bin/kill -s SIGINT -$MAINPID

Restart=always
RestartSec=30

StandardInput=null

[Install]
WantedBy=multi-user.target
```
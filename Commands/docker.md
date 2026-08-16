<sup>
  Created @ 2026-08-13 / Updated @ 2026-08-13
</sup>

# Docker Compose commands set memo

because my memory sucks probably thanks to yearly 4hr avg sleep

all script snippet below assumes following:
- standard docker installation
- user is not added to docker group (like, root operation must be explicit, ffs)
- contains `-euo pipefail` even when unnecessary since that's better habit at least for me

<br>

---

## Generic

### Cleanup

```shell
docker system prune -a
```

<br>

### Compose update & clean

removes dangling orphan images

```sh
#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
sudo docker compose pull
sudo docker compose up -d
sudo docker image prune -f
```

<br>

---

## Services

### Update Portainer

```shell
#!/bin/bash

sudo docker stop portainer
sudo docker rm portainer
sudo docker pull portainer/portainer-ce:latest
sudo docker run -d -p 8000:8000 -p 9443:9443 --pull=always --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
```

<br>
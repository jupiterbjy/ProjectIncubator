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

## Generic

TODO

<br>
<br>

## Compose

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

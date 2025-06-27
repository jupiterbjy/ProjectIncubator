### Trio based Async FastAPI + MariaDB Upload server Demo

Demo code implementing simple and fast(hopefully) file upload API.

On Windows 11, i7-8550U with file size of 25,068,313 Bytes takes 1~1.3 sec response time.

### Requirements

- CPython 3.12+ (tested on CPython3.12)
- MariaDB 11.x

For python libraries, please refer [requirements.txt](requirements.txt)


### Usage

Fill out [db_conf.ini](db_conf.ini) and just run [server.py](server.py).

Send POST to `http://127.0.0.1/files` with multipart file attachment.

i.e.

```bash
curl -F "file=@test.jpg" http://127.0.0.1/files
```

On Successful POST server will generate md5 hash, and store file name, hash in database, while storing the image in `./uploaded`.

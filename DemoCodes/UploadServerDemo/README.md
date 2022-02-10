### FastAPI + Trio File receiving Demo

Demo code implementing simple and fast(hopefully) file upload API.

On Windows 11, i7-8550U with file size of 25,068,313 Bytes takes 1~1.3 sec response time.

### Requirements

- CPython 3.8+ (tested on CPython3.10)
- MariaDB 10.x / MySQL ~= 5.5

For python libraries, please refer [requirements.txt](requirements.txt)

`trio-mysql` cannot use MySQL version higher than that, but support latest stable MariaDB. (Tested on 10.7.1)

### Usage

Fill out [db_conf.ini](db_conf.ini) and just run [server.py](server.py).

Send POST to `http://127.0.0.1/files` with multipart file attachment.

On Successful POST server will generate md5 hash, and store file name, hash in database, while storing the image in `./uploaded`.

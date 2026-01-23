
## Rclone Mount

It's surprisingly hard to properly configure rclone mounts on windows. Everything is in their docs, but still finding
the right combination that works for you is still a bit of trouble.

Just make sure to use DIRECT PATH, not even junction.
So `scoop` installation won't work for service or task scheduler, idk why either!

`rclone.conf`:
```ini
[some_server]
type = sftp
host = YOUR_SERVER_ADDR
user = YOUR_SFTP_USER
key_file = FULL_PATH_TO_PRIV_KEY_FILE
shell_type = unix
md5sum_command = md5sum
sha1sum_command = sha1sum

[sftp]
type = alias
remote = some_server:/FOLDER/YOU/WANT/AS/ROOT
```

batch:
```commandline
FULL_PATH_TO_RCLONE\rclone.exe mount sftp: F: --volname sftp ^
--network-mode --links --transfers 16 ^
--config FILL_PATH_TO_CONF\rclone.conf ^
-o FileSecurity="D:P(A;;FA;;;WD)" ^
--log-file %TEMP%\rclone.log --log-level INFO --no-console ^
--cache-dir %TEMP%\rclone --vfs-cache-mode writes ^
--vfs-cache-min-free-space 4G

REM NOTE TO SELF:

REM install service via:
REM nssm install "_rclone" SCRIPT_FULL_PATH
REM nssm start

REM also disable windows explorer history in explorer settings in win11
REM otherwise mere file move & renaming takes 5-10 sec
```

| notable param                | details                                                                                                                                                                                 |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-o FileSecurity`            | Allow FILE EDIT on mounted drive. Otherwise can upload/delete but not editing. Refer [this](https://rclone.org/commands/rclone_mount/#windows-filesystem-permissions) for finer control |
| `--vfs-cache-mode writes`    | Write cache which is almost always required. Don't use `full`, it just adds notable overhead for large archive file opening in sftp                                                     |
| `--cache-dir`                | Optional, I set it since I use ramdisk                                                                                                                                                  |
| `--vfs-cache-min-free-space` | Optional, makes sure there's enough room in drive where `cache-dir` is in                                                                                                               |
| `--network-mode`             | Optional, marks mount as network drive on explorer                                                                                                                                      |


This command will start rclone mount named `sftp` with volume name `sftp` at mount point `F:`,
with 16 concurrent transfers & file cache on write (which is required for permissions to work)

Consider installing this as service using [`nssm`](https://nssm.cc/commands).


## Rclone Mount

It's surprisingly hard to properly configure rclone mounts on windows. Everything is in their docs, but still finding
the right combination that works for you is still a bit of trouble.

Since I just put all the portable stuffs in `C:\Shortcuts` script is based on it,
but I'll keep this as-is because these are mostly memo for myself thanks to my terrible memory.

- Make sure to use DIRECT PATH, not even junction.
`scoop` installation won't work for service or task scheduler.

- Log is optional, but I like to keep it so I can see what's going on.

- `FileSecurity` is there to allow FILE EDIT on mounted drive.
Otherwise file upload/delete works but not editing.
Refer [this](https://rclone.org/commands/rclone_mount/#windows-filesystem-permissions) for finer control.

- `cache-dir` is optional, but I set it since I have ramdisk for `%TEMP%` using `AIM Toolkit`.

```commandline
C:\Shortcuts\rclone\rclone.exe mount sftp: F: --volname sftp --network-mode ^
--cache-dir %TEMP%\rclone --vfs-cache-mode writes ^
--transfers 16 --links --config C:\Shortcuts\rclone.conf ^
--log-file %TEMP%\rclone.log --log-level ERROR --no-console ^
-o FileSecurity="D:P(A;;FA;;;WD)"

REM install service via:
REM nssm install "_rclone" C:\Shortcuts\mount_sftp.bat
REM nssm start
```

This command will start rclone mount with volume name `sftp` and mount point `F:`,
with 16 concurrent transfers & file cache on write (which is required for permissions to work)

Consider installing this as service using [`nssm`](https://nssm.cc/commands).

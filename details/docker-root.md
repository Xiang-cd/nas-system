# 修改docker root到nfs中

为了防止debian服务器太过于臃肿，以及系统盘有限, 所以考虑将docker home都转移到由truenas管理的大容量nfs中。

1. docker目录需要root权限, 所以在nfs共享时要将rootusermap设置为root
2. docker使用vfs才可以支持nfs后端，所以需要修改docker设置, 修改`/etc/docker/daemon.json`

```json
{
    "data-root": "/mnt/docker",
    "storage-driver": "vfs"
}
```

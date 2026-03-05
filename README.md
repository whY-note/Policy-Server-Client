

## 注意事项

### 格式转化
Be carefull: 

- Cannot do: np.bytes -> json
- Can do: bytes -> json

### 服务器端口不可用：利用隧道
在本地的一个终端输入
```bash
ssh -p 6361 -L 9000:localhost:9000 root@120.48.23.252
```

在另一个终端启动对应的 client 程序

注意： 将服务器的公网IP换成`localhost`

对于`web_client.py`: 
`server_url` 不是用`"ws://120.48.23.252:9000"` 而是`"ws://localhost:9000"`
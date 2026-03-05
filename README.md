# Policy Server and Client

## 工作流程

```mermaid
sequenceDiagram
    participant Robot as Robot (Server)
    participant Policy as Policy (Client)

    Robot->>Policy: obs
    Policy-->>Robot: action
```





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
> [!NOTE]
>
> **参数解析：**
>
> `9000:localhost:9000` 中：
>
> 左边的`9000`是本地的 TCP socket 或 Web socket 所用的端口
>
> 右边的`9000`是服务器的 TCP socket 或 Web socket 所用的端口
>
> 这两个数字**可以不同**。
>
> `-p 6361` 是指服务器的ssh端口，比如下面这样：
>
> ```bash
> Host baidu_a800
>     HostName 120.48.23.252
>     Port 6361
>     User root
> ```

然后在另一个终端启动对应的 client 程序

> [!CAUTION]
>
> 注意： 将服务器的公网IP换成`localhost`
>
> 对于`web_client.py`: `server_url` 不是用`"ws://120.48.23.252:9000"`，而是`"ws://localhost:9000"`
>
> 对于`tcp_client.py`: `host`不是用`120.48.23.252`，而是`localhost`

## TODO

- [x] 在scripts里添加测试代码：从config/yaml中读取配置，然后调用api
- [ ] shell文件，实现一键测试，类似于操作系统比赛的测例一样
- [ ] 加入UDP
- [ ] 尝试将TCP也变成异步, 用`async`

## 知识

对于一个线程：

- 不用`async`: 对于多个连接的请求，只能逐个**串行**
- 使用`async`: 对于多个连接的请求，可以**并发**执行（ 执行模式：一个线程，多个协程，事件循环调度）

对于多个线程或者多个进行：

不用`async`也可以并发执行
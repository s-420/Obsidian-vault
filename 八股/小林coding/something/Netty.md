## 什么是 Netty

==Netty 是一个高性能、异步事件驱动的 NIO 网络通讯框架== [10]。它提供了对 Java 原生 NIO（非阻塞 I/O）API 的高级封装，大大简化了网络编程的复杂度（如 TCP 粘包/拆包处理、多线程反应器模型构建等）[2, 10]。

如果把 Java 原生的 NIO 比作原材料（钢筋水泥），那么 Netty 就是已经建好的高架桥。你不需要自己去抠底层的网络细节，直接在上面跑业务代码即可。现代 Java 生态中，绝大多数涉及高性能网络通信的中间件（如 Dubbo、RocketMQ、Elasticsearch、Gateway 等）底层都 100% 选用 Netty 作为通信核心。

---

## 核心基石：Reactor 线程模型

Netty 能够支撑百万级高并发的核心，在于它实现了极其高效的 Reactor（反应器）线程模型。在 Netty 中，这套模型被具象化为两个组件：BossGroup 和 WorkerGroup。

```unset
[客户端请求] ──> [BossGroup (EventLoopGroup)]
                       │
                       │ (1. 负责连接建立 accept)
                       ▼
                 [WorkerGroup (EventLoopGroup)]
                       │
                       │ (2. 负责非阻塞读写 read/write)
                       ▼
           [Pipeline 管道 (各种 Handler 业务处理)]
```

- BossGroup：专门负责接收客户端的连接请求（Accept 事件）。它通常只需要极少的线程（默认 1 个即可）。当它成功建立连接后，会将生成的 `SocketChannel` 注册并丢给 WorkerGroup。
- WorkerGroup：专门负责处理连接的读写事件和业务逻辑（Read/Write 事件）。它的线程数默认是 `CPU 核心数 × 2`。这组线程会不停地轮询已经建立的连接，一旦某个连接有数据传过来，它就负责读取数据并派发处理。

---

## 三大核心组件

Netty 的代码架构非常优雅，主要由以下三个核心概念串联而成：

- Channel（通道）：网络通信的载体，代表了一个开放的连接（例如一个 TCP 结合点）。它负责底层的网络读写操作。
- Handler（处理器）：核心业务逻辑的实施者。你可以把它理解为过滤器。数据进出 Channel 都要经过一层层的 Handler 处理（比如：解码 Handler → 权限校验 Handler → 业务数据处理 Handler → 编码 Handler）。
- ChannelPipeline（管道）：一个由 Handler 串联而成的双向链表。每一个 Channel 在创建时都会被分配一个专属的 Pipeline。数据就像水流一样，在这个管道中被各个 Handler 依次拦截并加工。

---

## 为什么 Netty 性能高（面试必问）

- 同步非阻塞 I/O：基于 Java NIO 机制，用极少数的线程就能维持海量的并发连接，不再像 BIO 那样因为等待数据而阻塞线程。
- 零拷贝（Zero-Copy）：Netty 在接收和发送数据时，采用了直接内存（Direct Buffer），数据可以直接在操作系统的内存缓冲区进行读写，避免了数据在 JVM 堆内存与操作系统内核之间来回复制，极大释放了 CPU。
- 高效的并发无锁设计：Netty 的 `EventLoop`（事件循环）采用“一线程一事件循环”的设计。这意味着一个连接的所有读写操作永远由同一个线程执行。因为没有多线程竞争，所以完全不需要加锁，执行效率极高。

---

如果想进一步探讨，可以告诉我：

- 你想看一个简单的 Netty 服务端/客户端 Hello World 代码实现吗？
- 需要了解 Netty 是如何解决 TCP 传输中让人头疼的 粘包与拆包 问题的吗？
- 对 Netty 中 ByteBuf（内存缓冲区） 的对象池化和自研引用计数感兴趣吗？
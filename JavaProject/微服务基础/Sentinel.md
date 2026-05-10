# Sentinel

Sentinel 是作用于 服务保护的框架，对资源添加保护规则

随着微服务的流行，服务和服务之间的**稳定性**变得越来越重要。**Spring Cloud Alibaba Sentinel** 以流量为切入点，从 **流量控制、流量路由、熔断降级、**系统自适应 **过载保护、热点流量防护** 等多个维度保护服务的稳定性。

## 1 工作原理

### 1.1 架构原理

1. 定义规则
2. 存储规则
3. 向资源发送规则（规则 校验资源）

![{C3616D76-9DEC-42AD-82EE-4F79C45A67D2}](https://gitee.com/s420/image-bed/raw/master/img/{C3616D76-9DEC-42AD-82EE-4F79C45A67D2}.png)

### 1.2 资源 与 规则

**定义资源：**

- 主流框架 **自动适配** （Web Servlet、Dubbo、Spring Cloud、gRPC、Spring WebFlux、Reactor）；所有Web接口均为资源
- 编程式：SphU API
- 声明式：@SentinelResource

**定义规则：**

- 流量控制（FlowRule）
- 熔断降级（DegradeRule）
- 系统保护（SystemRule）：根据当前系统的 cpu的负载、内存使用率 限制请求的进入
- 来源访问控制（AuthorityRule）
- 热点参数（ParamFlowRule）

### 1.3 工作原理

<img src="https://gitee.com/s420/image-bed/raw/master/img/{16E126BF-26AB-41D5-89F1-AE4977C94919}.png" alt="{16E126BF-26AB-41D5-89F1-AE4977C94919}" style="zoom: 50%;" />

用户 请求资源，若配置了规则，则会进行 Sentinel 检查，判断是否违反规则，若未违反规则，则放行 结束，r
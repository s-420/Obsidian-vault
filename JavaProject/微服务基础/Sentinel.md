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

用户 请求资源，若配置了规则，则会进行 Sentinel 检查，判断是否违反规则，若未违反规则，则放行 结束，若违反规则 抛出异常，判断是否有异常处理，没有则 输出默认错误 结束，若有则 执行fallback 结束

---

## 2 整合使用

### 2.1 docker 部署

~~~ java
docker pull bladex/sentinel-dashboard:1.8.8

 docker run -d --name sentinel-dashboard -p 8858:8858 
     -e JAVA_OPTS="-Dserver.port=8858 Dsentinel.dashboard.auth.username=sentinel -Dsentinel.dashboard.auth.password=sentinel" 
     bladex/sentinel-dashboard:1.8.8
~~~

### 2.2 连接控制台

#### 2.2.1 配置场景依赖

~~~ java
spring:
  cloud:
	sentinel:
      transport:
        dashboard: 127.0.0.1:8858
~~~

#### 2.2.2 配置规则

![{47A1F00A-11A2-4B84-8EBF-6F42D7F3B0BA}](https://gitee.com/s420/image-bed/raw/master/img/{47A1F00A-11A2-4B84-8EBF-6F42D7F3B0BA}.png)

## 3 异常处理

![{BC560BFF-728A-43CF-BD24-BC6907BC66AC}](https://gitee.com/s420/image-bed/raw/master/img/{BC560BFF-728A-43CF-BD24-BC6907BC66AC}.png)

### 3.1 Web接口

对于web接口（对 请求接口），sentinel的异常处理机制是通过SentinelWebInterceptor 拦截器拦截，若有异常，则由默认的BlockExceptionHandler返回默认异常信息，可以自定义 MyBlockExceptionHandler实现BlockExceptionHandler来自定义异常信息

MyBlockExceptionHandler：

```java
@Component
public class MyBlockExceptionHandler implements BlockExceptionHandler {
    @Override
    public void handle(HttpServletRequest httpServletRequest,
                       HttpServletResponse httpServletResponse,
                       String s, BlockException e) throws Exception {
        PrintWriter writer = httpServletResponse.getWriter();
        httpServletResponse.setContentType("application/json;charset=utf-8");

        R error=R.error(500,s+"被sentinel限流了"+e.getMessage());
        String json= JSONUtil.toJsonStr(error);
        writer.write(json);
    }
}
```

被规则保护的资源：

```java
@GetMapping("/order/create")
public Order createOrder(@RequestParam("productId") Long productId, @RequestParam("userId") Long userId) {
    return orderService.createOrder(productId,userId);
}
```

### 3.2 @SentinelResource

对于 @SentinelResource（对方法），底层是一个SentinelResourceAspect 切面类，其中逻辑是，若符合规则则正常返回，若不符合规则，则通过注解中指定的blockHandler兜底处理方法进行兜底回调，若blockHandler不存在，则查看是否指定了fallback，若fallback不存在，则看是否指定了DefaultFallback，若都没有则抛出系统异常
简单解决，自定义个兜底方法，添加到注解参数中

对应方法：

```java
//被规则保护的资源
@SentinelResource(value="createOrder",blockHandler="createOrderHandleBlock")
@Override
public Order createOrder(Long productId, Long userId) {
    //Product product = getProductFromRemoteWithLoadBalanceByAnnotation(productId);
    Product product = productFeignClient.getProductById(productId);
    // 计算订单金额
    BigDecimal totalAmount = product.getPrice().multiply(BigDecimal.valueOf(product.getNum()));
    return Order.builder()
            .id("123")
            .totalAmount(totalAmount)
            .userId(userId)
            .nickname("张三")
            .address("北京市海淀区")
            .productList(List.of(product))
            .build();
}
//兜底方法
public Order createOrderHandleBlock(Long productId, Long userId, BlockException e) {
    return Order.builder()
            .id("123")
            .totalAmount(BigDecimal.ZERO)
            .userId(userId)
            .nickname("未知用户")
            .address("异常信息"+e.getMessage())
            .build();
}
```

### 3.3 OpenFeign 远程调用

对于openfeign（对远程调用方法），由SentinelFeign.builder()执行，@FeignClient中的兜底返回机制，若未配置则也会抛出系统异常

被规则保护的资源：

```java
@FeignClient(value="service-product",fallback= ProductFeginClienFallBack.class)
@Component
public interface ProductFeignClient {

    @GetMapping("/product/{productId}")
    Product getProductById(@PathVariable("productId") Long productId);
}
```

兜底方法：

```java
@Component
public class ProductFeginClienFallBack implements ProductFeignClient {
    @Override
    public Product getProductById(Long productId) {
        System.out.println("兜底回调...");
        return Product.builder()
                .productId(productId)
                .price(BigDecimal.valueOf(0))
                .productName("兜底商品")
                .num(0)
                .build();
    }
}
```

## 4 流量控制

流量控制，是通过限制多于请求，避免资源被耗尽，导致服务雪崩的策略

### 4.1 阈值类型

- QPS：每秒单个线程请求数
- 并发线程数：多个线程的请求

单机：

- 单机阈值：一次允许通过的请求数

集群：

- 均摊阈值：假设均摊阈值为5
  - 单机均摊：每个服务器，最多为5，总体最多15
  - 总体阈值：所有服务器，最多为5

### 4.2 流控模式

![{9C99CEE9-67E9-4A46-B762-C9F8169408D1}](https://gitee.com/s420/image-bed/raw/master/img/{9C99CEE9-67E9-4A46-B762-C9F8169408D1}.png)
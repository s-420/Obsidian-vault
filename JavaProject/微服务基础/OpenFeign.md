# OpenFeign

**openfeign** 是Spring Cloud 生态的声明式 Http客户端

**核心特点**：

| 特点         | 说明                                   |
| ------------ | -------------------------------------- |
| 声明式       | 只需要定义接口，不需要编写HTTP调用代码 |
| 负载均衡     | 集成Ribbon，自动实现负载均衡           |
| 若错/降级    | 支持fallback（服务不可用时返回默认值） |
| 整合注册中心 | 自动从 Nacos/Eureka获取服务实例        |

**相关注解**：

| 注解                                                        | 功能                               |
| ----------------------------------------------------------- | ---------------------------------- |
| @FeignClient                                                | 指定远程调用地址，配置，兜底实现类 |
| @GetMapping、<br />@PostMapping、<br />@DeleteMapping ……    | 指定请求方式                       |
| @RequestHeader、<br />@RequestParam、<br />@RequestBody！…… | 指定携带参数                       |

## 1.编写 OpenFeign 远程调用客户端

### 1.1 引入依赖

```xml
<!--远程调用-->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-openfeign</artifactId>
</dependency>
```

### 1.2 基本实现

#### 1.2.1 在启动类上，加上@EnableFeignClients的可执行注解：

~~~ java
@EnableFeignClients
@SpringBootApplication
@EnableDiscoveryClient
public class OrderMainApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderMainApplication.class,args);
    }
}
~~~

#### 1.2.2 编写 Feign 远程调用客户端

```java
@FeignClient(value="service-product",fallback= ProductFeginClienFallBack.class)
public interface ProductFeignClient {

    @GetMapping("/product/{productId}")
    Product getProductById(@PathVariable("productId") Long productId);
}
```

**@FeignClient** 参数：

- value/name：指定服务名称（用于服务发现）
- url：直接指定服务URL（跳过服务发现，超用于调用第三方api）
- fallback：指定降级处理类（不包含异常信息）
- configuration：自定义配置类
- contextId：多客户端区分标识，未指定则将value/name 当作标识
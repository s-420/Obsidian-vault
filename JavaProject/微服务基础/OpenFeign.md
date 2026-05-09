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

接口抽象方法，模拟被调用服务的http请求来写

#### 1.3 客户端负载均衡与服务端负载均衡的区别![{56C35088-D643-40E1-832F-61DC29260F0C}](https://gitee.com/s420/image-bed/raw/master/img/{56C35088-D643-40E1-832F-61DC29260F0C}.png)

客户端：发送请求的这一端，自己发起负载均衡算法，获取服务地址列表，选择服务地址，并发起请求
服务端：接受请求的这一段，服务端内部实现负载均衡
**总结：** 客户端主动选择服务，服务端被动分配服务

---

## 2 进阶用法

### 2.1 日志功能

#### 2.1.1 修改配置文件

在 配置文件中，配置日志模式

~~~ java
spring：
  cloud：
    openfeign:
      client:
        config:
          default:
            logger-level: FULL
            connect-timeout: 10000
            read-timeout: 20000
          service-product:
            # logger-level: FULL
            connect-timeout: 1000
            read-timeout: 2000
~~~

spring:cloud：openfeign:client:config:default/服务名：logger-level:FULL

#### 2.1.2 修改配置类

在配置类中注册，该配置：

```java
@Bean
Logger.Level feginLoggerLevel(){
    return Logger.Level.FULL;
}
```

### 2.2 超时机制

#### 2.2.1 修改配置文件

代码：2.1.1
connect-timeout：连接超时 
read-timeout：读取超时

### 2.3 重试机制

实现方式：

- 修改配置类：

  - ```java
    application.yml
    service-product:
      retryer: default
    ```

- 修改配置文件：

  - ```java
    OrderConfig.java
    @Bean
    Retryer retryer(){
        return new Retryer.Default();
    }
    ```

---

## 3 拦截器（请求拦截器）

#### 3.1 新建请求拦截类

新建请求拦截类，并实现RequestInterceptor接口

```java
@Component
public class XTokenRequestInterceptor implements RequestInterceptor {


    @Override
    public void apply(RequestTemplate requestTemplate) {
        System.out.println("Xtoken-----------");
        requestTemplate.header("token", UUID.randomUUID().toString());
    }
}
```

### 3.2 拦截注册

两种实现方式，注入容器/添加配置

- 在请求拦截类上，添加@Component，将拦截器注入容器

- 在配置文件中，配置拦截器参数

  - ```yml
    openfeign:
      client:
        config:
          service-product:
            request-interceptors:
              - com.s420.interceptor.XTokenRequestInterceptor
            response-interceptor:
              - com.s420.interceptor.XTokenResponseInterceptor
    ```

## 4 兜底返回

远程调用中，若远程调用失败，返回兜底数据（通过兜底类实现请求接口，降级处理）
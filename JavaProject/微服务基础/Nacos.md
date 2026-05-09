# 注册中心

## 1.服务注册

### **1.1 引入依赖**

~~~ xml
<dependency>  
    <groupId>com.alibaba.cloud</groupId>  
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>  
</dependency>
~~~

### **1.2 配置nacos地址**

~~~ yml
spring:
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        username: nacos
        password: nacos
~~~

### **1.3 在nacos中注册**

启动服务控制台中出现

~~~java
2026-05-07T10:22:56.670+08:00  INFO 12448 --- [service-order] [           main] c.a.c.n.registry.NacosServiceRegistry    : nacos registry, DEFAULT_GROUP service-order 192.168.219.1:8000 register finished

~~~

即为成功注册

### **1.4 通过多个端口模拟集群模式**

nacos服务列表中可以看到 一个服务有多个实例数

![](https://gitee.com/s420/image-bed/raw/master/img/屏幕截图 2026-05-07 103358.png)

![{3B6BA6C2-0A35-49B6-B3C6-01351E98D4D7}](https://gitee.com/s420/image-bed/raw/master/img/{3B6BA6C2-0A35-49B6-B3C6-01351E98D4D7}.png)

![{16759D72-633B-4263-8EC9-426FC7995703}](https://gitee.com/s420/image-bed/raw/master/img/{16759D72-633B-4263-8EC9-426FC7995703}.png)

---

## 2.服务发现

### 2.1 添加@EnableDiscoveryClient注解

在 启动类 上 添加@EnableDiscoveryClient注解后，就可以调用 DiscoveryClient的api

~~~ java
@SpringBootApplication
@EnableDiscoveryClient
public class OrderMainApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderMainApplication.class,args);
    }
~~~

### **2.2 DiscoveryClient**

通过 **DiscoveryClient** 的方法 实现服务发现功能

- **discoveryClient.getService:**获取服务对象（实际上获取的是服务名称）
- **service.getInstance**:获取对象实例
- **instance.getHost**:获取实例IP
- **instance.getPort**:获取实例端口

**测试代码如下：**

```java
@SpringBootTest
public class DiscoveryTest {

    @Autowired
    private DiscoveryClient discoveryClient;

//    @Autowired
//    private NacosServiceDiscovery nacosServiceDiscovery;

    @Test
    void discoveryClientTest(){
        List<String> services = discoveryClient.getServices();
        for (String service : services) {
            // 获取服务名称
            System.out.println(service);
            // 获取服务实例列表（ip:port）
            List<ServiceInstance> instances = discoveryClient.getInstances(service);
            for (ServiceInstance instance : instances) {
                System.out.println(instance.getHost() + ":" + instance.getPort());
            }
        }
    }

}
```

> NacosServiceDiscovery 也是服务发现的api 也有相同的功能，不过只针对nacos

---

## 3 nacos远程调用

![{379F7B6E-5BD8-4708-880C-654282D18799}](https://gitee.com/s420/image-bed/raw/master/img/{379F7B6E-5BD8-4708-880C-654282D18799}.png)

### 3.1 远程调用实现

远程调用，本质是通过，discoveryClient 获取服务的信息，来拼接url，通过RestTemplate进行远程调用

**首先要编写RestConfig配置类，RestConfig：**

```java
@Configuration
public class RestConfig {

    @Bean
    @LoadBalanced
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
```

**封装成getProductFromRemote方法实现：**

```java
@Service
public class OrderServiceImpl implements OrderService {

    @Autowired
    private DiscoveryClient discoveryClient;

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private LoadBalancerClient loadBalancerClient;

    @Override
    public com.s420.order.bean.Order createOrder(Long productId, Long userId) {
        Product product = getProductFromRemoteWithLoadBalanceByAnnotation(productId);
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

    // 从远程服务获取商品信息
    private Product getProductFromRemote(Long productId) {
        List<ServiceInstance> instances = discoveryClient.getInstances("service-product");
        ServiceInstance instance = instances.get(0);
        // http://localhost:8003/product/1
        String uri="http://"+instance.getHost()+":"+instance.getPort()+"/product/"+productId;
        return restTemplate.getForObject(uri, Product.class);
    }
}
```

### 3.2 负载均衡

#### 3.2.1 LoadBalancerClient

通过 loadBalancerClient.choose()方法 从服务列表中 按 负载均衡算法 获取一个对象实例

```java
// 优化 1：完成负载均衡
private Product getProductFromRemoteWithLoadBalance(Long productId) {
    ServiceInstance instance = loadBalancerClient.choose("service-product");
    // http://localhost:8003/product/1
    String uri="http://"+instance.getHost()+":"+instance.getPort()+"/product/"+productId;
    System.out.println(uri);
    return restTemplate.getForObject(uri, Product.class);
}

```

#### 3.2.2 @LoadBalanced

[]: D:\Code\JavaProjects\Obsidian-vault\JavaProject\微服务基础\@LoadBalanced注解原理深度解析.md

在RestTemplate上，添加LoadBalanced来实现负载均衡

~~~ java
 @Bean
    @LoadBalanced
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
~~~

## 3.3 **注册中心宕机，远程调用还能成功吗？**

第一次 向注册中心获取微服务地址列表的时候，会将服务所有的地址进行缓存，所以如果是第一次调用就宕机，远程调用不能成功，如果，后续调用时注册中心宕机，还可以通过缓存的地址成功调用

---

## 4 配置中心

### 4.1 基本用法

#### 4.1.1 引入依赖

```java
<!--配置中心-->
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
</dependency>
```

### 4.1.2 在nacos中配置文件

![{5299F4BB-1D73-4478-B61F-17865CE9D9D4}](https://gitee.com/s420/image-bed/raw/master/img/{5299F4BB-1D73-4478-B61F-17865CE9D9D4}.png)

创建配置成功后，会在启动时自动加载配置

~~~ java
2026-05-07T10:22:54.905+08:00  WARN 12448 --- [service-order] [           main] c.a.c.n.c.NacosConfigDataLoader          : [Nacos Config] config[dataId=order.yml, group=order] is empty
2026-05-07T10:22:54.905+08:00  INFO 12448 --- [service-order] [           main] c.a.c.n.c.NacosConfigDataLoader          : [Nacos Config] Load config[dataId=database.yml, group=order] success
2026-05-07T10:22:54.905+08:00  INFO 12448 --- [service-order] [           main] c.a.c.n.c.NacosConfigDataLoader          : [Nacos Config] Load config[dataId=common.yml, group=order] success
~~~

### 4.1.3 解决导入检查

在项目中引入了 配置的依赖，但在nacos中并未创建这个依赖时，**Spring Cloud Nacos 提供的配置导入检查机制**，程序会报错

**解决方案：**

- ```xml
  - optional: # 通过optional来标识，此配置时可选择的
  spring:
    config:
      import:
        - optional:nacos:common.yml?group=order
  ```

- ~~~xml
  import-check:# 将导入检查功能关闭
  spring:
    config:
      import-check:
        enabled:false
  ~~~

---

### 4.2 自动刷新

### 4.2.1 @RefreshScope

在 controller 上 加上 @RefreshScope ,在配置中心中修改了配置，就会自动刷新

```java
//@RefreshScope 自动刷新配置
@RestController
public class OrderController {
    @Autowired
    private OrderService orderService;

    @Autowired
    private OrderProperties orderProperties;

    @GetMapping("/order/config")
    public String getAutoConfig(){
        String str=orderProperties.getTimeOut()+"///"+
                orderProperties.getAutoConfig()+"///"+orderProperties.getDbUrl();
        return str;
    }



    @GetMapping("/order/create")
    public Order createOrder(@RequestParam("productId") Long productId, @RequestParam("userId") Long userId) {
        return orderService.createOrder(productId,userId);
    }
}
```

### 4.2.2 @ConfigrationProperties（prefix=” ”）

若 配置中 有经常要用到的变量，则可以将变量封装到配置属性类中

orderProperties.class:

```
@Data
@ConfigurationProperties(prefix = "order")
@Component
public class OrderProperties {

    String timeOut;

    String autoConfig;

    String dbUrl;
}
```

这样 不用加 @RefreshScope 就可以实现自动刷新

---

## 5 配置监听

### 5.1 NacosConfigManager 

NacosConfigManager，是 nacos 提供的 一种通过编码的方式 监听配置变化的方法

#### 5.1.1实现 配置监听功能

用 NacosConfigManaer 来实现配置监听功能：

实现 **配置中心中的配置文件一变化 就输出日志信息**

> 1）项目启动就监听配置文件变化（ApplicationRunner 一次性任务，项目一启动，这个任务就会启动）
> 2）发生变化后拿到变化的值（NacoConfigManager 的 configService.addListener，其中 Listener参数来 实现获取变化的配置信息
> 3）输出日志信息

```java
@Bean
ApplicationRunner applicationRunner(NacosConfigManager nacosConfigManager){
    return args -> {
        ConfigService configService = nacosConfigManager.getConfigService();
        configService.addListener("service-order.yaml","DEFAULT_GROUP",
                new Listener(){

                    @Override
                    public Executor getExecutor() {
                        return Executors.newFixedThreadPool(4);
                    }

                    @Override
                    public void receiveConfigInfo(String s) {
                        System.out.println("变化的配置信息：\n"+s);
                        System.out.println("-----------------");
                    }
                });
        System.out.println("-----------------");
    };
}
```

> nacosConfigManager 获取 配置服务对象，addListener方法，绑定配置方法，并配置监听

## 6 如果配置中心和微服务中有相同的配置会使用哪个配置？

从配置中心的设置初衷来看，配置中心本就是为了，统一管理配置存在的，如果以微服务的配置为主，配置中心就是去了存在的意义了。
先导入优先，外部优先

---

## 7 数据隔离

当 项目有多套环境：dev、test、prod 时，每个微服务 同一个配置 每套环境的值都不一样，项目可以通过切换环境，加载对应环境的配置

![{00B55A91-B355-4541-93FC-187E5A015F41}](https://gitee.com/s420/image-bed/raw/master/img/{00B55A91-B355-4541-93FC-187E5A015F41}.png)

通过 Namespace--->Group--->Data-id 这样层层分组来对应 隔离不同环境下的配置

### 7.1 Nacos 操作

#### 7.1.1 新建命名空间

![{8473B944-FF45-4DEF-844B-D461E13F7E3A}](https://gitee.com/s420/image-bed/raw/master/img/{8473B944-FF45-4DEF-844B-D461E13F7E3A}.png)

![{E15AB0D3-FACF-41DA-9F05-3F3A68A78B8B}](https://gitee.com/s420/image-bed/raw/master/img/{E15AB0D3-FACF-41DA-9F05-3F3A68A78B8B}.png)

#### 7.1.2 创建配置

![](D:\HuaweiMoveData\Users\施鸿福\Pictures\Screenshots\屏幕截图 2026-05-07 230748.png)

新建配置时 设置Group 和 Data ID

#### 7.2.1 编写配置文件

```yml
server:
  port: 8000

spring:
  application:
    name: service-order
  profiles:
    active: dev # 默认激活的配置文件
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        username: nacos
        password: nacos
      config:
        server-addr: 127.0.0.1:8848
        username: nacos
        password: nacos
        import-check:
          enabled: false
        namespace: ${spring.profiles.active:dev} #本质是Nacos的namespace id，这里因为刚好设置的是dev，所以这里就用dev

---
spring:
  config:
    import:
      - optional:nacos:common.yml?group=order
      - optional:nacos:database.yml?group=order
      - optional:nacos:order.yml?group=order
    activate:
      on-profile: dev
---
spring:
  config:
    import:
      - optional:nacos:common.yml?group=order
      - optional:nacos:database.yml?group=order
      - optional:nacos:order.yml?group=order
    activate:
      on-profile: prod
---
spring:
  config:
    import:
      - optional:nacos:common.yml?group=order
      - optional:nacos:database.yml?group=order
      - optional:nacos:order.yml?group=order
    activate:
      on-profile: test

```

> - spring:profile:active: dev : 默认激活的配置文件
> - --- ： 配置分页
> - spring:config:activate:on-profile:dev ：对应激活环境的配置内容，通过分页来区分（实际开发中也会分为三个yml文件）
> - spring:nacos:config:namespace：对应nacos中配置的命名空间 ID，命名空间的唯一标识

---


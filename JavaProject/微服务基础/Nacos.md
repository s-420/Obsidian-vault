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

## 3 远程调用

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

在RestTemplate

~~~ java
 @Bean
    @LoadBalanced
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
~~~


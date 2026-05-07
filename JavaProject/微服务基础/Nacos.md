# 注册中心

## 1.服务注册

**1.1 引入依赖**

~~~ xml
<dependency>  
    <groupId>com.alibaba.cloud</groupId>  
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>  
</dependency>
~~~

**1.2 配置nacos地址**

~~~ yml
spring:
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        username: nacos
        password: nacos
~~~

**1.3 在nacos中注册**

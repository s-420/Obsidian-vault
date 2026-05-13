# Gateway

![Spring Cloud Gateway Diagram](https://springdoc.cn/spring-cloud-gateway/images/spring_cloud_gateway_diagram.png)

## 1 网关功能

![{9E509E9D-FF8E-4375-A7BF-4C7FD221B813}](https://gitee.com/s420/image-bed/raw/master/img/{9E509E9D-FF8E-4375-A7BF-4C7FD221B813}.png)

在 前端请求 和 后端服务 中间，充当中转站，作为所有前端请求的入口， 并转发 到配置的后端服务

**功能：**

- 统一入口
- 请求路由
- 负载均衡
- 流量控制
- 身份认证
- 协议转换
- 系统监控
- 安全防护

---

## 2 基础使用

### 2.1 引入依赖

创建网关服务后，引入gateway依赖：

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-gateway</artifactId>
</dependency>
```

### 2.2 编写配置文件

**基础实现：**

```yml
spring:
  application:
    name: gateway
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        username: nacos
        password: nacos
    gateway:
      routes:
        
        - id: product-router
          uri: lb://service-product
          predicates:
          # 短写法
            - Path=/api/product/**

        - id: order-router
          uri: lb://service-order
          predicates:
          # 长写法
            - name: Path
              args:
                pattern: /api/order/**
                matchTrailingSlash: true
          order: 0
     
```

**配置参数：**

- id：网关名称（唯一标识）
- uri：转发地址（“lb: ”：标识负载均衡）
- predicates：断言
  - Path：断言名，用于指定接受的路径
- order： 设置优先级

---

## 3 Predicate 断言

### 3.1 断言工厂

以 Path的断言工厂为例：

```java
public class PathRoutePredicateFactory extends AbstractRoutePredicateFactory<Config> {
    private static final Log log = LogFactory.getLog(PathRoutePredicateFactory.class);
    private static final String MATCH_TRAILING_SLASH = "matchTrailingSlash";
    private PathPatternParser pathPatternParser = new PathPatternParser();

    public PathRoutePredicateFactory() {
        super(Config.class);
    }

    private static void traceMatch(String prefix, Object desired, Object actual, boolean match) {
        if (log.isTraceEnabled()) {
            String message = String.format("%s \"%s\" %s against value \"%s\"", prefix, desired, match ? "matches" : "does not match", actual);
            log.trace(message);
        }

    }

    public void setPathPatternParser(PathPatternParser pathPatternParser) {
        this.pathPatternParser = pathPatternParser;
    }

    public List<String> shortcutFieldOrder() {
        return Arrays.asList("patterns", "matchTrailingSlash");
    }

    public ShortcutConfigurable.ShortcutType shortcutType() {
        return ShortcutType.GATHER_LIST_TAIL_FLAG;
    }

    public Predicate<ServerWebExchange> apply(final Config config) {
        final ArrayList<PathPattern> pathPatterns = new ArrayList();
        synchronized(this.pathPatternParser) {
            this.pathPatternParser.setMatchOptionalTrailingSeparator(config.isMatchTrailingSlash());
            config.getPatterns().forEach((pattern) -> {
                PathPattern pathPattern = this.pathPatternParser.parse(pattern);
                pathPatterns.add(pathPattern);
            });
        }

        return new GatewayPredicate() {
            public boolean test(ServerWebExchange exchange) {
                PathContainer path = (PathContainer)exchange.getAttributes().computeIfAbsent(ServerWebExchangeUtils.GATEWAY_PREDICATE_PATH_CONTAINER_ATTR, (s) -> {
                    return PathContainer.parsePath(exchange.getRequest().getURI().getRawPath());
                });
                PathPattern match = null;

                for(int i = 0; i < pathPatterns.size(); ++i) {
                    PathPattern pathPattern = (PathPattern)pathPatterns.get(i);
                    if (pathPattern.matches(path)) {
                        match = pathPattern;
                        break;
                    }
                }

                if (match != null) {
                    PathRoutePredicateFactory.traceMatch("Pattern", match.getPatternString(), path, true);
                    PathPattern.PathMatchInfo pathMatchInfo = match.matchAndExtract(path);
                    ServerWebExchangeUtils.putUriTemplateVariables(exchange, pathMatchInfo.getUriVariables());
                    exchange.getAttributes().put(ServerWebExchangeUtils.GATEWAY_PREDICATE_MATCHED_PATH_ATTR, match.getPatternString());
                    String routeId = (String)exchange.getAttributes().get(ServerWebExchangeUtils.GATEWAY_PREDICATE_ROUTE_ATTR);
                    if (routeId != null) {
                        exchange.getAttributes().put(ServerWebExchangeUtils.GATEWAY_PREDICATE_MATCHED_PATH_ROUTE_ID_ATTR, routeId);
                    }

                    return true;
                } else {
                    PathRoutePredicateFactory.traceMatch("Pattern", config.getPatterns(), path, false);
                    return false;
                }
            }

            public Object getConfig() {
                return config;
            }

            public String toString() {
                return String.format("Paths: %s, match trailing slash: %b", config.getPatterns(), config.isMatchTrailingSlash());
            }
        };
    }

    @Validated
    public static class Config {
        private List<String> patterns = new ArrayList();
        private boolean matchTrailingSlash = true;

        public Config() {
        }

        public List<String> getPatterns() {
            return this.patterns;
        }

        public Config setPatterns(List<String> patterns) {
            this.patterns = patterns;
            return this;
        }

        /** @deprecated */
        @Deprecated
        public boolean isMatchOptionalTrailingSeparator() {
            return this.isMatchTrailingSlash();
        }

        /** @deprecated */
        @Deprecated
        public Config setMatchOptionalTrailingSeparator(boolean matchOptionalTrailingSeparator) {
            this.setMatchTrailingSlash(matchOptionalTrailingSeparator);
            return this;
        }

        public boolean isMatchTrailingSlash() {
            return this.matchTrailingSlash;
        }

        public Config setMatchTrailingSlash(boolean matchTrailingSlash) {
            this.matchTrailingSlash = matchTrailingSlash;
            return this;
        }

        public String toString() {
            return (new ToStringCreator(this)).append("patterns", this.patterns).append("matchTrailingSlash", this.matchTrailingSlash).toString();
        }
    }
}
```

断言工厂都继承于 AbstractRoutePredicateFactory：

```java
public abstract class AbstractRoutePredicateFactory<C> extends AbstractConfigurable<C> implements RoutePredicateFactory<C> {
    public AbstractRoutePredicateFactory(Class<C> configClass) {
        super(configClass);
    }
}
```

实现 AbstractConfigurable 接口

```java
@FunctionalInterface
public interface RoutePredicateFactory<C> extends ShortcutConfigurable, Configurable<C> {
    String PATTERN_KEY = "pattern";

    default Predicate<ServerWebExchange> apply(Consumer<C> consumer) {
        C config = this.newConfig();
        consumer.accept(config);
        this.beforeApply(config);
        return this.apply(config);
    }

    default AsyncPredicate<ServerWebExchange> applyAsync(Consumer<C> consumer) {
        C config = this.newConfig();
        consumer.accept(config);
        this.beforeApply(config);
        return this.applyAsync(config);
    }

    default Class<C> getConfigClass() {
        throw new UnsupportedOperationException("getConfigClass() not implemented");
    }

    default C newConfig() {
        throw new UnsupportedOperationException("newConfig() not implemented");
    }

    default void beforeApply(C config) {
    }

    Predicate<ServerWebExchange> apply(C config);

    default AsyncPredicate<ServerWebExchange> applyAsync(C config) {
        return ServerWebExchangeUtils.toAsyncPredicate(this.apply(config));
    }

    default String name() {
        return NameUtils.normalizeRoutePredicateName(this.getClass());
    }
}
```

![{C755ACD3-4293-48EA-B70F-BC8023E29D34}](https://gitee.com/s420/image-bed/raw/master/img/{C755ACD3-4293-48EA-B70F-BC8023E29D34}.png)

### 3.2 断言规则

![{1B36731F-7A29-4B5D-B419-2906F8269C77}](https://gitee.com/s420/image-bed/raw/master/img/{1B36731F-7A29-4B5D-B419-2906F8269C77}.png)

系统内置了，这些断言工厂，使用直接在配置文件中 配置就好

以Query为例（对应QueryRoutePredicateFactory，RoutePredicateFactory 前 即为断言名）：

```yml
spring:
  cloud:
    gateway:
      routes:
        - id: chrome-router
          uri: https://www.google.com/
          predicates:
            - name: Path
              args:
                pattern: /search
            - name: Query
              args:
                param: q
                regexp: haha
```

> 意义：只有路径为/search 开头，且携带参数 q 且其值为haha 则执行转发到uri


[[Predicate 与 Filter 的区别]]

### 3.3 自定义断言规则

### 3.3.1 自定义断言工厂

```java
@Component
public class VipRoutePredicateFactory extends AbstractRoutePredicateFactory<VipRoutePredicateFactory.Config> {
    public static final String PARAM_KEY = "param";
    public static final String VALUE_KEY = "value";

    public VipRoutePredicateFactory() {
        super(Config.class);
    }

    public List<String> shortcutFieldOrder() {
        return Arrays.asList(PARAM_KEY, VALUE_KEY);
    }

    public Predicate<ServerWebExchange> apply(final Config config) {
        return  new GatewayPredicate() {
            @Override
            public boolean test(ServerWebExchange serverWebExchange) {
                ServerHttpRequest request = serverWebExchange.getRequest();

                String param = request.getQueryParams().getFirst(config.getParam());

                return param != null && param.equals(config.getValue());
            }
        };

    }

    @Validated
    public static class Config {
        private @NotEmpty String param;
        private @NotEmpty String value;

        public Config() {
        }

        public String getParam() {
            return this.param;
        }

        public Config setParam(String param) {
            this.param = param;
            return this;
        }

        public String getValue() {
            return this.value;
        }

        public Config setValue(String value) {
            this.value = value;
            return this;
        }
    }

}
```

主要包含以下几个部分：

- @Component：注册自定义断言工厂

- PARAM_KEY/VALUE_KEY：断言参数

- VipRoutePredicateFactory()：构造方法

  - 告诉父类使用哪个配置类来解析yml中的参数
  - 父类会自动处理配置绑定和参数校验

-  List<String> shortcutFieldOrder() ：定义短配置的参数顺序

- Predicate<ServerWebExchange> apply(final Config config)：核心实现逻辑

  - 定义断言的核心逻辑，返回一个Predicate<ServerWebExchange>

  - 每个请求到达时 会调用 test() 方法来判断是否匹配

  - 返回 true 则允许 路由，返回 false 则拒绝

  - > Predicate 核心：校验请求是否匹配要求

- public static class Config： 内部类
  - 绑定配置和参数校验

~~~ java
请求进入网关 → 读取 YAML 配置 → 解析参数到 Config 对象 → 
→ 调用 apply(Config) 生成 Predicate → 
→ 对每个请求调用 test(ServerWebExchange) → 
→ 返回 true/false 决定是否路由
~~~

### 3.3.2 自定义断言配置

```yml
spring:
  application:
    name: gateway
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        username: nacos
        password: nacos
    gateway:
      routes:
        - id: chrome-router
          uri: https://www.google.com/
          predicates:
             - name: Vip
              args:
                param: user
                value: wujinhai
```

> 自定义断言规则：当路径中有 user 参数且其值等于 wujinhai的时候返回 true 放行

### 3.4 微服务之间的调用会经过网关吗

默认不通过网关，直接通过注册中心获取被调用方的地址，不通过网关
可以设置成经过网关，将@FeignClient的value值 设置为网关服务的名称

## 4 Filter 过滤器

### 4.1 Filter 基本使用

```yml
spring:
  application:
    name: gateway
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        username: nacos
        password: nacos
    gateway:
      routes:
        - id: product-router
          uri: lb://service-product
          predicates:
            - Path=/api/product/**
          filters:
            # - RewritePath=/api/product/?(?<segment>.*), /$\{segment}
            - name: ReWritePath
              args:
              
```

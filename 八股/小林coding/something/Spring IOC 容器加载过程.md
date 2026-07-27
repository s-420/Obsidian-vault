[https://zhuanlan.zhihu.com/p/1898510180670497408](https://zhuanlan.zhihu.com/p/1898510180670497408)

#### 1.简介

当 new ApplicationContext 或者 new BeanFacotry的时候，就创建了一个IOC容器（本质是一个ConcurrentMap容器，Key是BeaName，Value是 Bean 实例对象），当运行refresh的时候采取加载IOC容器

new ApplicationContext的时候，底层发生了什么

加载流程大致分四步：`概念态->定义态->纯静态->成熟态`

![](https://gitee.com/s420/image-bed/raw/master/img/屏幕截图 2026-07-27 211346.png)

#### 2 IOC容器加载步骤

##### 2.1 配置Bean

通过XML或javaConfig去配置Bean，没有配置Bean，[[BeanDefinition]]没有东西可以加载。

加载IOC容器的过程，也可以看作创建Bean的过程。

![img](https://pic2.zhimg.com/v2-8bbb3cb8818039f16ee9156ae6d6ab43_1440w.jpg)

#### 2.2 读取Bean到BeanDefinition

配置完毕后，会将Bean的各项参数（Class，lazy-init，scope，init-method）装载到BeanDefinition中。

我们可以把BeanDefiniion看作 **工厂的设计图纸** ，Bean配置则是 **概念的 设计点**

不同IOC容器，读取方式不同，

- ClassPathXmlAPplicationContext（读取的是XML的配置方式）
- AnnotationConfigApplicationContext（读取的是javaconfig的配置方式）

![img](https://picx.zhimg.com/v2-f38382f20e3da1553ad53c697fd497ed_1440w.jpg)

##### 2.3 生产Bean

生产由BeanFactory负责，通过BeanFactroy的getBean()（实际上ApplicationContext中的getBean()方法，底层是调用BeanFactroy方法）将Bean生产出来的（底层getBean()，会经历过一系列的校验，通过后 由docreateBean()来创建Bean实例）

getBean的时候，会判断是否容器中已存在Bean。如果存在就直接返回Bean，如果没有才会去做bean的生产

bean的生产过程：

1. **实例化**：实例化后bena是“纯净态”，之所以叫实例化，是因为bean实例化后，里面的字段、属性都是null。
2. 反射：通过反射将BeanDefiniton中的bean的Class，去做newInstance()，新建一个单例
3. 工厂：生产bean的时候，根据BeanDefiniton中参数指定的的factoryMethod来创建bean，生产过程灵活，可自定义
4. **属性赋值**：DI，自动注入。自动注入注解：@Autowired
5. **初始化**：调用生命周期的初始化回调方法

生产出来的bean默认是单例的，会把bean放入一个static的Map（一级缓存）Key为BeanName，Value为Bean的实例

**两种获取Bean的方法：**![{55937B34-7F11-4810-96CE-46E9BFEA2088}](https://gitee.com/s420/image-bed/raw/master/img/{55937B34-7F11-4810-96CE-46E9BFEA2088}.png)

- 通过bean **名字** 获取 bean（大多数情况）：通过@Component、@Bean这种方式注册的bean，后续通过 getBean获取的时 只是通过 **bean的名字** ，此时IOC容器Key只是**单纯的 Bean名**
- 通过bean **全路径名**获取bean（少数情况）：通过@Import导入的bean，通过getBean获取的时候使用**全路径名** 去获取，此时 **全路径名** 称作容器map的Key
- 调用bean的时候 其实就是通过 Key 去获取 Vaule中 bean的实例

Spring三级缓存：

![img](https://pic4.zhimg.com/v2-440485306f3f78f22e6495ce354850dd_1440w.jpg)

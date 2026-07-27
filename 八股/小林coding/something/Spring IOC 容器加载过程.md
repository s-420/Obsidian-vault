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

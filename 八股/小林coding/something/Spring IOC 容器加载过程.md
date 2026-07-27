[https://zhuanlan.zhihu.com/p/1898510180670497408](https://zhuanlan.zhihu.com/p/1898510180670497408)

#### 1.简介

当 new ApplicationContext 或者 new BeanFacotry的时候，就创建了一个IOC容器（本质是一个ConcurrentMap容器，Key是BeaName，Value是 Bean 实例对象），当运行refresh的时候采取加载IOC容器

new ApplicationContext的时候，底层发生了什么

加载流程大致分四步：`概念态->定义态->纯静态->成熟态`

![](https://gitee.com/s420/image-bed/raw/master/img/屏幕截图 2026-07-27 211346.png)

#### 2 IOC容器加载步骤

##### 2.1 配置Bean

通过XML或j'a


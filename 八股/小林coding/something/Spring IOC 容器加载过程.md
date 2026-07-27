[https://zhuanlan.zhihu.com/p/1898510180670497408](https://zhuanlan.zhihu.com/p/1898510180670497408)

当 new ApplicationContext 或者 new BeanFacotry的时候，就创建了一个IOC容器（本质是一个ConcurrentMap容器，Key是BeaName，Value是 Bean 实例对象），当运行refresh的时候采取加载IOC容器
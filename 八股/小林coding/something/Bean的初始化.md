========================================================================================
【属性填充完毕 (populateBean)】 ── 此时对象已经拿到所有依赖，开始进入 initializeBean()
   │
   ▼
【第一步：激活 Aware 身份感知接口】 (注入容器原生资源)
   │  1. 检查是否实现 BeanNameAware ──> 注入当前 Bean 的名字
   │  2. 检查是否实现 BeanClassLoaderAware ──> 注入类加载器
   │  3. 检查是否实现 BeanFactoryAware ──> 注入底层的工厂本身 (BeanFactory)
   ▼
【第二步：执行初始化前置处理器】 (BeanPostProcessor.postProcessBeforeInitialization)
   │  4. 拦截器介入，寻找类内部的特殊注解
   │  5. 🔍【核心爆发点】：解析并执行程序员写的 **`@PostConstruct`** 回调方法
   │  6. 激活 ApplicationContextAware 接口 ──> 注入高级应用上下文 (ApplicationContext)
   ▼
【第三步：执行正式初始化方法】 (invokeInitMethods)
   │  7. 检查是否实现 InitializingBean 接口 ──> 执行重写的 **`afterPropertiesSet()`** 方法
   │  8. 检查 BeanDefinition 图纸 ──> 执行你在配置里指定的自定义 **`init-method`** 方法
   ▼
【第四步：执行初始化后置处理器 (核心)】 (BeanPostProcessor.postProcessAfterInitialization)
   │  9. 流水线两旁的“质检员”最后一次拦截这个完全长成的 Bean
   │ 10. 🎭【AOP 动态代理诞生点】：检查该类是否匹配切面或 `@Transactional` 事务
   │ 11. 【如果是】：利用 JDK/CGLIB 在内存中彻底克隆包装，生成全新的 **`Proxy` 代理对象**
   ▼
【单例池晋升】 ── 彻底洗净，put 存入一级缓存 singletonObjects，初始化流程完美闭环！
========================================================================================

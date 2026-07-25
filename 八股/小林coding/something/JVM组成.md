## 类加载子系统

简述：将字节码文件加载进入内存

![{60F457EA-EF79-442D-83A2-B8866765D8EA}](https://gitee.com/s420/image-bed/raw/master/img/{60F457EA-EF79-442D-83A2-B8866765D8EA}.png)

工作流程：

- 加载
- 链接
  - 验证：验证待加载的class文件是否正确
  - 准备：为static变量分配内存并赋零值
  - 解析：将类的全域名解析为类在方法区中的地址
- 初始化
  - 为变量赋实际值

类加载器的分类：

![{32CC683D-4B45-48D5-9A3B-8EDD232C7A9D}](https://gitee.com/s420/image-bed/raw/master/img/{32CC683D-4B45-48D5-9A3B-8EDD232C7A9D}.png)

- 引导性类加载器
  - BootStrapClassLoader：jre/lib
- 自定义类加载器
  - ExtClassLoader:jre/lib/ext
  - AppClassLoader:classpath 指定的类加载器（指定的jar包，target/classes）
  - WebAppClassLoader
- 双亲委派：![](https://gitee.com/s420/image-bed/raw/master/img/{75FD171B-AD60-4E90-835D-5E1950391643}.png)

​	当AppClassLoader加载类时调用loadClass方法时，他会先去调用ExtClassLoader的loadClass方法去加载当前这个类，ExtLoadClass方法也会先去让BootStreapClassBloader区加载这个类

- 避免类被重复加载
  - 当前加载的类可能已经被父加载器使用过了
- 防止核心API被篡改
  - 若项目中类被篡改，但还是会优先加载父类原有的方法类（原始导入的包中的类）

总结，先让父类加载，找不到了再自己找，防止重复加载类

Tomcat为什么要加载自定义类加载器

![{35856DE9-31DA-4531-9CDD-6904A11E6974}](https://gitee.com/s420/image-bed/raw/master/img/{35856DE9-31DA-4531-9CDD-6904A11E6974}.png)

​	对于Tomcat来说，如果直接使用AppClassLoader加载器即同一个加载器实例，就会导致，若tomcat上的三个应用都要加载了一个相同类名的类，此时当已有其中一个类加载器被加载后，剩下的类加载器就不会被加载了；所以需要通过自定义类加载器，来处理自己对引得类，**就可以保证类加载的隔离**（由因：JVM判断一个类是否被加载的逻辑，类名+对应类加载器实例，多个app公用一个类加载器就会导致，类加载被吞掉）

---

## 运行时数据区

![{00F57237-57F8-433D-9E66-074B6F0120A0}](https://gitee.com/s420/image-bed/raw/master/img/{00F57237-57F8-433D-9E66-074B6F0120A0}.png)
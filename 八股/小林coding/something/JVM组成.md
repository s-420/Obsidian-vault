## 类加载子系统

简述：将字节码文件加载进入内存

![{60F457EA-EF79-442D-83A2-B8866765D8EA}](https://gitee.com/s420/image-bed/raw/master/img/{60F457EA-EF79-442D-83A2-B8866765D8EA}.png)

#### 工作流程：

- 加载
- 链接
  - 验证：验证待加载的class文件是否正确
  - 准备：为static变量分配内存并赋零值
  - 解析：将类的全域名解析为类在方法区中的地址
- 初始化
  - 为变量赋实际值

#### 类加载器的分类：

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

#### Tomcat为什么要加载自定义类加载器

![{35856DE9-31DA-4531-9CDD-6904A11E6974}](https://gitee.com/s420/image-bed/raw/master/img/{35856DE9-31DA-4531-9CDD-6904A11E6974}.png)

​	对于Tomcat来说，如果直接使用AppClassLoader加载器即同一个加载器实例，就会导致，若tomcat上的三个应用都要加载了一个相同类名的类，此时当已有其中一个类加载器被加载后，剩下的类加载器就不会被加载了；所以需要通过自定义类加载器，来处理自己对引得类，**就可以保证类加载的隔离**（由因：JVM判断一个类是否被加载的逻辑，类名+对应类加载器实例，多个app公用一个类加载器就会导致，类加载被吞掉）

---

## 运行时数据区

![{00F57237-57F8-433D-9E66-074B6F0120A0}](https://gitee.com/s420/image-bed/raw/master/img/{00F57237-57F8-433D-9E66-074B6F0120A0}.png)

- 线程私有：java方法栈、本地方法站、程序计数器

- 线程公有：方法区、堆

#### 程序计数器

![{46AA3D83-D268-4AF9-BAF9-26FFBB948354}](https://gitee.com/s420/image-bed/raw/master/img/{46AA3D83-D268-4AF9-BAF9-26FFBB948354}.png)

#### 虚拟机栈

![{A0C1C202-C6E5-41B9-9201-1BFA80A24CB1}](https://gitee.com/s420/image-bed/raw/master/img/{A0C1C202-C6E5-41B9-9201-1BFA80A24CB1}.png)

![{593C9EA9-B84E-4B94-9BDB-78B493CB4D0E}](https://gitee.com/s420/image-bed/raw/master/img/{593C9EA9-B84E-4B94-9BDB-78B493CB4D0E}.png)

- 虚拟机栈会在方法执行的开始和结束，自动入栈出栈，不需要垃圾回收器回收
- StackOverflowError：虚拟机栈空间大小已经确定，线程执行方法嵌套过多，虚拟机栈内存空间不够，放不下栈帧
- OutOfMermoryError：线程太多，线程创建是没有足够的内存区创建虚拟机栈

##### 栈帧

![{F8FCDFCC-C7C7-4169-9117-7073E4695234}](https://gitee.com/s420/image-bed/raw/master/img/{F8FCDFCC-C7C7-4169-9117-7073E4695234}.png)

**操作数栈**

- 定义：执行字节码指令过程中用来进行计算的区域

**局部变量表**

- 定义：在编译时，方法中局部变量被编译到字节码文件中，栈帧中存储了局部变量表

![{5811565F-E230-42BD-8FC3-9E64D3CB90B8}](https://gitee.com/s420/image-bed/raw/master/img/{5811565F-E230-42BD-8FC3-9E64D3CB90B8}.png)

- bipush：将值压入操作数栈
- istore-index：将栈底数据存入局部变量表（index处）
- iload-index：从局部变量表中读取index处的变量值
- iadd：加法

#### 本地方法栈

![{FDFE2460-19FE-4ECA-8681-A7F330F32D53}](https://gitee.com/s420/image-bed/raw/master/img/{FDFE2460-19FE-4ECA-8681-A7F330F32D53}.png)

### 堆

- 所有的对象实例和地址，都该放在堆中
- 栈帧中有对象引用的地址
- 方法执行完（栈帧释放），对象实例不会立马被回收
- JVM后台执行GC（垃圾回收器），对象才会被回收

![{2EEDEA28-F93F-4BD0-94B1-8567423DEA9B}](https://gitee.com/s420/image-bed/raw/master/img/{2EEDEA28-F93F-4BD0-94B1-8567423DEA9B}.png)

![{ACA4C57C-5FC9-4B36-8026-6FF5F3027320}](https://gitee.com/s420/image-bed/raw/master/img/{ACA4C57C-5FC9-4B36-8026-6FF5F3027320}.png)

![{5963D0EA-1B6D-479B-9E05-9241A3428298}](https://gitee.com/s420/image-bed/raw/master/img/{5963D0EA-1B6D-479B-9E05-9241A3428298}.png)

- 新生代：刚刚创建的一些新对象

- 老年代：经过了多次垃圾回收之后仍然存在的对象

  ![{BAF2E5E1-0DD6-4502-AE93-81C09B443CDE}](https://gitee.com/s420/image-bed/raw/master/img/{BAF2E5E1-0DD6-4502-AE93-81C09B443CDE}.png)

![{79AE29D2-C836-4221-BBE4-6F1240580077}](https://gitee.com/s420/image-bed/raw/master/img/{79AE29D2-C836-4221-BBE4-6F1240580077}.png)

- Eden：新创建的对象都会先存放在Eden区
  - Eden区被放满后，触发YGC（新生代的垃圾回收），找到Edan区的垃圾对象（局部对象没有再使用了）
- S0：首次被垃圾回收检验筛选过后存活下来的对象（记录被垃圾回收过一次）
  - YGC之后，剩下的对象会被存放到S0区，并记录已经被垃圾回收检验过一次

- S1：第二次被垃圾回收器校验筛选后存活下来的对象（经历过两次垃圾回收，记录被垃圾回收过两次）
  - 后续又创建新的对象又将Eden区存满了，再次进行垃圾回收（S0区也会被垃圾回收器校验），校验通过后被存放到S1区，并记录已经被垃圾回收校验过两次

> 在YGC的过程中，没有被垃圾回收器回收的对象，不断地重复这个过程（从S0到S1，从S1到S0）
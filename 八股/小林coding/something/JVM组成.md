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

## 堆

- 所有的对象实例和地址，都该放在堆中
- 栈帧中有对象引用的地址
- 方法执行完（栈帧释放），对象实例不会立马被回收
- JVM后台执行GC（垃圾回收器），对象才会被回收

![{2EEDEA28-F93F-4BD0-94B1-8567423DEA9B}](https://gitee.com/s420/image-bed/raw/master/img/{2EEDEA28-F93F-4BD0-94B1-8567423DEA9B}.png)

![{ACA4C57C-5FC9-4B36-8026-6FF5F3027320}](https://gitee.com/s420/image-bed/raw/master/img/{ACA4C57C-5FC9-4B36-8026-6FF5F3027320}.png)

![{5963D0EA-1B6D-479B-9E05-9241A3428298}](https://gitee.com/s420/image-bed/raw/master/img/{5963D0EA-1B6D-479B-9E05-9241A3428298}.png)

- ![{BAF2E5E1-0DD6-4502-AE93-81C09B443CDE}](https://gitee.com/s420/image-bed/raw/master/img/{BAF2E5E1-0DD6-4502-AE93-81C09B443CDE}.png)

![{79AE29D2-C836-4221-BBE4-6F1240580077}](https://gitee.com/s420/image-bed/raw/master/img/{79AE29D2-C836-4221-BBE4-6F1240580077}.png)

- 新生代：刚刚创建的一些新对象

  - Eden：新创建的对象都会先存放在Eden区
    - Eden区被放满后，触发YGC（新生代的垃圾回收），找到Edan区的垃圾对象（局部对象没有再使用了）
  - S0：首次被垃圾回收检验筛选过后存活下来的对象（记录被垃圾回收过一次）
    - YGC之后，剩下的对象会被存放到S0区，并记录已经被垃圾回收检验过一次

  - S1：第二次被垃圾回收器校验筛选后存活下来的对象（经历过两次垃圾回收，记录被垃圾回收过两次）
    - 后续又创建新的对象又将Eden区存满了，再次进行垃圾回收（S0区也会被垃圾回收器校验），校验通过后被存放到S1区，并记录已经被垃圾回收校验过两次

> 在YGC的过程中，没有被垃圾回收器回收的对象，不断地重复这个过程（从S0到S1，从S1到S0）

- 老年代：经过了多次垃圾回收之后仍然存在的对象

  - 当一个对象被垃圾回收器，检验了15次还没有被垃圾回收器回收，就放入老年代![{F4BA063E-B7B7-473D-A795-4142DC39BCB7}](https://gitee.com/s420/image-bed/raw/master/img/{F4BA063E-B7B7-473D-A795-4142DC39BCB7}.png)

  

  - 当一个较大的对象被创建后，可以在Eden区放得下，此时被YGC检验没有被回收（仅一次检验），不会进入S0、S1（因为这两个地方内存空间小，放不下），直接进入老年代空间![{4DA6296D-0E73-4DC6-A946-47E975B2FE4B}](https://gitee.com/s420/image-bed/raw/master/img/{4DA6296D-0E73-4DC6-A946-47E975B2FE4B}.png)

  - 当一个非常大的对象被创建后，Eden区也放不下这个对象，会直接放到老年代中![](https://gitee.com/s420/image-bed/raw/master/img/{5E0D6513-0585-4D5F-9B9A-845F8F4EA591}.png)

## 垃圾回收机制

**垃圾回收器的实现**

![{1C5066BF-3F63-4BBE-96DF-725AF0DD0353}](https://gitee.com/s420/image-bed/raw/master/img/{1C5066BF-3F63-4BBE-96DF-725AF0DD0353}.png)

- Young GC：负责新生代的垃圾回收
- Old GC：负责老年代的垃圾回收，除了CMS垃圾回收器会单独对老年代进行处理，其他垃圾回收器基本都是整堆回收的时候回收对老年代进行处理

- Full GC：整堆回收，**也会对方法区进行垃圾收集**

**为什么进行垃圾回收**

- 垃圾指的是JVM中没有**被任何引用指向它的对象**
- 如果不清理这些垃圾对象，他会一直占用着内存，从而不能给其他对象使用，垃圾越来越多，就会出现OOM（OutOfMermoryError）

### 垃圾回收算法

#### 垃圾标记阶段

找到垃圾对象的方法：

- 引用计数法![{DEC24779-A473-4891-8C9F-C9E1495D64BD}](https://gitee.com/s420/image-bed/raw/master/img/{DEC24779-A473-4891-8C9F-C9E1495D64BD}.png)
  - 记录当前对象被引用的次数
  - 缺点（不常用）
    - 需要额外的时间空间维护
    - **无法处理循环引用**
- 可达性分析法![{15EC7720-4EC9-4291-A99F-605DF5A765C5}](https://gitee.com/s420/image-bed/raw/master/img/{15EC7720-4EC9-4291-A99F-605DF5A765C5}.png)
  - GC Root 会”引用”对象，此对象还会应用其他对象，被引用的对象即使存活对象，**从未被引用**的对象即为垃圾对象
  - 简单来说就是，内存中 方法内 或 类 内部的一些 **静态属性/常量属性** 相关联 的对象引用 ![{845CD631-4338-4FB8-8003-2644D27B18C4}](https://gitee.com/s420/image-bed/raw/master/img/{845CD631-4338-4FB8-8003-2644D27B18C4}.png)

#### 标记-清除 算法

- 当模块内存空间不够用（新生代（Eden、S0、S1）、老年代），则会暂停线程执行（STW），随后执行垃圾回收
- 先标记找到可达对象，并进行标记；随后线性遍历，对没有标记的对象进行回收

![{E2C4440F-3E34-4183-ABD9-F1814E9E9B10}](https://gitee.com/s420/image-bed/raw/master/img/{E2C4440F-3E34-4183-ABD9-F1814E9E9B10}.png)

#### 复制算法

- 核心思想：空间换时间，使用两块内存空间
- 进行垃圾回收时，通过GC-Root直接找到科大对象，STW，随后若对象是可达的会将其复制到另一个内存空间
  - 非垃圾对象少时，复制成本会高，效率较低
  - 对象复制后，对象存放地址发生变化，需要额外的时间去修改栈帧中记录的引用地址

![{2D659506-B07C-4924-8DF4-9BF24286C718}](https://gitee.com/s420/image-bed/raw/master/img/{2D659506-B07C-4924-8DF4-9BF24286C718}.png)

#### 标记整理算法

![{A85A4E9E-E40C-40C3-B221-229C537A0E62}](https://gitee.com/s420/image-bed/raw/master/img/{A85A4E9E-E40C-40C3-B221-229C537A0E62}.png)

- 先标记可达对象，将所有可达对象移动到内存另一端
- 将边界之外的区域（非科大对象）进行清理
  - 步骤多效率低
  - 也需要改变栈帧中对 对象实例的引用

#### 对比总结

![{9838EE17-48C0-4F8D-B7E5-7FB967184DEF}](https://gitee.com/s420/image-bed/raw/master/img/{9838EE17-48C0-4F8D-B7E5-7FB967184DEF}.png)

#### 分代收集算法（理念）

对不同的对象采用不同的垃圾回收算法

![{268C02E3-E245-44F1-9563-42909007CD57}](https://gitee.com/s420/image-bed/raw/master/img/{268C02E3-E245-44F1-9563-42909007CD57}.png)

### 垃圾回收器

- JDK8：默认Parallel GC
- JDK9：默认G1

![{C125AA4C-8036-43FC-B3B4-20EC9D578009}](https://gitee.com/s420/image-bed/raw/master/img/{C125AA4C-8036-43FC-B3B4-20EC9D578009}.png)

#### Parllel GC & Parllel Old GC

![{A8042094-6003-4E5C-9060-A6FD625A889F}](https://gitee.com/s420/image-bed/raw/master/img/{A8042094-6003-4E5C-9060-A6FD625A889F}.png)

#### CMS GC（ConcMarkSweepGC）

并发标记清除垃圾回收器（并发导致吞吐量减少）

![{C357E289-5108-4D16-84F6-89C1D83E6FD3}](https://gitee.com/s420/image-bed/raw/master/img/{C357E289-5108-4D16-84F6-89C1D83E6FD3}.png)![{A0AE99B9-7796-45BB-8822-82482ED51B49}](https://gitee.com/s420/image-bed/raw/master/img/{A0AE99B9-7796-45BB-8822-82482ED51B49}.png)

- 初始标记：STW，利用GC Root去找到**直接可达**的对象
- 并发标记：与用户线程，并发标记找到**所有可达**的对象
  - 与用户线程并发标记时，用户标记的操作可能会改变对象的 **可用状态**，可以用**三色标记法**来解决

![](https://gitee.com/s420/image-bed/raw/master/img/{C96E4B61-E238-4074-933E-B4ECE5CE71FD}.png)

- 重新标记：STW，解决并发标记带来的 可用**状态可能被改变**的误差 
- 并发清理：与用户线程，并发执行，清理垃圾对象
- 并发重置：重置 可用标记

总结，将 简单的 标记清理算法 最费时间的 标记 和 清理 两个阶段，让其与 用户线程 并发执行 极大的减少了时间，并通过 初始标记（标记可直达对象）快速标记对象，重新标记（解决 对象可用状态 因 并发 产生影响）等操作，在保证绝大多数 垃圾对象能被正确回收的情况下，极大的节省时间消耗（STW 时间很短）。

![{DC2CC692-4858-4FC7-B7C0-75FE4D6E70D8}](https://gitee.com/s420/image-bed/raw/master/img/{DC2CC692-4858-4FC7-B7C0-75FE4D6E70D8}.png)

- 并发标记 并发清理的过程中，新的对象要进到 老年代 但老年代的空间不够，会先调用 Serial Old做一下来集会收（全局 STW） CMS相当于见缝插针 整体减少时间消耗，但若 新对象无法创建 就会全局停止，清理老年代完成后 再继续
- 并发清理过程中，可能会产生 新的垃圾对象，只能交由下一次垃圾回收处理（并发提高效率，时间短，因此新的垃圾对象较少）
- CMS 因采用的时标记清楚算法，所以会产生内存碎片，通过参数 可以 对内存空间进行整理

#### G1 （Garbage-First）

将堆空间分作很多小region，分区依然存在 Eden、S0、S1、老年代，但物理上不是连续的了，逻辑上依然连续

- HUmongous ：专门存储大对象的区域（对象大小超过 一个region的一半）

![{2BDD6221-AF14-4376-9F6D-FE24657BE7FD}](https://gitee.com/s420/image-bed/raw/master/img/{2BDD6221-AF14-4376-9F6D-FE24657BE7FD}.png)

![{AD1F528B-500A-4A40-B4A4-3F8822FF86B5}](https://gitee.com/s420/image-bed/raw/master/img/{AD1F528B-500A-4A40-B4A4-3F8822FF86B5}.png)

- 初始标记：STW，根据 GC Root 去找到直接 可用的对象
- 并发标记：和 用户线程 一起工作 找到所有 可用对象
- 最终标记：STW，主要是为了 标记 在并发标记中 可用态转变了的对象
- 筛选回收：STW，
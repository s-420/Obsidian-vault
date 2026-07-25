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
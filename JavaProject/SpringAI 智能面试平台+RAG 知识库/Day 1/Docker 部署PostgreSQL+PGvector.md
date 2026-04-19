[[2.本地搭建 PostgreSQL + PGvector 向量数据库.pdf]]
样例：
``` plain
docker run -d \
	--name my_pgvector \
	-p 5432:5432 \ 
	-e POSTGRES_PASSWORD=123456 \ 
	-v /Users/guide/docker/postgresql/data:/var/lib/postgresql/data\
	pgvector/pgvector:pg17
```
后台启动一个带有向量扩展（pgvector）的 PostgreSQL 17 数据库容器

命令拆分解释：
1.`docker run -d`：
- `docker run`是Docker最常用的命令，用于创建一个新的容器并运行一个命令
- `-d `（detached）：意思是”后台运行“ 如果不加这个参数，容器的运行日志会直接占据你的终端窗口，一旦按下 `Ctrl + C`或者关闭终端，容器通常会停止。加上`-d`后，容器会在后台静默运行
2.`--name my_pgvector`：
- 自定义容器名称
- 有了名字就可以  通过其他命令对该容器进行操作`docker stop my_pgvector`
3.`-p 5432:5432`:
- 端口映射，格式为 `宿主机端口：容器内端口`
- PostgreSQL默认在容器内部监听 `5432` 端口。通过这个映射，可以通过访问电脑（宿主机）的localhost：5432 来连接容器中的数据库
4.`-e POSTGRES_PASSWORD=123456`：设置 默认超级用户 postgres 的的登陆密码。实际应用下可以使用复杂的随机字符串
5.`-v /Users/guide/docker/postgresql/data:/var/lib/postgresql/data\`
- 挂载数据卷（Volume），格式为 `宿主机绝对路劲:容器内路径`
- 用于 **数据持久化**
- 容器时一个“临时“的环境，删除容器会导致内部数据丢失。通过 映射来实现持久化，数据库产生的所有数据会实时写入到 指定的路径 **磁盘中** 。即使删除了容器，下次挂载这个目录（只要你指向的是**同一个宿主机路径**（即 `D:/Code/docker/postgresql/data`），Docker 就会自动加载该目录中已有的数据库文件，恢复所有数据和配置。）数据依然存在。
6.`pgvector/pgvector:pg17`:指定使用的镜像名和标签（Tag) (仓库名/镜像名:标签)

本机：
~~~ text 
docker run -d \
  --name my_pgvector \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=123456 \
  -v D:/Code/docker/postgresql/data:/var/lib/postgresql/data \
  pgvector/pgvector:pg17

~~~

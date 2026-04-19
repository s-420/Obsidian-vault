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

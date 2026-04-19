样例：
``` plain
docker run -d \
	--name my_pgvector \
	-p 5432:5432 \ 
	-e POSTGRES_PASSWORD=123456 \ 
	-v /Users/guide/docker/postgresql/data:/var/lib/postgresql/data\
	pgvector/pgvector:pg17
```

命令拆分解释：
1.`docker run -d`：
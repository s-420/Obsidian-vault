# Spring Task 定时任务

## 概述

Spring Task 是 Spring 框架提供的任务调度模块，支持注解式的定时任务配置，无需额外依赖（如 Quartz）。

## 核心注解

### @EnableScheduling

在启动类上添加，启用定时任务支持。

```java
@SpringBootApplication
@EnableScheduling
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### @Scheduled

在方法上添加，配置定时任务执行规则。

```java
@Component
public class MyTask {
    
    @Scheduled(fixedDelay = 10000)  // 固定延迟 10 秒
    public void task1() {
        // 任务逻辑
    }
    
    @Scheduled(fixedRate = 5000)  // 固定频率 5 秒
    public void task2() {
        // 任务逻辑
    }
    
    @Scheduled(cron = "0 0/30 * * * ?")  // cron 表达式
    public void task3() {
        // 任务逻辑
    }
}
```

## 执行规则

### fixedDelay（固定延迟）

- 上一次任务执行完成后，等待指定时间再执行下一次
- 适合耗时不确定的任务
- 避免任务重叠执行

### fixedRate（固定频率）

- 上一次任务开始后，间隔指定时间执行下一次
- 即使上一次任务未完成，也会按频率触发
- 可能导致任务重叠

### cron 表达式

- 支持复杂的调度规则
- 格式：`秒 分 时 日 月 周`
- 示例：
  - `0 0/30 * * * ?` - 每 30 分钟
  - `0 0 2 * * ?` - 每天凌晨 2 点
  - `0 0 8 ? * MON-FRI` - 工作日早上 8 点

## 实际案例：课程过期检查

### 需求

定期检查 `learning_lesson` 表中的课程是否过期，如果过期则将课程状态修改为已过期。

### 实现

#### 1. Service 接口

```java
public interface ILearningLessonService extends IService<LearningLesson> {
    /**
     * 更新过期课程状态
     */
    void updateExpiredLessons();
}
```

#### 2. Service 实现

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class LearningLessonServiceImpl extends ServiceImpl<LearningLessonMapper, LearningLesson> 
        implements ILearningLessonService {

    @Override
    public void updateExpiredLessons() {
        // 1 查询已过期但状态不是已过期的课程
        LambdaQueryWrapper<LearningLesson> wrapper = new LambdaQueryWrapper<LearningLesson>()
                .lt(LearningLesson::getExpireTime, LocalDateTime.now())
                .ne(LearningLesson::getStatus, LessonStatus.EXPIRED.getValue());
        List<LearningLesson> expiredLessons = list(wrapper);
        if (CollUtils.isEmpty(expiredLessons)) {
            log.debug("没有需要更新的过期课程");
            return;
        }
        // 2 批量更新状态为已过期
        List<LearningLesson> updates = expiredLessons.stream()
                .map(lesson -> new LearningLesson()
                        .setId(lesson.getId())
                        .setStatus(LessonStatus.EXPIRED.getValue()))
                .collect(Collectors.toList());
        updateBatchById(updates);
        log.info("已更新{}条过期课程状态", updates.size());
    }
}
```

#### 3. 定时任务类

```java
@Slf4j
@Component
@RequiredArgsConstructor
public class LessonExpirationTask {

    private final ILearningLessonService lessonService;

    /**
     * 每小时检查一次过期课程
     */
    @Scheduled(fixedDelay = 3600000)
    public void checkExpiredLessons() {
        log.debug("开始检查过期课程");
        try {
            lessonService.updateExpiredLessons();
            log.debug("过期课程检查完成");
        } catch (Exception e) {
            log.error("检查过期课程时发生异常", e);
        }
    }
}
```

## 代码规范

### 1. 包结构

```
com.tianji.learning/
├── task/              # 定时任务包
│   └── LessonExpirationTask.java
├── service/           # 服务层
│   ├── ILearningLessonService.java
│   └── impl/
│       └── LearningLessonServiceImpl.java
└── ...
```

### 2. 命名规范

- 定时任务类：`XxxTask`
- Service 接口：`IXxxService`
- Service 实现：`XxxServiceImpl`

### 3. 日志规范

- 使用 `@Slf4j` 注解
- 关键操作记录 `info` 级别日志
- 调试信息记录 `debug` 级别日志
- 异常记录 `error` 级别日志

### 4. 异常处理

- 定时任务必须捕获异常，避免任务中断
- 记录异常日志，便于排查问题

```java
@Scheduled(fixedDelay = 3600000)
public void checkExpiredLessons() {
    try {
        lessonService.updateExpiredLessons();
    } catch (Exception e) {
        log.error("检查过期课程时发生异常", e);
    }
}
```

## 注意事项

1. **线程安全**：Spring Task 默认使用单线程执行所有定时任务，高并发场景需配置线程池
2. **任务重叠**：使用 `fixedDelay` 避免任务重叠执行
3. **异常处理**：务必捕获异常，避免任务中断
4. **日志记录**：记录关键操作和异常，便于排查问题
5. **数据库操作**：批量更新时注意事务管理

## 相关链接

- [[Spring Boot CRUD Patterns]]
- [[MyBatis Plus 使用指南]]
- [[天机学堂项目架构]]

---

*创建时间：2026-06-05*
*关联任务：课程过期检查定时任务*

# NullPointerException - queryOldRecord 传入 null

## 错误信息

```
java.lang.NullPointerException: null
    at com.tianji.learning.utils.LearningRecordDelayTaskHandler$RecordRedisData.<init>(LearningRecordDelayTaskHandler.java:130)
    at com.tianji.learning.utils.LearningRecordDelayTaskHandler.writeRecordCache(LearningRecordDelayTaskHandler.java:90)
    at com.tianji.learning.service.impl.LearningRecordServiceImpl.queryOldRecord(LearningRecordServiceImpl.java:162)
    at com.tianji.learning.service.impl.LearningRecordServiceImpl.handlerVideoRecord(LearningRecordServiceImpl.java:106)
    at com.tianji.learning.service.impl.LearningRecordServiceImpl.addlearningRecord(LearningRecordServiceImpl.java:72)
```

## 错误原因

### 问题代码

```java
private LearningRecord queryOldRecord(Long lessonId, Long sectionId) {
    // 1 先查询缓存
    LearningRecord record = taskHandler.readRecordCache(lessonId, sectionId);
    if (record != null) {
        return record;
    }
    // 2 若不存在则查询数据库
    record = lambdaQuery().eq(LearningRecord::getLessonId, lessonId)
            .eq(LearningRecord::getSectionId, sectionId)
            .one();
    if (record == null) {
        log.info("数据库中不存在学习记录，lessonId：{}，sectionId：{}", lessonId, sectionId);
        // ❌ 问题在这里！没有 return null，继续往下执行了
    }
    // 3 写入缓存（record 为 null 时会 NPE！）
    taskHandler.writeRecordCache(record);  // ❌ 传入了 null
    // 4 返回学习记录
    return record;
}
```

### 根本原因

1. **方法职责混乱**：`queryOldRecord` 应该只做查询，但实际却尝试写入缓存
2. **缺少 null 检查**：当数据库中不存在记录时，没有 `return null`，继续往下执行
3. **防御性编程不足**：`writeRecordCache` 没有对入参进行 null 检查

### 调用链

```
addlearningRecord
  └─> handlerVideoRecord
       └─> queryOldRecord
            └─> writeRecordCache(record)  // record 为 null
                 └─> new RecordRedisData(record)  // NPE！
```

## 修复方案

```java
private LearningRecord queryOldRecord(Long lessonId, Long sectionId) {
    // 1 先查询缓存
    LearningRecord record = taskHandler.readRecordCache(lessonId, sectionId);
    if (record != null) {
        return record;
    }
    // 2 若不存在则查询数据库
    record = lambdaQuery().eq(LearningRecord::getLessonId, lessonId)
            .eq(LearningRecord::getSectionId, sectionId)
            .one();
    if (record == null) {
        log.info("数据库中不存在学习记录，lessonId：{}，sectionId：{}", lessonId, sectionId);
        return null;  // ✅ 直接返回 null，让调用方决定是否新增
    }
    // 3 写入缓存（只有 record 不为 null 时才写入）
    taskHandler.writeRecordCache(record);
    // 4 返回学习记录
    return record;
}
```

## 经验教训

### 1. 方法职责要单一

- **查询方法**：只负责查询，返回 `null` 表示不存在
- **新增方法**：只负责新增
- **更新方法**：只负责更新

不要在一个方法中混合多种职责。

### 2. 防御性编程

```java
// ❌ 错误：没有检查 null
taskHandler.writeRecordCache(record);

// ✅ 正确：先检查 null
if (record != null) {
    taskHandler.writeRecordCache(record);
}
```

### 3. 注意代码逻辑完整性

当 `if (record == null)` 时，一定要考虑：
- 是否需要 `return`？
- 后续代码是否会受到影响？
- 是否需要 `else` 分支？

### 4. 单元测试的重要性

如果写了单元测试，这种 `null` 传入的问题很容易被发现：

```java
@Test
public void testQueryOldRecord_NotExist() {
    // 模拟数据库中不存在记录
    when(recordMapper.selectOne(any())).thenReturn(null);
    
    LearningRecord result = service.queryOldRecord(1L, 1L);
    
    assertNull(result);  // 应该返回 null
    // 不应该调用 writeRecordCache
    verify(taskHandler, never()).writeRecordCache(any());
}
```

## 相关链接

- [[NullPointerException 常见原因]]
- [[Java 防御性编程]]
- [[单元测试最佳实践]]

---

*创建时间：2026-06-05*
*错误类型：NullPointerException*
*严重程度：高*

---
title: MyBatis-Plus分页查询流程
tags: [MyBatis-Plus, 分页查询, SpringBoot]
created: 2026-05-28
updated: 2026-05-28
status: 100%
related: [[ThreadLocal跨服务用户传递]]
---

# MyBatis-Plus 分页查询流程

## 1. 业务场景与核心诉求

实现分页查询用户课表接口：`GET /lessons/page`，需要：
- 根据当前用户过滤数据
- 支持分页参数（pageNo, pageSize）
- 支持排序（按最近学习时间倒序）
- 远程调用其他服务补充数据

## 2. 最终落地方案 & 核心代码

### 2.1 分页参数封装

```java
@Data
public class PageQuery {
    @Min(value = 1, message = "页码不能小于1")
    private Integer pageNo = 1;

    @Min(value = 1, message = "每页查询数量不能小于1")
    private Integer pageSize = 20;

    private Boolean isAsc = true;
    private String sortBy;

    // 转换为 MyBatis-Plus 的 Page 对象
    public <T> Page<T> toMpPage(String defaultSortBy, boolean isAsc) {
        if (StringUtils.isBlank(sortBy)) {
            sortBy = defaultSortBy;
            this.isAsc = isAsc;
        }
        Page<T> page = new Page<>(pageNo, pageSize);
        OrderItem orderItem = new OrderItem();
        orderItem.setAsc(this.isAsc);
        orderItem.setColumn(sortBy);
        page.addOrder(orderItem);
        return page;
    }
}
```

### 2.2 分页查询实现

```java
@Override
public PageDTO<LearningLessonVO> queryMyLesson(PageQuery query) {
    // 1. 获取用户ID
    Long userId = UserContext.getUser();

    // 2. 分页查询
    Page<LearningLesson> page = lambdaQuery()
            .eq(LearningLesson::getUserId, userId)
            .page(query.toMpPage("latest_learn_time", false));

    // 3. 提取课程ID
    List<Long> courseIds = page.getRecords().stream()
            .map(LearningLesson::getCourseId)
            .collect(Collectors.toList());

    // 4. 远程调用获取课程信息
    List<CourseSimpleInfoDTO> courseInfoList = 
            courseClient.getSimpleInfoList(courseIds);

    // 5. 合并数据
    Map<Long, CourseSimpleInfoDTO> courseMap = courseInfoList.stream()
            .collect(Collectors.toMap(CourseSimpleInfoDTO::getId, c -> c));

    List<LearningLessonVO> voList = new ArrayList<>();
    for (LearningLesson record : page.getRecords()) {
        LearningLessonVO vo = BeanUtils.copyBean(record, LearningLessonVO.class);
        CourseSimpleInfoDTO course = courseMap.get(record.getCourseId());
        vo.setCourseName(course.getName());
        vo.setCourseCoverUrl(course.getCoverUrl());
        vo.setSections(course.getSectionNum());
        voList.add(vo);
    }

    return PageDTO.of(page, voList);
}
```

### 2.3 返回值封装

```java
@Data
public class PageDTO<T> {
    private Long total;  // 总记录数
    private Long pages;  // 总页数
    private List<T> list; // 数据列表

    public static <T> PageDTO<T> of(Page<?> page, List<T> list) {
        return new PageDTO<>(page.getTotal(), page.getPages(), list);
    }
}
```

## 3. 原理剖析与踩坑记录

### 3.1 MyBatis-Plus 分页原理

```sql
-- 逻辑代码
SELECT * FROM learning_lesson 
WHERE user_id = ? 
ORDER BY latest_learn_time DESC 
LIMIT ?, ?

-- 实际执行
-- 1. 先查总数
SELECT COUNT(*) FROM learning_lesson WHERE user_id = ?
-- 2. 再查分页数据
SELECT * FROM learning_lesson WHERE user_id = ? ORDER BY latest_learn_time DESC LIMIT 0, 20
```

### 3.2 关键点

| 要点 | 说明 |
|------|------|
| 分页插件 | 需要配置 `MybatisPlusInterceptor` + `PaginationInnerInterceptor` |
| 自动 count | 默认会执行 count 查询，可通过 `page.setSearchCount(false)` 关闭 |
| 排序字段 | 使用数据库字段名，不是 Java 属性名 |

### 3.3 踩坑记录

**坑1：分页插件未配置**
```java
@Bean
public MybatisPlusInterceptor mybatisPlusInterceptor() {
    MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
    interceptor.addInnerInterceptor(new PaginationInnerInterceptor());
    return interceptor;
}
```

**坑2：跨服务查询 N+1 问题**
- ❌ 循环中逐个调用远程服务
- ✅ 先收集所有 ID，批量查询，再用 Map 合并

**坑3：远程服务返回空**
- 需要判断 `CollUtils.isEmpty(courseInfoList)`
- 空结果直接返回空 PageDTO

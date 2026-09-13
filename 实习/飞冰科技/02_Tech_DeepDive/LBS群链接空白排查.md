---
title: 技术专题：LBS 群链接打开空白的排查与修复
date: 2026-09-09
status: draft
tags:
  - 实习/飞冰科技
  - TechDeepDive
tech_stack:
  - Java
  - React
ai_agent_context: 本篇沉淀飞冰 LBS 群图片链接（group-img）打开空白的完整排查链路：链接生成机制、subType/posterId 参数核验方法、同名分类干扰的根因谱系与修正方案，可用于回答 LBS 链接类客诉的定位路径。
---

# LBS 群链接打开空白的排查与修复

## 背景与动机

从 2026-09-09 茶瀑布客诉提炼：客户拿到一条 LBS 群图片链接，打开后页面无数据。排查过程中发现「同名分类」干扰项，且链接生成机制、分类数据挂载方式两层都有认知偏差，值得沉淀一条标准排查链路。

## 链接结构与参数含义

```text
https://connect.feibing.tech/lbs/#/pages/lbs/group-img/index
  ?sid={商户ID}          # account.seller.id
  &type=GROUP            # 对象类型：群
  &subType={分类ID}      # 分享时选中的分类 catalogId，未选分类时为 default（未分类）
  &posterId={海报ID}     # LBS_POSTER 类型的海报模板内容 ID
```

链接由管理后台「桌台管理 → 群列表」的分享弹窗**纯前端拼接**（`group-list/index.tsx` 的 `checkShare`）：

```typescript
let link = `https://connect.feibing.tech/lbs/#/pages/lbs/group-img/index?sid=${getSellerId()}&type=GROUP&subType=${catalogId || 'default'}`
if (data?.shopTypeRange == "1") link += `&shopId=${getShopId()}`   // 限定门店
if (data?.posterId) link += `&posterId=${data.posterId}`           // 海报样式
if (data?.qrcodeTypeRange == "0") link += `&groupLink=true`        // 入群码模式
```

**关键点**：`catalogId || 'default'` —— 没选中分类 Tab 就点分享，`subType` 落到 `default`（未分类）。

## 排查方法（API 核验链路）

三个只读接口即可定位问题，无需翻页面：

```bash
# 1. 列出该商户全部分类（subType 的合法取值来源）
GET /sc/v1/sellers/{sid}/catalogs?type=GROUP

# 2. 数每个分类下实际有多少群（分类 ID 是否有数据）
GET /sc/v1/sellers/{sid}/places?type=GROUP&catalogId={分类ID}
#    可加 keyword 按群名过滤

# 3. 核验海报归属/类型/状态（三个条件都截图在返回里）
GET /sc/v1/sellers/{sid}/contents/{posterId}
#    校验 type=LBS_POSTER、status=PUBLISHED、sellerId 与链接 sid 一致
```

排查决策树：

```mermaid
flowchart TD
    A[LBS 链接打开空白] --> B{contents/{posterId} 返回?}
    B -->|404/NOT_FOUND| B1[海报不存在/已删/归属其他商户]
    B -->|type ≠ LBS_POSTER| B2[海报类型错误]
    B -->|status ≠ PUBLISHED| B3[海报未发布]
    B -->|正常| C{places?catalogId=subType 有数据?}
    C -->|total=0| C1[subType 指向空分类：未选分类落 default，或分类下没挂群]
    C -->|有数据| D[检查 shopId/tid 等附加过滤参数]
```

## 根因谱系（本次案例）

两层原因叠加：

### 1. 分享时未选分类（直接原因）

坏链接 `subType=default`。生成那一刻没选中任何分类 Tab，前端空状态落到 `default`（未分类），而该商户未分类下 **0 条群**。

### 2. 误建同名分类（干扰项，已删）

海报名「茶瀑布线下TV」、群名也都叫「线下TV」，于是有人按字面建了一个同名**分类**——但「线下TV」实际是**群的名称**，2027 条群全部挂在「市场部」分类下。这个同名分类从未挂过群（0 条），后来被删除，排查时徒增混淆。

### 时间线还原

1. 09-08 建「市场部」分类 + 「茶瀑布线下TV」海报（同批配置）
2. 群批量挂到市场部分类下（每店一条，群名「线下TV」）
3. 误建同名「线下TV」分类（后删）
4. 分享链接时未选分类 → `subType=default` → 页面无数据

## 修正方案

把 `subType` 换成实际挂群的分类 ID（市场部 `6a9fb4bf48416029d91bafbb`，2027 条群）：

```text
https://connect.feibing.tech/lbs/#/pages/lbs/group-img/index?sid={sid}&type=GROUP&subType=6a9fb4bf48416029d91bafbb&posterId=6a9fb4adcd9fe9067f4ee1ae
```

**预防**：分享前先点选目标分类 Tab；生成后抽查链接里 `subType` 不是 `default`。

## 踩坑记录

**坑1：把群名当成分类名**
群（place）的 `catalog` 字段是单值精确匹配（`catalog.eid`），查询不做子级展开。同名 ≠ 同物：「线下TV」是群名，分类叫「市场部」。排查时先 `places?catalogId=X` 数一遍，别按名字想当然。

**坑2：default 是合法值但可能是空分类**
`subType=default` 不会报错，页面正常渲染，只是无数据。判断链接好坏不能只看格式，必须核验分类下有无数据。

**坑3：分类会被删除，历史链接中的 ID 不会失效提示**
本次排查中曾出现过一个同名分类，核验时已删。旧链接引用已删分类同样表现为空白，需重新确认当前分类列表。

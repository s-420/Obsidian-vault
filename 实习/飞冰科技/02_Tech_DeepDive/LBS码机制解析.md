---
title: 技术专题：飞冰互联 LBS 码机制解析（是什么/内部逻辑/实现效果）
date: 2026-09-11
status: draft
tags:
  - 实习/飞冰科技
  - TechDeepDive
tech_stack:
  - Java
  - Node.js
  - 企业微信
ai_agent_context: 本篇解析飞冰互联 LBS 码的完整机制：LBS 码=名为「LBS」的特殊群桌台码，扫码经 redirect/lbs 随机分跳 10 个 H5 实例按分类展示群活码；三条内部链路（创建同步链/批量换链链/C 端消费链）与门店 metadata.groupLink 的一致性约定。可用于回答 LBS 码类客诉定位与换链运维决策。
---

# 飞冰互联 LBS 码机制解析

## 一、LBS 码是什么

**一句话**：LBS 码不是一个独立的码种，它是**门店下名为「LBS」的特殊桌台（Place）生成的二维码**——本质是「群活码的物理载体」。

判定逻辑在 `PlaceService._groupLinkSyncShop`（vinci-sc, L277）：

```java
if (StrUtil.equals(place.getType(), PlaceType.GROUP.getCode())
        && StrUtil.equals("LBS", place.getName())) {
```

即 `type=GROUP` 且 `name="LBS"` 的桌台才会触发 LBS 专属逻辑。**严格定性**（`PlaceType` 枚举，vinci-sc `domain/place/PlaceType` L21-27）：地点共 7 类——DESK 桌台 / PAY 支付贴牌 / SINGLE / CHANNEL 渠道 / GROUP 群码 / ACTIVITY 活动码 / ROOM 包厢。两类码的本质区别在「回答的问题」：DESK 回答**客人坐在哪张桌**（空间定位，数量=桌位数，正餐店可批量建上百个、奶茶店可 0～1 个），GROUP 回答**客人从哪个入口来**（投放归因）。

**数量口径（重要修正）**：名叫「LBS」的那一个同步码一店一个，这是**业务约定而非系统强制约束**——建店流标配创建，但系统不校验唯一性；GROUP 群码类本身可按投放开无限个（不同活动/物料位/产品线各一个码，指向可以相同或不同的群）。实际客户「有很多 LBS 码」即指此；API 的 `types` 过滤参数里 LBS 已与 GROUP 并列（`门店-批量对齐-全渠道客服.js` L91 `types: 'DESK,SINGLE,CHANNEL,GROUP,LBS'`）。**群码分类（catalog）存在的根本原因**：码一多必须归堆——管理侧按 catalogId 圈批量范围，C 端落地页按 subType 分 Tab 展示。与「门店号」并列的标配地位有统计佐证：报表按 `contactName = 门店号 / LBS` 分别拉数（SellerService L2546/L2559）。

它的二维码内容来自桌台的欢迎语配置 `metadata.contact.welMsg`，附件（attachments）里挂着一条 `https://work.weixin.qq.com/gm/` 开头的**企微入群链接**（L282）。这张码印刷在海报、桌贴等物理场景，客户扫码后落到 LBS H5 落地页选群入群。**它存在的根本理由**：企微群码是易碎品（7 天过期/满员失效/解散重建），印死群码意味着每换一次群就要重印全量物料；LBS 码是印在物料上的「永久招牌」——群随便换，后台改链接指向即可，物料永不重印。

**命名陷阱**：叫 LBS（Location Based Service）但**代码里没有任何按地理位置路由的逻辑**——「lbs 跳转」做的是随机分流，不是 GPS 找最近门店。真正做地理围栏的是 AC 活动侧的「强制 LBS」领券半径（默认 50km，`ActivityService.java` L341-347），两套机制同名不同物，排查时不要混。

## 二、内部逻辑：三条链路

### 链路 A：创建/更新同步链（LBS 码 → 门店 groupLink）

新建或更新名为 LBS 的群桌台时，后端自动做一次「链接回填」（`PlaceService._groupLinkSyncShop`，L275-304，create/update 都调用）：

1. 解析桌台 `metadata.contact` 里的欢迎语附件，找到第一条 `work.weixin.qq.com/gm/` 链接（L281-286）；
2. 与门店 `metadata.groupLink` 比对，不一致则**用 LBS 码的链接覆盖门店 groupLink**（L294-297）；
3. 异常只记日志不阻断建桌台（L301-303）。

效果：**LBS 码是门店入群链接的一致性源头之一**——桌台码欢迎语、门店号、欢迎语批量链接三者不打架，靠的就是这条同步。昨日分析「门店入群链接 vs 桌台欢迎语链接一致性」的代码落点即此（一致性日志：L3970 `lbsLink:%s shopGroupLink:%s`）。

### 链路 B：批量换链链（运维高频，活码思想的核心价值）

- 后端入口：`SellerPlaceResource`（L566-587）两个接口——按桌台 id 换单码、按门店 id 换整店；实现为 `PlaceService.updateLbsLink(id, link)`（L3678）与 `updateLbsLink(sellerId, shopId, link)`（L3709，查出门店下全部 LBS 码逐个改，L3713-3730）。
- 脚本驱动：`feibing-ops/scripts/sc/桌台-批量更换-LBS群链接.js`（高风险，默认 dryRun）——改的正是 `metadata.contact.welMsg.attachments` 中 `type=link` 的 `link` 字段，处理范围是门店下**所有**链接为 `work.weixin.qq.com/gm/` 的桌台与渠道码，带备份/回滚（`mode: replace | rollback`）与并发控制。
- 茶瀑布 09-10 的 38,514 条全渠道刷图，走的就是这类「改附件链接」路径：**群可以换，码不用重印**。

### 链路 C：C 端消费链（客户扫码 → 入群）

1. 客户扫 LBS 码 → 附件链接指向的入口经 `vinci-ac` 的 `redirect/lbs`（`WxAuthResource.lbsOpt`，L34-45，`@IgnoreAuth`）；
2. 该接口**随机取 0-9** 拼出 `https://connect.feibing.tech/lbs{0-9}/#/pages/lbs/group-img/index` 并 302 跳转——10 个 H5 部署实例做负载分散，附原始 query + `time` 时间戳（L40-42）；
3. H5 落地页按参数渲染群活码图片列表，参数结构（沉淀自 [[LBS群链接空白排查]]）：

```text
?sid={商户ID}&type=GROUP&subType={分类ID|default}&posterId={海报ID}
  [&shopId={门店ID}]   // shopTypeRange=="1" 时限定门店
  [&groupLink=true]    // qrcodeTypeRange=="0" 入群码模式
```

4. 客户点选群活码图 → 加入企微福利群。

外围配套：`CheckAliEcsHealth.getLbsInfo/notifyLbs`（L521/L347）对 LBS 页面做 pv/uv/queryCount 统计并推飞书；`OpenApiResource`（L359-371）把门店 LBS 二维码（`metadata.preQrCode`）按 tc/sms/order/delivery 四场景字段暴露给外部系统。

## 三、实现效果

| 效果 | 机制支撑 |
| --- | --- |
| 一张码承载「客户 → 门店福利群」最短路径 | 桌台欢迎语附件挂企微群活码链接 |
| 群换链不重印物料（活码思想） | 附件链接可被 updateLbsLink / 脚本批量替换，支持备份回滚 |
| 桌台码、门店号、欢迎语链接不打架 | `_groupLinkSyncShop` 用 LBS 码链接覆盖门店 groupLink，单一事实源 |
| 高可用抗单点 | redirect/lbs 随机分跳 lbs0-lbs9 十个 H5 实例 |
| 一套 H5 服务全部商户、可配样式 | 参数化 sid/subType(catalog)/shopId/posterId |
| 可观测 | CheckAliEcsHealth 统计 pv/uv 推飞书 |

## 四、已知坑与排查入口

1. **页面空白**：分享/生成链接时未选分类 → `subType=default` → 未分类下 0 条群。核验三接口：`catalogs?type=GROUP` → `places?type=GROUP&catalogId=` → `contents/{posterId}`（详见 [[LBS群链接空白排查]] 决策树）。
2. **同名分类干扰**：分类/群/海报三者同名时按字面理解会认错对象，以 ID 为准。
3. **换链一致性**：批量换 LBS 码链接后，门店 `groupLink` 不会自动跟随脚本直改（同步只发生在走后端 create/update 时）——直改附件后需核对门店 groupLink 是否要一并更新，否则桌台码与门店号指向旧群。
4. **redirect 随机分流的观测副作用**：同参数两次扫码可能落到不同实例，排查时注意 `time` 时间戳与实例编号（lbs0-9）差异。

## 五、代码锚点索引

| 逻辑 | 位置 |
| --- | --- |
| LBS 桌台判定 + groupLink 同步 | vinci-sc `PlaceService._groupLinkSyncShop` L275-304（调用点 L267/L313） |
| 单码/整店换链 | vinci-sc `PlaceService.updateLbsLink` L3678/L3709；REST `SellerPlaceResource` L566-587 |
| C 端跳转分流 | vinci-ac `WxAuthResource.lbsOpt` L34-45 |
| 门店 LBS 二维码开放字段 | vinci-ac `OpenApiResource` L359-371 |
| LBS 页面统计 | vinci-ac `CheckAliEcsHealth` L347/L521 |
| 批量换链脚本 | feibing-ops `scripts/sc/桌台-批量更换-LBS群链接.js`（dryRun/备份/回滚） |
| 渠道码导出（含 LBS 码入群链接） | feibing-ops `scripts/sc/渠道码-导出-LBS码.js` |
| 链接参数结构与空白排查 | [[LBS群链接空白排查]] |

## Changelog

- v1 2026-09-11 初版：基于 feibing-project/backend 与 feibing-ops 代码实证（行号见锚点索引）。

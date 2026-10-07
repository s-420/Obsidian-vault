# JEnv for Windows 操作指南

> 适用对象：本机通过 Scoop 安装的 `jenv`（jenv-for-windows），用于多 JDK 版本管理与目录级自动切换。
> 记录日期：2026-09-29

## 一、基本概念

- jenv 管理的是**已注册的 JDK 清单** + **全局默认版本** + **目录级固定版本**
- jenv 通过修改 `PATH` / `JAVA_HOME` 环境变量实现切换，**改全局版本后需要新开终端才生效**
- ⚠️ 关键限制：jenv 切换目录版本靠启动时的 PATH 注入，**已经打开的终端不会自动跟随目录切换**——进入新目录后如果 `java -version` 不对，重开终端即可

## 二、常用命令

### 1. 查看所有已注册版本

```powershell
jenv list
```

输出两段：`All available versions`（全局+注册清单）和 `All locally specified versions`（哪些目录固定了哪个版本）。本机当前清单：

| 名称 | 路径 |
|---|---|
| jdk8 | `~\scoop\apps\temurin8-jdk\current` |
| jdk11 | `D:\Java\jdk-11.0.17` |
| jdk17 | `D:\Java\jdk-17` |
| jdk21 | `D:\Java\jdk-21` |

### 2. 切换全局默认版本

```powershell
jenv change jdk21    # 全局切到 JDK 21
```

修改的是用户级 `JAVA_HOME` 和 PATH，**对已开终端无效，新开终端生效**。当前全局默认是 `jdk17`。

### 3. 当前目录固定版本（最常用）

```powershell
cd D:\Code\feibing\feibing-project\backend\vinci-sc
jenv local jdk8      # 本目录固定 JDK 8
```

- 固定关系保存在 jenv 自己的配置文件里（不在项目目录生成 dotfile），**不要提交到 git，也不会影响同事**
- 取消当前目录的固定：

```powershell
jenv local remove
```

取消后该目录回落到全局版本。

### 4. 注册 / 删除版本

```powershell
# 注册新 JDK（path 指向 JDK 根目录，即 bin 的上级）
jenv add jdk25 "D:\Java\jdk-25"

# 删除注册
jenv remove jdk25
```

> 具体子命令以 `jenv help` 输出为准；`add/remove` 少用，本机 4 个版本已配齐。

## 三、验证切换是否生效

```powershell
java -version                              # 看 java 命令
echo $env:JAVA_HOME                        # mvnw/gradle 用的是这个
(Get-Command java).Source                  # 确认走的不是 Oracle javapath
```

在 vinci-sc 目录下（新终端）应看到 `java -version` 为 `1.8.0_504`。

## 四、Maven/Gradle 注意事项（重要）

jenv 主要接管 `java` 命令，但 **`mvnw` 读的是 `JAVA_HOME`**。在固定了 jdk8 的目录里，如果 `JAVA_HOME` 还指向 jdk17，Maven 仍会用 17 编译。稳妥做法——编译前显式设置：

```powershell
$env:JAVA_HOME = "$env:USERPROFILE\scoop\apps\temurin8-jdk\current"
.\mvnw.cmd clean compile
.\mvnw.cmd spring-boot:run "-Dspring-boot.run.profiles=dev"
```

## 五、常见问题

| 现象 | 原因 / 处理 |
|---|---|
| `jenv` 命令找不到 | 当前终端是旧 PATH，**重开终端**；确认 `~\scoop\shims` 在用户 PATH 里 |
| 目录固定了但 `java -version` 不对 | 终端是进入目录前开的，PATH 没刷新；重开终端 |
| 提示 "需要管理员权限修改环境变量" | 首次全局切换时的提示，按需允许；不提权则只改当前会话变量 |
| `jenv.ps1` 第 61 行 Get-Command 报错 | 会话初始化时序问题，不影响 list/change/local 功能，重开终端后消失 |
| mvnw 编译用了错误的 JDK | 手动设 `$env:JAVA_HOME`（见第四节） |
| 切换后 IDEA 里版本没变 | IDEA 的 Project SDK 在 IDE 设置里独立管理，不归 jenv 管，需在 `File → Project Structure → SDK` 单独选 |

## 六、本机当前状态速查

- 全局默认：`jdk17`
- vinci-sc 固定：`jdk8`（Temurin 8u504）
- PATH 已清理：Oracle javapath / java8path / 各 JDK bin 直连均已移除，java 统一走 jenv
- 查看固定关系：`jenv list` 输出的第二段 `All locally specified versions`

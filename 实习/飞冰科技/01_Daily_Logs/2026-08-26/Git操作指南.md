# Git 操作指南

> 适用项目：`web-wework-connect`  
> 远程仓库别名：`web-wework-connect`  
> 开发分支：`dev`

## 1. 三个核心概念

- **本地仓库**：你电脑上的项目和 Git 记录。
- **远程仓库**：Codeup 服务器上的项目。
- **分支**：一条独立的开发线，本项目当前使用 `dev`。

`web-wework-connect` 是远程仓库在本地的别名，`dev` 是分支名。

## 2. 首次获取项目

如果电脑上还没有项目，在目标父目录执行：

```powershell
git clone -b dev git@codeup.aliyun.com:5ff9ca92168c689c9272ccd5/feibing_front/web-wework-connect.git web-wework-connect
cd web-wework-connect
```

如果已有本地仓库，且已配置远程别名：

```powershell
git fetch web-wework-connect
git switch -c dev --track web-wework-connect/dev
```

## 3. 查看当前状态

```powershell
git status
git branch -vv
git remote -v
```

- `git status`：查看当前分支和已修改文件。
- `git branch -vv`：查看本地分支及其跟踪的远程分支。
- `git remote -v`：查看远程别名和地址。

## 4. 每天开始工作

先确认分支，再拉取最新代码：

```powershell
git switch dev
git status
git pull
```

`git pull` 会下载远程更新，并合并到当前分支。如果本地有未提交修改，建议先提交或暂存。

## 5. 提交代码

### 5.1 查看修改

```powershell
git status
git diff
```

### 5.2 将文件加入暂存区

添加指定文件：

```powershell
git add src/path/file.ts
```

添加当前目录下所有修改：

```powershell
git add .
```

执行 `git add .` 前应先用 `git status` 确认没有误加无关文件。

### 5.3 创建提交

```powershell
git commit -m "feat: 新增某项功能"
```

常见提交类型：

- `feat`：新功能。
- `fix`：修复问题。
- `docs`：文档修改。
- `refactor`：重构。
- `style`：格式调整，不改变逻辑。
- `chore`：构建、工具或其他杂项。

### 5.4 推送到 Codeup

```powershell
git push
```

如果是新建的本地分支，第一次推送可使用：

```powershell
git push -u web-wework-connect 分支名
```

## 6. 推荐的日常完整流程

```powershell
git switch dev
git pull
git status

# 编写代码后
git diff
git add .
git status
git commit -m "feat: 描述本次改动"
git push
```

## 7. 使用独立功能分支

团队若不允许直接在 `dev` 开发，可先从最新 `dev` 创建分支：

```powershell
git switch dev
git pull
git switch -c feat/功能名
```

完成开发后：

```powershell
git add .
git commit -m "feat: 描述功能"
git push -u web-wework-connect feat/功能名
```

然后在 Codeup 上创建合并请求，将功能分支合并到 `dev`。

## 8. `fetch` 和 `pull` 的区别

```powershell
git fetch web-wework-connect
```

只下载远程信息，不修改当前工作文件，适合安全查看远程更新。

```powershell
git pull
```

下载更新并合并到当前分支，会影响当前代码。

## 9. 暂时保存未提交修改

需要临时切换分支时：

```powershell
git stash push -m "临时保存"
```

恢复修改：

```powershell
git stash pop
```

查看暂存列表：

```powershell
git stash list
```

## 10. 常见报错

### 10.1 Host key verification failed

先手动验证 SSH 主机：

```powershell
ssh -T git@codeup.aliyun.com
```

核对 Codeup 主机指纹后输入 `yes`。出现以下内容代表 SSH 连接和账号权限正常：

```text
Welcome to Codeup, 用户名!
```

### 10.2 Permission denied (publickey)

表示 SSH 公钥未添加到 Codeup，或 Git 使用了错误的私钥。

### 10.3 推送被拒绝

如果远程分支已有新提交，先拉取再推送：

```powershell
git pull --rebase
git push
```

如果出现冲突，不要盲目覆盖，先确认冲突文件并请求团队成员协助。

### 10.4 No such branch: main

表示仓库不存在名为 `main` 的本地分支。本项目使用 `dev`，可执行：

```powershell
git switch dev
```

## 11. 操作前的安全检查

执行提交、拉取或切换分支前，建议先运行：

```powershell
git status
```

不确定时，避免使用下列可能丢失代码的命令：

```text
git reset --hard
git clean -fd
git push --force
```

这些命令可能删除未提交修改或覆盖远程历史，应在明确理解影响后使用。

## 12. 快速命令表

| 目的 | 命令 |
| --- | --- |
| 查看状态 | `git status` |
| 查看分支 | `git branch -vv` |
| 查看远程仓库 | `git remote -v` |
| 切换到 `dev` | `git switch dev` |
| 拉取最新代码 | `git pull` |
| 查看修改 | `git diff` |
| 暂存所有修改 | `git add .` |
| 创建提交 | `git commit -m "描述"` |
| 推送代码 | `git push` |
| 查看提交历史 | `git log --oneline --graph --decorate -20` |

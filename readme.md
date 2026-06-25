# RuoYi Spider

一个基于 Playwright 的 Web 系统前端调研脚本，用于访问开源后台管理系统演示环境，自动采集页面截图、HTML、Network 请求记录，并生成 Markdown 调研报告初稿。

当前项目以 RuoYi-Vue 演示系统为调研对象，主要用于练习和验证以下工作流：

```text
访问系统前端
↓
手动登录
↓
自动访问核心页面
↓
监听接口请求
↓
保存页面截图和 HTML
↓
导出 network.json
↓
生成 report.md 调研报告
```

## 1. 项目目标

本项目用于辅助完成陌生 Web 系统的前端调研工作，重点关注：

* 页面结构采集
* 前端路由记录
* 接口请求监听
* 页面截图留档
* HTML 内容保存
* 自动生成 Markdown 报告初稿
* 初步推断系统业务流程

需要注意的是，本项目当前版本不是“全自动业务理解工具”，而是一个半自动化采集工具。脚本负责自动收集页面和接口信息，最终业务分析仍需要人工补充和确认。

## 2. 技术栈

* Python 3
* Playwright
* Chromium
* Markdown
* JSON

## 3. 项目结构

```text
ruoyi-spider/
├── main.py
├── outputs/
│   ├── screenshots/
│   │   ├── home.png
│   │   ├── system_user.png
│   │   ├── system_role.png
│   │   └── system_menu.png
│   ├── html/
│   │   ├── home.html
│   │   ├── system_user.html
│   │   ├── system_role.html
│   │   └── system_menu.html
│   ├── network.json
│   └── report.md
└── README.md
```

## 4. 环境准备

### 4.1 创建虚拟环境

```bash
python3 -m venv .venv
```

### 4.2 激活虚拟环境

macOS / Linux：

```bash
source .venv/bin/activate
```

Windows：

```bash
.venv\Scripts\activate
```

激活成功后，终端前面通常会出现：

```text
(.venv)
```

### 4.3 安装依赖

```bash
python -m pip install --upgrade pip
python -m pip install playwright
```

### 4.4 安装 Playwright 浏览器

```bash
python -m playwright install chromium
```

## 5. 运行方式

在项目根目录下执行：

```bash
python main.py
```

脚本启动后会自动打开 RuoYi-Vue 演示系统。

由于演示系统登录页包含验证码，当前版本采用半自动方式：

1. 脚本打开浏览器；
2. 用户手动完成登录；
3. 登录成功并进入首页后，回到终端按 Enter；
4. 脚本自动访问核心页面并采集信息。

当前自动访问的页面包括：

| 页面名称 | 路由             | 说明                             |
| ---- | -------------- | ------------------------------ |
| 首页   | `/index`       | 系统首页，展示系统介绍、技术选型和更新日志          |
| 用户管理 | `/system/user` | 维护系统用户，包含用户查询、新增、修改、删除、部门筛选等功能 |
| 角色管理 | `/system/role` | 维护系统角色，角色用于承载菜单权限、按钮权限和数据权限    |
| 菜单管理 | `/system/menu` | 维护系统菜单、路由和按钮权限                 |

## 6. 输出文件说明

脚本运行结束后，会在 `outputs/` 目录下生成以下内容。

### 6.1 页面截图

目录：

```text
outputs/screenshots/
```

用于保存每个核心页面的完整截图。

示例：

```text
home.png
system_user.png
system_role.png
system_menu.png
```

### 6.2 页面 HTML

目录：

```text
outputs/html/
```

用于保存每个核心页面的 HTML 内容，便于后续分析页面结构和前端渲染结果。

### 6.3 Network 请求记录

文件：

```text
outputs/network.json
```

用于保存浏览器访问过程中的请求和响应记录。

记录内容包括：

* 请求方法
* 请求 URL
* 简化后的接口路径
* 请求类型
* 请求体
* 响应状态码
* 响应类型
* 请求时间

示例结构：

```json
{
  "event": "request",
  "method": "GET",
  "url": "https://vue.ruoyi.vip/prod-api/getInfo",
  "path": "/prod-api/getInfo",
  "resource_type": "xhr",
  "post_data": null,
  "time": "2026-06-25 17:12:24"
}
```

### 6.4 Markdown 调研报告

文件：

```text
outputs/report.md
```

报告内容包括：

* 调研对象
* 页面采集结果
* 接口请求清单
* 登录后初始化流程
* 用户管理流程推断
* 角色与权限流程推断
* 核心业务模型
* 待人工补充事项

## 7. 当前已采集的核心接口

当前版本可以采集到以下典型接口：

| 分类     | 接口                                                        | 作用                 |
| ------ | --------------------------------------------------------- | ------------------ |
| 登录     | `/prod-api/captchaImage`                                  | 获取验证码              |
| 登录     | `/prod-api/login`                                         | 用户登录               |
| 登录后初始化 | `/prod-api/getInfo`                                       | 获取当前登录用户信息、角色和权限标识 |
| 登录后初始化 | `/prod-api/getRouters`                                    | 获取当前用户可访问菜单和动态路由   |
| 用户管理   | `/prod-api/system/user/list`                              | 分页查询用户列表           |
| 用户管理   | `/prod-api/system/user/deptTree`                          | 获取用户管理左侧部门树        |
| 角色管理   | `/prod-api/system/role/list`                              | 分页查询角色列表           |
| 菜单管理   | `/prod-api/system/menu/list`                              | 查询菜单列表             |
| 字典数据   | `/prod-api/system/dict/data/type/...`                     | 获取状态、性别、显示隐藏等字典选项  |
| 系统参数   | `/prod-api/system/config/configKey/sys.user.initPassword` | 获取用户默认初始密码配置       |

## 8. 业务流程初步理解

通过当前采集结果，可以初步推断 RuoYi-Vue 的权限体系如下：

```text
部门 dept
  ↓
用户 user
  ├─ 绑定岗位 post
  └─ 绑定角色 role
          ├─ 菜单权限 menu
          ├─ 按钮权限 permission
          └─ 数据权限 dataScope
```

系统登录后的主要流程为：

```text
用户登录
↓
前端保存 token
↓
请求 /getInfo 获取用户信息、角色和权限标识
↓
请求 /getRouters 获取可访问菜单和动态路由
↓
前端根据路由树渲染左侧菜单
↓
前端根据权限标识控制按钮显示
```

## 9. 当前版本能力

当前 V1 版本支持：

* 打开目标系统
* 手动登录后继续采集
* 自动访问指定页面
* 监听页面 Network 请求
* 过滤静态资源请求
* 保存页面截图
* 保存页面 HTML
* 导出接口请求记录
* 自动生成 Markdown 报告初稿
* 对常见接口进行简单分类和作用推断

## 10. 当前版本局限

当前 V1 版本暂未实现：

* 自动登录
* 自动识别验证码
* 自动点击搜索、新增、修改、删除等按钮
* 自动展开角色权限树
* 自动保存接口响应 body
* 自动分析完整请求参数和响应字段
* 自动推断复杂业务流程

因此，当前生成的报告主要作为调研初稿，后续仍需要人工结合页面和接口内容进行补充。

## 11. 后续优化方向

后续 V2 可以考虑加入以下能力：

* 自动搜索用户，例如输入 `admin` 并点击搜索；
* 自动点击部门树节点，采集带 `deptId` 参数的用户列表接口；
* 自动打开新增用户弹窗，截图并记录初始化接口；
* 自动打开修改用户弹窗，采集用户详情接口；
* 自动进入角色管理，打开普通角色修改弹窗；
* 自动采集角色菜单权限树；
* 保存 JSON 响应 body，并对字段结构进行进一步分析；
* 对敏感字段进行脱敏，例如密码、token、cookie；
* 将报告中的接口说明从规则匹配升级为更完整的字段级说明。

## 12. 安全说明

当前项目仅用于学习、调研和授权范围内的系统分析。对于真实业务系统，应注意：

* 不要高频访问接口；
* 不要绕过权限控制；
* 不要提交删除、修改、强制下线等危险操作；
* 不要在日志或报告中明文保存密码、token、cookie 等敏感信息；
* 调研前应确认目标系统允许自动化访问。

## 13. 运行示例

```bash
source .venv/bin/activate
python main.py
```

运行完成后查看：

```bash
cat outputs/report.md
```

或直接在编辑器中打开：

```text
outputs/report.md
outputs/network.json
```

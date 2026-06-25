# RuoYi Spider

基于 Playwright 的 Web 系统前端调研脚本。

本项目以 RuoYi-Vue 演示系统为目标，用于练习通过浏览器自动化方式访问系统、监听接口请求、保存页面截图和 HTML，并生成 Markdown 调研报告初稿。

## 1. 项目说明

本项目主要完成以下工作：

* 手动调研 RuoYi-Vue 的核心页面和接口；
* 使用 Playwright 自动访问指定页面；
* 监听浏览器 Network 请求；
* 保存页面截图和 HTML；
* 导出接口请求记录 `network.json`；
* 生成调研报告 `report.md`。

当前版本为 V1，属于半自动化采集工具。登录部分仍需要手动完成，脚本负责登录后的页面访问和信息采集。

## 2. 技术栈

* Python
* Playwright
* Chromium
* Markdown
* JSON

## 3. 项目结构

```text
ruoyi-spider/
├── main.py
├── README.md
└── outputs/
    ├── screenshots/
    │   ├── home.png
    │   ├── system_user.png
    │   ├── system_role.png
    │   └── system_menu.png
    ├── html/
    │   ├── home.html
    │   ├── system_user.html
    │   ├── system_role.html
    │   └── system_menu.html
    ├── network.json
    └── report.md
```

## 4. 环境准备

创建虚拟环境：

```bash
python3 -m venv .venv
```

激活虚拟环境：

```bash
source .venv/bin/activate
```

安装依赖：

```bash
python -m pip install --upgrade pip
python -m pip install playwright
```

安装 Chromium：

```bash
python -m playwright install chromium
```

## 5. 运行方式

在项目根目录执行：

```bash
python main.py
```

运行后脚本会自动打开 RuoYi-Vue 演示系统。

操作流程：

1. 浏览器打开后，手动登录系统；
2. 登录成功进入首页后，回到终端按 Enter；
3. 脚本自动访问核心页面；
4. 脚本保存截图、HTML、接口日志和报告。

当前自动访问页面：

| 页面   | 路由             |
| ---- | -------------- |
| 首页   | `/index`       |
| 用户管理 | `/system/user` |
| 角色管理 | `/system/role` |
| 菜单管理 | `/system/menu` |

## 6. 输出说明

运行完成后，输出文件位于 `outputs/` 目录。

| 文件/目录                  | 说明              |
| ---------------------- | --------------- |
| `outputs/screenshots/` | 页面截图            |
| `outputs/html/`        | 页面 HTML         |
| `outputs/network.json` | Network 请求记录    |
| `outputs/report.md`    | Markdown 调研报告初稿 |

## 7. 手动调研接口记录

在写脚本前，先通过浏览器 DevTools 的 Network 面板手动观察了部分核心接口。

### 7.1 登录与初始化

| 接口                       | 方法   | 作用               |
| ------------------------ | ---- | ---------------- |
| `/prod-api/captchaImage` | GET  | 获取验证码            |
| `/prod-api/login`        | POST | 用户登录             |
| `/prod-api/getInfo`      | GET  | 获取当前用户信息、角色和权限标识 |
| `/prod-api/getRouters`   | GET  | 获取当前用户可访问菜单和动态路由 |

初步结论：

* 系统登录后会通过 token 鉴权；
* `/getInfo` 返回用户角色和权限标识；
* `/getRouters` 返回菜单和路由树；
* 前端根据返回的路由数据动态生成左侧菜单。

### 7.2 用户管理

| 接口                                                        | 方法  | 作用          |
| --------------------------------------------------------- | --- | ----------- |
| `/prod-api/system/user/list?pageNum=1&pageSize=10`        | GET | 分页查询用户列表    |
| `/prod-api/system/user/deptTree`                          | GET | 获取左侧部门树     |
| `/prod-api/system/dict/data/type/sys_normal_disable`      | GET | 获取正常/停用状态字典 |
| `/prod-api/system/dict/data/type/sys_user_sex`            | GET | 获取性别字典      |
| `/prod-api/system/config/configKey/sys.user.initPassword` | GET | 获取用户初始密码配置  |
| `/prod-api/system/user/2`                                 | GET | 获取指定用户详情    |

初步结论：

* 用户管理页面通过 `/system/user/list` 获取表格数据；
* 查询条件会拼接到用户列表接口参数中；
* 左侧部门树会通过 `deptId` 筛选用户；
* 修改用户时会请求用户详情，并回填部门、岗位和角色信息。

### 7.3 角色管理

| 接口                                                 | 方法  | 作用        |
| -------------------------------------------------- | --- | --------- |
| `/prod-api/system/role/list?pageNum=1&pageSize=10` | GET | 分页查询角色列表  |
| `/prod-api/system/role/2`                          | GET | 获取指定角色详情  |
| `/prod-api/system/menu/roleMenuTreeselect/2`       | GET | 获取角色菜单权限树 |

初步结论：

* 用户通过绑定角色获得权限；
* 角色中包含数据权限范围 `dataScope`；
* 角色修改弹窗中存在菜单权限树；
* 菜单权限树包含目录、菜单页面和按钮权限。

### 7.4 菜单管理

| 接口                                                   | 方法  | 作用          |
| ---------------------------------------------------- | --- | ----------- |
| `/prod-api/system/menu/list`                         | GET | 查询菜单列表      |
| `/prod-api/system/dict/data/type/sys_show_hide`      | GET | 获取显示/隐藏字典   |
| `/prod-api/system/dict/data/type/sys_normal_disable` | GET | 获取正常/停用状态字典 |

初步结论：

* 菜单管理用于维护系统目录、菜单页面和按钮权限；
* 菜单数据与动态路由、角色权限配置有关。

## 8. 业务流程初步理解

RuoYi-Vue 的权限链路可以初步理解为：

```text
菜单 / 按钮权限
↓
角色绑定菜单权限
↓
用户绑定角色
↓
用户登录后请求 getInfo 和 getRouters
↓
前端动态生成菜单并控制按钮权限
```

核心模型：

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

## 9. 当前版本能力

V1 版本支持：

* 打开目标系统；
* 手动登录后继续采集；
* 自动访问指定页面；
* 监听 Network 请求；
* 保存页面截图；
* 保存页面 HTML；
* 导出 `network.json`；
* 生成 `report.md` 初稿；
* 对常见接口进行简单分类和说明。

## 10. 当前版本局限

V1 版本暂未实现：

* 自动登录；
* 自动识别验证码；
* 自动点击搜索、新增、修改等按钮；
* 自动展开角色权限树；
* 自动保存接口响应 body；
* 自动分析完整业务流程。

因此，当前版本更适合作为系统调研的第一版采集工具，后续仍需要人工补充分析。

## 11. 后续优化方向

后续可以继续优化：

* 增加自动搜索用户；
* 增加自动部门筛选；
* 自动打开新增/修改弹窗；
* 自动采集角色权限树；
* 保存接口响应内容；
* 对密码、token、cookie 等敏感信息做脱敏处理。

## 12. 安全说明

本项目仅用于学习和授权范围内的系统调研。

真实业务系统中应注意：

* 不高频请求接口；
* 不绕过权限；
* 不执行删除、强制下线等危险操作；
* 不在日志中明文保存密码、token、cookie 等敏感信息。

# RuoYi-Vue 系统调研报告

## 1. 调研对象

- 前端地址：`https://vue.ruoyi.vip`
- 调研方式：Playwright 自动访问页面 + Network 请求监听 + 页面截图 + HTML 保存
- 调研目标：梳理系统页面结构、接口请求和核心业务流程

## 2. 页面采集结果

| 页面名称 | 路由 | 页面说明 | 截图 | HTML |
|---|---|---|---|---|
| 首页 | `/index` | 系统首页，展示系统介绍、技术选型和更新日志 | `outputs/screenshots/home.png` | `outputs/html/home.html` |
| 用户管理 | `/system/user` | 维护系统用户，包含用户查询、新增、修改、删除、部门筛选等功能 | `outputs/screenshots/system_user.png` | `outputs/html/system_user.html` |
| 角色管理 | `/system/role` | 维护系统角色，角色用于承载菜单权限、按钮权限和数据权限 | `outputs/screenshots/system_role.png` | `outputs/html/system_role.html` |
| 菜单管理 | `/system/menu` | 维护系统菜单、路由和按钮权限 | `outputs/screenshots/system_menu.png` | `outputs/html/system_menu.html` |

## 3. 接口请求清单

| 分类 | 方法 | 状态码 | 接口 | 初步作用 |
|---|---|---:|---|---|
| 其他 | GET | 200 | `/prod-api/captchaImage` | 待人工确认 |
| 其他 | POST | 200 | `/prod-api/login` | 待人工确认 |
| 登录后初始化 | GET | 200 | `/prod-api/getInfo` | 获取当前登录用户信息、角色和权限标识 |
| 登录后初始化 | GET | 200 | `/prod-api/getRouters` | 获取当前用户可访问菜单和动态路由 |
| 其他 | GET | 200 | `/prod-api/system/notice/listTop` | 待人工确认 |
| 字典数据 | GET | 200 | `/prod-api/system/dict/data/type/sys_user_sex` | 获取字典选项数据 |
| 用户管理 | GET | 200 | `/prod-api/system/user/deptTree` | 获取用户管理左侧部门树 |
| 字典数据 | GET | 200 | `/prod-api/system/dict/data/type/sys_normal_disable` | 获取字典选项数据 |
| 系统参数 | GET | 200 | `/prod-api/system/config/configKey/sys.user.initPassword` | 获取系统参数配置 |
| 用户管理 | GET | 200 | `/prod-api/system/user/list?pageNum=1&pageSize=10` | 分页查询用户列表 |
| 角色管理 | GET | 200 | `/prod-api/system/role/list?pageNum=1&pageSize=10` | 分页查询角色列表 |
| 字典数据 | GET | 200 | `/prod-api/system/dict/data/type/sys_show_hide` | 获取字典选项数据 |
| 菜单/权限管理 | GET | 200 | `/prod-api/system/menu/list` | 查询菜单列表 |

## 4. 登录后初始化流程

用户登录成功后，前端会携带 token 请求 `/prod-api/getInfo` 获取当前用户信息、角色和权限标识，再请求 `/prod-api/getRouters` 获取当前用户可访问的菜单和路由树。前端根据路由树动态渲染左侧菜单，并根据权限标识控制页面按钮显示。

## 5. 用户管理流程推断

用户管理页面用于维护系统登录用户。页面加载时会请求用户列表、部门树、字典数据和初始密码配置。管理员可以通过用户名、手机号、状态、创建时间、部门等条件筛选用户。点击新增用户时，系统初始化新增表单；点击修改用户时，系统根据用户 ID 请求用户详情，并回填用户基础信息、部门、岗位和角色。

## 6. 角色与权限流程推断

角色管理用于维护系统角色。用户通过绑定角色获得对应权限。角色编辑页面中的菜单权限树包含目录、菜单页面和按钮权限，例如用户查询、用户新增、用户修改、用户删除等。因此，若依权限体系可以理解为：用户绑定角色，角色绑定菜单和按钮权限，用户登录后系统根据角色返回可访问路由和权限标识。

## 7. 核心业务模型

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

## 8. 待人工补充

- 各接口的完整请求参数和响应字段说明
- 新增、修改、删除等写操作的具体请求体
- 普通角色与超级管理员的权限差异
- 菜单管理模块的字段结构和权限标识规则

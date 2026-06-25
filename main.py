from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
import json
import time


BASE_URL = "https://vue.ruoyi.vip"

OUTPUT_DIR = Path("outputs")
SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"
HTML_DIR = OUTPUT_DIR / "html"

for directory in [OUTPUT_DIR, SCREENSHOT_DIR, HTML_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


network_records = []
visited_pages = []


PAGES_TO_VISIT = [
    {
        "name": "首页",
        "route": "/index",
        "description": "系统首页，展示系统介绍、技术选型和更新日志"
    },
    {
        "name": "用户管理",
        "route": "/system/user",
        "description": "维护系统用户，包含用户查询、新增、修改、删除、部门筛选等功能"
    },
    {
        "name": "角色管理",
        "route": "/system/role",
        "description": "维护系统角色，角色用于承载菜单权限、按钮权限和数据权限"
    },
    {
        "name": "菜单管理",
        "route": "/system/menu",
        "description": "维护系统菜单、路由和按钮权限"
    },
]


def safe_filename(text: str) -> str:
    """把中文页面名或路由转为安全文件名。"""
    mapping = {
        "首页": "home",
        "用户管理": "system_user",
        "角色管理": "system_role",
        "菜单管理": "system_menu",
    }
    if text in mapping:
        return mapping[text]

    return (
        text.strip("/")
        .replace("/", "_")
        .replace("?", "_")
        .replace("&", "_")
        .replace("=", "_")
        .replace(":", "_")
        or "page"
    )


def is_static_resource(url: str) -> bool:
    """过滤 JS、CSS、图片、字体等静态资源。"""
    static_suffixes = [
        ".js", ".css", ".png", ".jpg", ".jpeg", ".gif",
        ".svg", ".ico", ".woff", ".woff2", ".ttf", ".map"
    ]
    path = urlparse(url).path.lower()
    return any(path.endswith(suffix) for suffix in static_suffixes)


def simplify_url(url: str) -> str:
    """把完整 URL 简化为 path + query，便于报告阅读。"""
    parsed = urlparse(url)
    result = parsed.path
    if parsed.query:
        result += "?" + parsed.query
    return result


def on_request(request):
    """记录请求。"""
    if is_static_resource(request.url):
        return

    network_records.append({
        "event": "request",
        "method": request.method,
        "url": request.url,
        "path": simplify_url(request.url),
        "resource_type": request.resource_type,
        "post_data": request.post_data,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
    })


def on_response(response):
    """记录响应。"""
    if is_static_resource(response.url):
        return

    content_type = response.headers.get("content-type", "")

    # 只重点记录 XHR/JSON/API 类请求，减少噪音
    if "application/json" not in content_type and "/prod-api/" not in response.url:
        return

    network_records.append({
        "event": "response",
        "status": response.status,
        "url": response.url,
        "path": simplify_url(response.url),
        "content_type": content_type,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
    })


def save_page_snapshot(page, page_info):
    """保存当前页面截图和 HTML。"""
    name = page_info["name"]
    filename = safe_filename(name)

    screenshot_path = SCREENSHOT_DIR / f"{filename}.png"
    html_path = HTML_DIR / f"{filename}.html"

    page.screenshot(path=str(screenshot_path), full_page=True)
    html_path.write_text(page.content(), encoding="utf-8")

    visited_pages.append({
        "name": name,
        "route": page_info["route"],
        "description": page_info["description"],
        "screenshot": str(screenshot_path),
        "html": str(html_path),
    })

    print(f"[保存页面] {name}")
    print(f"  截图: {screenshot_path}")
    print(f"  HTML: {html_path}")


def export_network_json():
    path = OUTPUT_DIR / "network.json"
    path.write_text(
        json.dumps(network_records, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"[导出] {path}")


def get_unique_api_responses():
    """从记录中提取去重后的接口响应。"""
    result = []
    seen = set()

    for record in network_records:
        if record.get("event") != "response":
            continue

        path = record.get("path", "")
        status = record.get("status", "")

        key = (path, status)
        if key in seen:
            continue
        seen.add(key)

        result.append(record)

    return result


def classify_api(path: str) -> str:
    """根据接口路径进行简单分类。"""
    if "/getInfo" in path or "/getRouters" in path:
        return "登录后初始化"
    if "/system/user" in path:
        return "用户管理"
    if "/system/role" in path:
        return "角色管理"
    if "/system/menu" in path:
        return "菜单/权限管理"
    if "/system/dept" in path:
        return "部门管理"
    if "/dict/data/type" in path:
        return "字典数据"
    if "/config/configKey" in path:
        return "系统参数"
    return "其他"


def guess_api_description(path: str) -> str:
    """根据路径粗略推断接口作用。"""
    if "/getInfo" in path:
        return "获取当前登录用户信息、角色和权限标识"
    if "/getRouters" in path:
        return "获取当前用户可访问菜单和动态路由"
    if "/system/user/list" in path:
        return "分页查询用户列表"
    if "/system/user/deptTree" in path:
        return "获取用户管理左侧部门树"
    if "/system/user/" in path and path.rstrip("/").split("/")[-1].isdigit():
        return "获取指定用户详情，用于修改用户表单回填"
    if path.rstrip("/").endswith("/system/user"):
        return "初始化新增用户表单或用户相关操作"
    if "/system/role/list" in path:
        return "分页查询角色列表"
    if "/system/role/" in path and path.rstrip("/").split("/")[-1].isdigit():
        return "获取指定角色详情"
    if "/system/menu/roleMenuTreeselect" in path:
        return "获取指定角色的菜单权限树"
    if "/system/menu/list" in path:
        return "查询菜单列表"
    if "/dict/data/type" in path:
        return "获取字典选项数据"
    if "/config/configKey" in path:
        return "获取系统参数配置"
    return "待人工确认"


def export_markdown_report():
    report_path = OUTPUT_DIR / "report.md"

    lines = []

    lines.append("# RuoYi-Vue 系统调研报告\n\n")

    lines.append("## 1. 调研对象\n\n")
    lines.append(f"- 前端地址：`{BASE_URL}`\n")
    lines.append("- 调研方式：Playwright 自动访问页面 + Network 请求监听 + 页面截图 + HTML 保存\n")
    lines.append("- 调研目标：梳理系统页面结构、接口请求和核心业务流程\n\n")

    lines.append("## 2. 页面采集结果\n\n")
    lines.append("| 页面名称 | 路由 | 页面说明 | 截图 | HTML |\n")
    lines.append("|---|---|---|---|---|\n")
    for page in visited_pages:
        lines.append(
            f"| {page['name']} | `{page['route']}` | {page['description']} | `{page['screenshot']}` | `{page['html']}` |\n"
        )

    lines.append("\n## 3. 接口请求清单\n\n")
    lines.append("| 分类 | 方法 | 状态码 | 接口 | 初步作用 |\n")
    lines.append("|---|---|---:|---|---|\n")

    # request 里有 method，response 里有 status；这里用 path 合并一下
    method_map = {}
    for record in network_records:
        if record.get("event") == "request":
            method_map[record["path"]] = record.get("method", "待确认")

    for record in get_unique_api_responses():
        path = record["path"]
        method = method_map.get(path, "待确认")
        category = classify_api(path)
        desc = guess_api_description(path)
        status = record.get("status", "")
        lines.append(f"| {category} | {method} | {status} | `{path}` | {desc} |\n")

    lines.append("\n## 4. 登录后初始化流程\n\n")
    lines.append(
        "用户登录成功后，前端会携带 token 请求 `/prod-api/getInfo` 获取当前用户信息、角色和权限标识，"
        "再请求 `/prod-api/getRouters` 获取当前用户可访问的菜单和路由树。"
        "前端根据路由树动态渲染左侧菜单，并根据权限标识控制页面按钮显示。\n\n"
    )

    lines.append("## 5. 用户管理流程推断\n\n")
    lines.append(
        "用户管理页面用于维护系统登录用户。页面加载时会请求用户列表、部门树、字典数据和初始密码配置。"
        "管理员可以通过用户名、手机号、状态、创建时间、部门等条件筛选用户。"
        "点击新增用户时，系统初始化新增表单；点击修改用户时，系统根据用户 ID 请求用户详情，"
        "并回填用户基础信息、部门、岗位和角色。\n\n"
    )

    lines.append("## 6. 角色与权限流程推断\n\n")
    lines.append(
        "角色管理用于维护系统角色。用户通过绑定角色获得对应权限。"
        "角色编辑页面中的菜单权限树包含目录、菜单页面和按钮权限，"
        "例如用户查询、用户新增、用户修改、用户删除等。"
        "因此，若依权限体系可以理解为：用户绑定角色，角色绑定菜单和按钮权限，"
        "用户登录后系统根据角色返回可访问路由和权限标识。\n\n"
    )

    lines.append("## 7. 核心业务模型\n\n")
    lines.append("```text\n")
    lines.append("部门 dept\n")
    lines.append("  ↓\n")
    lines.append("用户 user\n")
    lines.append("  ├─ 绑定岗位 post\n")
    lines.append("  └─ 绑定角色 role\n")
    lines.append("          ├─ 菜单权限 menu\n")
    lines.append("          ├─ 按钮权限 permission\n")
    lines.append("          └─ 数据权限 dataScope\n")
    lines.append("```\n\n")

    lines.append("## 8. 待人工补充\n\n")
    lines.append("- 各接口的完整请求参数和响应字段说明\n")
    lines.append("- 新增、修改、删除等写操作的具体请求体\n")
    lines.append("- 普通角色与超级管理员的权限差异\n")
    lines.append("- 菜单管理模块的字段结构和权限标识规则\n")

    report_path.write_text("".join(lines), encoding="utf-8")
    print(f"[导出] {report_path}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900}
        )
        page = context.new_page()

        page.on("request", on_request)
        page.on("response", on_response)

        print("[启动] 打开 RuoYi-Vue 演示系统")
        page.goto(BASE_URL, wait_until="networkidle")

        print("\n请在打开的浏览器中手动登录。")
        print("登录成功进入首页后，回到终端按 Enter。")
        input(">>> ")

        for page_info in PAGES_TO_VISIT:
            name = page_info["name"]
            route = page_info["route"]
            url = BASE_URL.rstrip("/") + route

            print(f"\n[访问页面] {name}: {url}")
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(1500)
            save_page_snapshot(page, page_info)

        export_network_json()
        export_markdown_report()

        print("\n[完成] 采集结束，请查看 outputs/report.md")
        browser.close()


if __name__ == "__main__":
    main()
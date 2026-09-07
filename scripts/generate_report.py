#!/usr/bin/env python3
"""
合成生物学干货周报 HTML 生成器（xiaohongshu-card / SynBio Digest）

由 xiaohongshu-card 技能（搜索模块）调用：把搜集筛选后的「纯干货」条目（知识科普/实验技巧/工具/方法学教程）
渲染为卡片式 HTML 周报。与 molecular-biology-weekly（新闻/资讯周报）共用同一套制作体验，但口径严格区分：
本文件产出为「干货周报」，不含行业动态/会议/广告。

用法:
  python generate_report.py <input.json> <output.html>

输入 JSON 格式:
{
  "title": "合成生物学干货周报 - 2026年第XX期",
  "date_range": "2026-09-01 至 2026-09-07",
  "items": [
    {
      "category": "质粒构建与载体设计",
      "category_key": "tools",
      "date": "2026-09-05",
      "title": "同源重组避坑干货手册",
      "summary": "3-5 句中文干货要点摘要...",
      "source": "优基生物 U&G Bio（公众号）",
      "url": "http://www.ugbio.cn/..."
    }
  ]
}

category_key 可选值:
  gene-editing, sequencing, protein, synbio, tools, rna, structure, other
"""

import json
import sys
import os
from datetime import datetime
from html import escape


# 分类映射: category_key -> (中文名, CSS class)
CATEGORY_MAP = {
    "gene-editing": ("基因编辑与基因治疗", "cat-gene-editing"),
    "sequencing":   ("测序与组学技术",   "cat-sequencing"),
    "protein":      ("蛋白质工程",       "cat-protein"),
    "synbio":       ("合成生物学",       "cat-synbio"),
    "tools":        ("分子工具与方法",   "cat-tools"),
    "rna":          ("RNA生物学",        "cat-rna"),
    "structure":    ("结构生物学",       "cat-structure"),
    "other":        ("其他",             "cat-other"),
}


def load_template():
    """加载 HTML 模板文件"""
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets", "report_template.html"
    )
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def generate_card_html(item):
    """生成单条资讯的卡片 HTML"""
    cat_key = item.get("category_key", "other")
    cat_name, cat_class = CATEGORY_MAP.get(cat_key, ("其他", "cat-other"))

    title = escape(item.get("title", "无标题"))
    summary = escape(item.get("summary", ""))
    source = escape(item.get("source", "未知来源"))
    url = item.get("url", "")
    date = escape(item.get("date", ""))

    # 标题链接
    if url:
        title_html = f'<a href="{escape(url)}" target="_blank" rel="noopener">{title}</a>'
        link_html = f'<a href="{escape(url)}" target="_blank" rel="noopener" class="card-link">阅读原文 →</a>'
    else:
        title_html = title
        link_html = ""

    return f'''<div class="card" data-category="{escape(cat_key)}">
  <div class="card-header">
    <span class="cat-badge {cat_class}">{escape(cat_name)}</span>
    <span class="card-date">{date}</span>
  </div>
  <div class="card-title">{title_html}</div>
  <div class="card-summary">{summary}</div>
  <div class="card-footer">
    <span class="card-source">{source}</span>
    {link_html}
  </div>
</div>'''


def generate_filter_tags(items):
    """生成分类筛选标签 HTML"""
    # 统计各分类出现次数
    cat_counts = {}
    for item in items:
        cat_key = item.get("category_key", "other")
        cat_counts[cat_key] = cat_counts.get(cat_key, 0) + 1

    tags_html = []
    for cat_key, (cat_name, _) in CATEGORY_MAP.items():
        if cat_key in cat_counts:
            count = cat_counts[cat_key]
            tags_html.append(
                f'<span class="filter-tag" onclick="filterCards(\'{cat_key}\')">'
                f'{escape(cat_name)} ({count})</span>'
            )

    return "\n    ".join(tags_html)


def generate_report(data):
    """填充模板生成最终 HTML"""
    template = load_template()

    items = data.get("items", [])

    # 生成卡片 HTML
    cards_html = "\n".join(generate_card_html(item) for item in items)
    if not items:
        cards_html = '<div class="empty">本周未收集到符合条件的资讯</div>'

    # 生成筛选标签
    filter_tags = generate_filter_tags(items)

    # 统计数据
    total_count = len(items)
    cat_count = len(set(item.get("category_key", "other") for item in items))
    source_count = len(set(item.get("source", "") for item in items))
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 替换占位符
    replacements = {
        "{{REPORT_TITLE}}": escape(data.get("title", "合成生物学干货周报")),
        "{{DATE_RANGE}}": escape(data.get("date_range", "")),
        "{{TOTAL_COUNT}}": str(total_count),
        "{{CAT_COUNT}}": str(cat_count),
        "{{SOURCE_COUNT}}": str(source_count),
        "{{FILTER_TAGS}}": filter_tags,
        "{{CARDS_HTML}}": cards_html,
        "{{GENERATED_AT}}": generated_at,
    }

    result = template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)

    return result


def main():
    if len(sys.argv) < 3:
        print("用法: python generate_report.py <input.json> <output.html>")
        print("  input.json  - 资讯数据 JSON 文件")
        print("  output.html - 输出的 HTML 报告路径")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # 读取 JSON 数据
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 生成报告
    html = generate_report(data)

    # 写入输出文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"报告已生成: {output_path}")
    print(f"  资讯总数: {len(data.get('items', []))} 条")
    print(f"  分类数量: {len(set(item.get('category_key', 'other') for item in data.get('items', [])))} 个")
    print(f"  来源数量: {len(set(item.get('source', '') for item in data.get('items', [])))} 个")


if __name__ == "__main__":
    main()

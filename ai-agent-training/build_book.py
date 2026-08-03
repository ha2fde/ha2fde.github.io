# -*- coding: utf-8 -*-
"""
把 integrated/slides 下七讲 HTML 合并为单文件《AI Agent 实战手册》book.html
核心处理：
  1. CSS 作用域隔离（各讲类名冲突：.slide/.head/.card 满天飞）
  2. vh/vw → px 换算（舞台固定 1280×720，视口单位会错位）
  3. 给每个 section 补 active 类（各讲靠 .slide.active 决定 display）
  4. 生成章扉页、书目录、连续页码、侧栏导航树
  5. 17 个配套脚本内嵌为附录，带语法高亮
"""
import io, os, re, html, json

ROOT = r"C:\Users\think\WorkBuddy\aippt8\integrated"
SLIDES = os.path.join(ROOT, "slides")
SCRIPTS = os.path.join(ROOT, "scripts")
OUT = os.path.join(ROOT, "book.html")

# ============================================================
# 一、章节元信息
# ============================================================
CHAPTERS = [
    dict(file="01-破冰指南.html", num="01", cn="一",
         title="破冰", sub="装上你的第一个 Agent",
         en="GETTING STARTED",
         lead="不讲原理，先让你今晚就能在自己电脑上跑起一个能干活的 Agent。"
              "壳（工具）和大脑（模型）是两回事——搞清这一点，剩下的都是配置问题。",
         who="全员 · 零基础", accent="#2563EB",
         secs=[(1,2,"开篇与导读"),(3,5,"破误解：Agent 是干活不是回答"),
               (6,8,"形态一：终端与编辑器里的 Agent"),
               (9,15,"大脑从哪来：云端 API 与本地部署"),
               (16,17,"形态二三：消息里与办公里的 Agent"),
               (18,21,"选型总表与 0 成本方案"),
               (22,24,"今晚就动手与总结")]),
    dict(file="02-从计算机到GPT.html", num="02", cn="二",
         title="前传", sub="大模型是怎么一步步长出来的",
         en="HOW LLM GREW",
         lead="一条因果链，不是概念清单。每一环都是为了解决上一环的痛而生——"
              "从 one-hot 的死胡同一路走到 Transformer 与缩放定律。",
         who="懂技术", accent="#0F766E",
         secs=[(1,2,"全篇地图：一条因果链"),
               (3,5,"机器怎么表示文字：one-hot 与 embedding"),
               (6,8,"怎么学会造句：n-gram → 神经网络 → RNN"),
               (9,12,"注意力机制与 Transformer"),
               (13,15,"预训练、微调与缩放定律"),
               (16,18,"递进小结与可运行实验")]),
    dict(file="03-ChatGPT是怎么工作的.html", num="03", cn="三",
         title="机制", sub="从接话机器到会干活的助手",
         en="HOW CHATGPT WORKS",
         lead="用 10 个真实困惑串起整个系统：生成、训练、上下文、采样、"
              "RAG、工具调用、协议、API——每一环都配一个能跑的脚本。",
         who="懂技术", accent="#7C3AED",
         secs=[(1,2,"10 个困惑总览"),
               (3,4,"生成机制：不是检索，是逐 token 预测"),
               (5,8,"训练与对齐：base / instruct、SFT、QLoRA"),
               (9,11,"上下文与记忆：它其实没有记忆"),
               (12,14,"采样、幻觉与思维链"),
               (15,16,"外部知识：RAG 检索增强"),
               (17,21,"工具调用与 MCP / CLI / Skills"),
               (22,24,"API 调用与全景回顾")]),
    dict(file="04-开发Agent.html", num="04", cn="四",
         title="开发", sub="从直接调 API 到用框架编排",
         en="BUILDING AGENTS",
         lead="整篇只有一条主线：抽象降级。省力的每一步，都在交出一点控制权——"
              "知道自己交出了什么，才谈得上选型。",
         who="开发者", accent="#B45309",
         secs=[(1,4,"主线：抽象降级与三条路线"),
               (5,8,"手写：裸 API → SDK → ReAct 主循环"),
               (9,10,"范式选择：ReAct vs Plan-and-Execute"),
               (11,15,"框架全景、总对比表与选型决策树"),
               (16,19,"落地 checklist 与可运行脚本")]),
    dict(file="05-Agent工程化全景.html", num="05", cn="五",
         title="工程化", sub="从能用到能信、能管、能连、能落地",
         en="ENGINEERING",
         lead="Demo 能跑不等于能上线。六大能力支柱、四层协议、Gartner 成熟度模型——"
              "这一章回答的是「凭什么敢把它放进生产」。",
         who="技术 + 管理者", accent="#0D9488",
         secs=[(1,3,"本章要回答的问题与三模块总览"),
               (4,11,"模块 A：六大能力支柱"),
               (12,18,"模块 B：四层协议生态与 MCP"),
               (19,23,"模块 C：企业落地与成熟度五级"),
               (24,26,"总结与落地评估速查表")]),
    dict(file="06-通往AGI之路.html", num="06", cn="六",
         title="收束", sub="通往 AGI 之路",
         en="ROAD TO AGI",
         lead="系列收束篇。前五章逐段展开的技术细节，在这里被串成一条主线："
              "计算终将战胜知识。中间两章是快速回顾，重点在序章与终章。",
         who="全员", accent="#4F46E5",
         secs=[(1,2,"本章定位与全篇地图"),
               (3,8,"序章 · 苦涩的教训"),
               (9,15,"Chat 的实现（回顾串讲）"),
               (16,21,"Agent 的实现（回顾串讲）"),
               (22,27,"终章 · 体验的时代")]),
    dict(file="07-资料索引.html", num="07", cn="七",
         title="深造", sub="大模型与 AI Agent 权威资料索引",
         en="REFERENCE INDEX",
         lead="23 条一手资料分 6 组，每条只写一句「为什么值得读」。"
              "本章不解释内容，它是查阅用的参考文献表。",
         who="全员", accent="#475569",
         secs=[(1,2,"怎么读这份索引"),
               (3,3,"第 1 组 · 大模型基础"),
               (4,5,"第 2 组 · Agent 范式"),
               (6,6,"第 3 组 · 工程架构"),
               (7,7,"第 4 组 · 协议生态"),
               (8,9,"第 5 组 · 落地实践"),
               (10,11,"第 6 组 · 课程路径与总览")]),
]

# ============================================================
# 二、CSS 作用域隔离
# ============================================================
def _block(css, open_idx):
    """从 open_idx（'{' 的位置）取出配对块，返回 (内容, 闭合后位置)"""
    depth, i, n = 0, open_idx, len(css)
    while i < n:
        c = css[i]
        if c == '/' and css.startswith('/*', i):
            j = css.find('*/', i + 2)
            i = n if j < 0 else j + 2
            continue
        if c in '"\'':
            q, i = c, i + 1
            while i < n and css[i] != q:
                i += 2 if css[i] == '\\' else 1
            i += 1
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return css[open_idx + 1:i], i + 1
        i += 1
    return css[open_idx + 1:], n


def _scope_selector(sel, scope):
    out = []
    for s in sel.split(','):
        s = s.strip()
        if not s:
            continue
        low = s.lower()
        if low in ('html', 'body', ':root', 'html body'):
            out.append(scope)
        elif low.startswith('body ') or low.startswith('html '):
            out.append(scope + ' ' + s.split(None, 1)[1])
        elif re.match(r'^(body|html)[.:\[#]', low):
            out.append(scope + s[4:] if low.startswith('body') else scope + s[4:])
        else:
            out.append(scope + ' ' + s)
    return ','.join(out)


def _conv_units(text):
    """舞台固定 1280×720：1vw=12.8px  1vh=7.2px  1vmin=7.2px  1vmax=12.8px"""
    def rep(m):
        v = float(m.group(1))
        u = m.group(2).lower()
        px = v * {'vw': 12.8, 'vh': 7.2, 'vmin': 7.2, 'vmax': 12.8}[u]
        return ('%.3f' % px).rstrip('0').rstrip('.') + 'px'
    return re.sub(r'(-?\d*\.?\d+)(vw|vh|vmin|vmax)\b', rep, text, flags=re.I)


def scope_css(css, scope, ap, drop_print=True):
    out, i, n = [], 0, len(css)
    while i < n:
        if css.startswith('/*', i):
            j = css.find('*/', i + 2)
            i = n if j < 0 else j + 2
            continue
        j = css.find('{', i)
        if j < 0:
            break
        pre = css[i:j]
        st = pre.strip()
        if st.startswith('@'):
            at = st.split(None, 1)[0].lower()
            body, end = _block(css, j)
            if at in ('@media', '@supports', '@layer', '@container'):
                if drop_print and 'print' in st.lower():
                    i = end
                    continue
                inner = scope_css(body, scope, ap, drop_print)
                if inner.strip():
                    out.append(pre + '{' + inner + '}')
            elif 'keyframes' in at:
                nm = st.split(None, 1)[1].strip() if ' ' in st else ''
                out.append(pre.replace(nm, ap + nm, 1) + '{' + _conv_units(body) + '}')
            else:
                out.append(pre + '{' + _conv_units(body) + '}')
            i = end
        else:
            body, end = _block(css, j)
            body = _conv_units(body)
            body = re.sub(r'(animation\s*:\s*)([a-zA-Z_][\w-]*)', r'\1' + ap + r'\2', body)
            body = re.sub(r'(animation-name\s*:\s*)([a-zA-Z_][\w-]*)', r'\1' + ap + r'\2', body)
            out.append(_scope_selector(pre, scope) + '{' + body + '}')
            i = end
    return '\n'.join(out)


# ============================================================
# 三、提取各讲内容
# ============================================================
SEC_RE = re.compile(r'<section[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>.*?</section>', re.S)


def extract(path):
    s = io.open(path, encoding='utf-8').read()
    styles = re.findall(r'<style(?![^>]*id="wb-shell-css")[^>]*>(.*?)</style>', s, re.S)
    css = '\n'.join(styles)
    secs = SEC_RE.findall(s)
    return css, secs


def sec_title(sec):
    body = re.sub(r'^<section[^>]*>|</section>$', '', sec)
    for pat in (r'<h1[^>]*>(.*?)</h1>', r'<h2[^>]*>(.*?)</h2>',
                r'class="[^"]*(?:slide-title|head|title)[^"]*"[^>]*>(.*?)<'):
        m = re.search(pat, body, re.S)
        if m:
            t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', m.group(1)))).strip()
            if t:
                return t
    return ''


def add_active(sec):
    """各讲靠 .slide.active 决定 display，合并后每页都要常显"""
    def rep(m):
        cls = m.group(1)
        return m.group(0) if 'active' in cls.split() else m.group(0).replace(cls, cls + ' active', 1)
    return re.sub(r'<section[^>]*class="([^"]*)"', rep, sec, count=1)


# ============================================================
# 四、脚本附录（含轻量 Python 高亮）
# ============================================================
PY_KW = set('False None True and as assert async await break class continue def del elif else except '
            'finally for from global if import in is lambda nonlocal not or pass raise return try '
            'while with yield match case self'.split())


def highlight_py(code):
    out, i, n = [], 0, len(code)
    while i < n:
        c = code[i]
        if c == '#':
            j = code.find('\n', i)
            j = n if j < 0 else j
            out.append('<span class="cm">' + html.escape(code[i:j]) + '</span>')
            i = j
        elif code.startswith('"""', i) or code.startswith("'''", i):
            q = code[i:i + 3]
            j = code.find(q, i + 3)
            j = n if j < 0 else j + 3
            out.append('<span class="st">' + html.escape(code[i:j]) + '</span>')
            i = j
        elif c in '"\'':
            j, q = i + 1, c
            while j < n and code[j] != q:
                if code[j] == '\\':
                    j += 1
                if code[j:j + 1] == '\n':
                    break
                j += 1
            j = min(j + 1, n)
            out.append('<span class="st">' + html.escape(code[i:j]) + '</span>')
            i = j
        elif c.isdigit():
            j = i
            while j < n and (code[j].isalnum() or code[j] == '.'):
                j += 1
            out.append('<span class="nu">' + html.escape(code[i:j]) + '</span>')
            i = j
        elif c.isalpha() or c == '_':
            j = i
            while j < n and (code[j].isalnum() or code[j] == '_'):
                j += 1
            w = code[i:j]
            if w in PY_KW:
                out.append('<span class="kw">' + w + '</span>')
            elif code[j:j + 1] == '(':
                out.append('<span class="fn">' + w + '</span>')
            else:
                out.append(html.escape(w))
            i = j
        else:
            out.append(html.escape(c))
            i += 1
    return ''.join(out)


SCRIPT_GROUPS = [
    ("lecture2", "第二章 · 从计算机到 GPT", [
        ("ngram_demo.py", "n-gram 语言模型：统计共现，看它为什么会崩"),
        ("embedding_demo.py", "词向量：把词义变成可计算的向量"),
        ("tiny_lm_train_demo.py", "迷你语言模型：几分钟训一个会续写的小网络"),
    ]),
    ("lecture3", "第三章 · ChatGPT 是怎么工作的", [
        ("tokenizer_demo.py", "分词：一句中文到底被切成几个 token"),
        ("sampling_demo.py", "采样：temperature / top-p 怎么改变输出"),
        ("training_stages_demo.py", "训练三阶段：预训练 → SFT → 对齐"),
        ("train_sft.py", "SFT 实战：loss masking 与 QLoRA 微调"),
        ("chat_context_demo.py", "上下文：多轮对话是怎么拼进 prompt 的"),
        ("cot_demo.py", "思维链：加一句「逐步思考」的效果对比"),
        ("rag_demo.py", "RAG：切分 → 向量化 → 检索 → 拼接"),
        ("agent_tool_demo.py", "工具调用：function calling 完整往返"),
        ("mcp_server.py", "MCP Server：最小可用实现"),
        ("mcp_skills_demo.py", "MCP + Skills：两者怎么配合"),
        ("api_server.py", "OpenAI 兼容 API：自己起一个服务端"),
    ]),
    ("lecture4", "第四章 · 开发 Agent", [
        ("direct_api_demo.py", "裸 API：手拼请求体、手解返回"),
        ("sdk_react_demo.py", "SDK + 手写 ReAct 主循环"),
        ("langgraph_plan_demo.py", "LangGraph：把流程画成图来编排"),
    ]),
]


def build_appendix():
    parts, toc = [], []
    idx = 0
    for folder, gname, files in SCRIPT_GROUPS:
        toc.append('<div class="bk-code-group">%s</div>' % html.escape(gname))
        for fn, desc in files:
            p = os.path.join(SCRIPTS, folder, fn)
            if not os.path.exists(p):
                continue
            idx += 1
            code = io.open(p, encoding='utf-8', errors='replace').read()
            lines = code.count('\n') + 1
            cid = 'code%d' % idx
            toc.append('<a class="bk-code-link" href="#%s"><b>%s</b><span>%s</span></a>' %
                       (cid, html.escape(fn), html.escape(desc)))
            parts.append(
                '<div class="bk-code-card" id="%s">'
                '<div class="bk-code-head" onclick="bkToggle(this)">'
                '<span class="bk-code-no">%02d</span>'
                '<div class="bk-code-meta"><b>%s</b><span>%s</span></div>'
                '<span class="bk-code-lines">%d 行</span>'
                '<span class="bk-code-arrow">▾</span></div>'
                '<div class="bk-code-body"><pre><code>%s</code></pre>'
                '<div class="bk-code-path">路径：scripts/%s/%s</div></div></div>'
                % (cid, idx, html.escape(fn), html.escape(desc), lines,
                   highlight_py(code), folder, fn))
    return '\n'.join(toc), '\n'.join(parts)


# ============================================================
# 五、组装
# ============================================================
def main():
    all_css, sheets, nav, toc_rows = [], [], [], []
    page = 0
    total_pages = sum(len(extract(os.path.join(SLIDES, c['file']))[1]) for c in CHAPTERS) + len(CHAPTERS)

    for ci, ch in enumerate(CHAPTERS, 1):
        scope = '.ch%d' % ci
        css, secs = extract(os.path.join(SLIDES, ch['file']))
        all_css.append('/* ===== 第%s章 %s ===== */\n' % (ch['cn'], ch['title'])
                       + scope_css(css, scope, 'a%d_' % ci))

        # --- 章扉页 ---
        page += 1
        ch['start'] = page
        sec_links = ''.join(
            '<li><span>%s</span><i></i><em>%d</em></li>' % (html.escape(t), page + a)
            for a, b, t in ch['secs'])
        opener = (
            '<div class="bk-opener" style="--ac:%s">'
            '<div class="bk-op-left">'
            '<div class="bk-op-cn">第 %s 章</div>'
            '<div class="bk-op-num">%s</div>'
            '<div class="bk-op-en">%s</div></div>'
            '<div class="bk-op-right">'
            '<h1>%s<small>%s</small></h1>'
            '<p class="bk-op-lead">%s</p>'
            '<div class="bk-op-meta"><span>%s</span><span>%d 页</span>'
            '<span>本章 %d 节</span></div>'
            '<ul class="bk-op-secs">%s</ul>'
            '</div></div>'
            % (ch['accent'], ch['cn'], ch['num'], ch['en'],
               html.escape(ch['title']), html.escape(ch['sub']),
               html.escape(ch['lead']), ch['who'], len(secs), len(ch['secs']), sec_links))
        sheets.append(
            '<div class="bk-sheet bk-sheet-opener" id="p%d" data-ch="%d" data-page="%d">'
            '<div class="bk-paper">%s</div>'
            '<div class="bk-folio"><span>%d</span></div></div>' % (page, ci, page, opener, page))

        # --- 侧栏 + 目录 ---
        nav.append('<div class="bk-nav-ch" data-ch="%d">'
                   '<a class="bk-nav-ch-t" href="#p%d" style="--ac:%s">'
                   '<b>%s</b><span>%s</span><i>%d</i></a><ul>' %
                   (ci, page, ch['accent'], ch['num'], html.escape(ch['title']), page))
        toc_rows.append('<div class="bk-toc-ch"><a href="#p%d" style="--ac:%s">'
                        '<b>第 %s 章</b><span>%s — %s</span><i></i><em>%d</em></a></div>'
                        % (page, ch['accent'], ch['cn'], html.escape(ch['title']),
                           html.escape(ch['sub']), page))

        base = page
        for a, b, t in ch['secs']:
            nav.append('<li><a href="#p%d">%s</a></li>' % (base + a, html.escape(t)))
            toc_rows.append('<div class="bk-toc-sec"><a href="#p%d"><span>%s</span>'
                            '<i></i><em>%d</em></a></div>' % (base + a, html.escape(t), base + a))
        nav.append('</ul></div>')

        # --- 内容页 ---
        for si, sec in enumerate(secs, 1):
            page += 1
            t = sec_title(sec)
            sheets.append(
                '<div class="bk-sheet" id="p%d" data-ch="%d" data-page="%d" data-title="%s">'
                '<div class="bk-paper ch%d">%s</div>'
                '<div class="bk-folio"><span>%d</span><em>%s</em></div></div>'
                % (page, ci, page, html.escape(t[:60], quote=True), ci,
                   add_active(sec), page, html.escape('第%s章 · %s' % (ch['cn'], ch['title']))))

    code_toc, code_body = build_appendix()
    body_pages = page

    chapters_meta = [dict(n=c['num'], t=c['title'], s=c['start'], ac=c['accent']) for c in CHAPTERS]

    doc = TEMPLATE.replace('/*__CSS__*/', '\n'.join(all_css)) \
                  .replace('<!--__NAV__-->', '\n'.join(nav)) \
                  .replace('<!--__TOC__-->', '\n'.join(toc_rows)) \
                  .replace('<!--__SHEETS__-->', '\n'.join(sheets)) \
                  .replace('<!--__CODETOC__-->', code_toc) \
                  .replace('<!--__CODEBODY__-->', code_body) \
                  .replace('__TOTAL__', str(body_pages)) \
                  .replace('__META__', json.dumps(chapters_meta, ensure_ascii=False))

    io.open(OUT, 'w', encoding='utf-8').write(doc)
    print('生成 %s' % OUT)
    print('  正文 %d 页（%d 章扉页 + %d 内容页）' % (body_pages, len(CHAPTERS), body_pages - len(CHAPTERS)))
    print('  体积 %.2f MB' % (os.path.getsize(OUT) / 1048576))


TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Agent 实战手册 · 全书</title>
<style>
/* ==================== 书本外壳 ==================== */
:root{
  --bk-ink:#1F2937; --bk-gray:#6B7280; --bk-faint:#9CA3AF;
  --bk-line:#E5E7EB; --bk-bg:#EEF1F6; --bk-blue:#2563EB;
  --bk-side:296px; --bk-scale:1;
  --bk-serif:"Songti SC","SimSun","Noto Serif CJK SC",Georgia,serif;
  --bk-sans:"PingFang SC","Microsoft YaHei","Noto Sans CJK SC",system-ui,-apple-system,"Segoe UI",sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bk-bg);color:var(--bk-ink);font-family:var(--bk-sans);
  -webkit-font-smoothing:antialiased}

/* ---------- 侧栏 ---------- */
#bk-side{position:fixed;left:0;top:0;bottom:0;width:var(--bk-side);background:#fff;
  border-right:1px solid var(--bk-line);display:flex;flex-direction:column;z-index:60;
  transition:transform .25s ease}
#bk-side.hide{transform:translateX(-100%)}
.bk-brand{padding:22px 22px 16px;border-bottom:1px solid var(--bk-line);flex:none}
.bk-brand .bk-b-k{font-size:10.5px;letter-spacing:.18em;color:var(--bk-blue);font-weight:700}
.bk-brand h1{margin:7px 0 4px;font-size:19px;font-weight:800;letter-spacing:-.01em;line-height:1.3}
.bk-brand p{margin:0;font-size:11.5px;color:var(--bk-gray);line-height:1.5}
.bk-search{flex:none;padding:12px 16px;border-bottom:1px solid var(--bk-line)}
.bk-search input{width:100%;border:1px solid var(--bk-line);background:#F9FAFB;border-radius:8px;
  padding:7px 11px;font-size:12.5px;font-family:inherit;color:var(--bk-ink);outline:none}
.bk-search input:focus{border-color:var(--bk-blue);background:#fff}
#bk-nav{flex:1;overflow-y:auto;padding:10px 12px 28px}
#bk-nav::-webkit-scrollbar{width:7px}
#bk-nav::-webkit-scrollbar-thumb{background:#D5DBE3;border-radius:4px}
.bk-nav-ch{margin-bottom:3px}
.bk-nav-ch-t{display:flex;align-items:center;gap:9px;padding:8px 10px;border-radius:8px;
  text-decoration:none;color:var(--bk-ink);cursor:pointer}
.bk-nav-ch-t:hover{background:#F3F4F6}
.bk-nav-ch-t b{font-size:11px;font-weight:800;color:var(--ac);font-variant-numeric:tabular-nums;
  min-width:19px}
.bk-nav-ch-t span{flex:1;font-size:13.5px;font-weight:600}
.bk-nav-ch-t i{font-style:normal;font-size:11px;color:var(--bk-faint);font-variant-numeric:tabular-nums}
.bk-nav-ch.on .bk-nav-ch-t{background:#EFF6FF}
.bk-nav-ch.on .bk-nav-ch-t span{color:var(--ac)}
.bk-nav-ch ul{list-style:none;margin:1px 0 6px;padding:0 0 0 30px;max-height:0;overflow:hidden;
  transition:max-height .28s ease}
.bk-nav-ch.on ul{max-height:420px}
.bk-nav-ch li a{display:block;padding:4.5px 9px;font-size:12.3px;color:var(--bk-gray);
  text-decoration:none;border-radius:6px;line-height:1.45;border-left:2px solid transparent}
.bk-nav-ch li a:hover{color:var(--bk-ink);background:#F9FAFB}
.bk-nav-ch li a.cur{color:var(--ac,#2563EB);background:#F3F7FF;font-weight:600;
  border-left-color:currentColor}
.bk-nav-extra{margin-top:12px;padding-top:12px;border-top:1px solid var(--bk-line)}
.bk-nav-extra a{display:flex;align-items:center;gap:9px;padding:8px 10px;border-radius:8px;
  font-size:13px;color:var(--bk-ink);text-decoration:none;font-weight:600}
.bk-nav-extra a:hover{background:#F3F4F6}
.bk-nav-extra a b{font-size:11px;color:var(--bk-faint);min-width:19px;font-weight:800}

/* ---------- 顶栏 ---------- */
#bk-top{position:fixed;left:var(--bk-side);right:0;top:0;height:46px;background:rgba(255,255,255,.92);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--bk-line);display:flex;align-items:center;
  gap:14px;padding:0 20px;z-index:50;transition:left .25s ease}
body.wide #bk-top{left:0}
body.wide #bk-side{transform:translateX(-100%)}
body.wide #bk-main{padding-left:0}
#bk-burger{border:1px solid var(--bk-line);background:#fff;border-radius:7px;width:30px;height:28px;
  cursor:pointer;color:var(--bk-gray);font-size:14px;line-height:1;flex:none}
#bk-burger:hover{border-color:var(--bk-blue);color:var(--bk-blue)}
#bk-crumb{flex:1;font-size:13px;color:var(--bk-gray);white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis}
#bk-crumb b{color:var(--bk-ink);font-weight:600}
#bk-crumb i{font-style:normal;color:var(--bk-faint);margin:0 7px}
.bk-tools{display:flex;gap:7px;flex:none}
.bk-tools button{border:1px solid var(--bk-line);background:#fff;border-radius:7px;padding:5px 11px;
  font-size:12px;color:var(--bk-gray);cursor:pointer;font-family:inherit;white-space:nowrap}
.bk-tools button:hover{border-color:var(--bk-blue);color:var(--bk-blue)}
#bk-pageno{font-size:12px;color:var(--bk-faint);font-variant-numeric:tabular-nums;flex:none}
#bk-pageno b{color:var(--bk-ink)}
#bk-bar{position:fixed;top:46px;left:var(--bk-side);right:0;height:2px;background:transparent;z-index:51;
  transition:left .25s ease}
body.wide #bk-bar{left:0}
#bk-bar i{display:block;height:100%;width:0;background:var(--bk-blue);transition:width .1s linear}

/* ---------- 正文区 ---------- */
#bk-main{padding-left:var(--bk-side);padding-top:46px;transition:padding-left .25s ease}
.bk-wrap{max-width:1180px;margin:0 auto;padding:26px 30px 90px}

/* 扉页 */
.bk-title-page{background:#fff;border:1px solid var(--bk-line);border-radius:4px;
  box-shadow:0 2px 10px rgba(15,23,42,.05);padding:74px 70px 62px;margin-bottom:22px;
  position:relative;overflow:hidden}
.bk-title-page::before{content:"";position:absolute;left:0;top:0;bottom:0;width:5px;
  background:linear-gradient(180deg,#2563EB,#7C3AED,#0D9488)}
.bk-tp-k{font-size:11px;letter-spacing:.24em;color:var(--bk-blue);font-weight:700;margin-bottom:20px}
.bk-title-page h1{margin:0;font-size:52px;font-weight:800;letter-spacing:-.02em;line-height:1.12}
.bk-title-page h2{margin:16px 0 0;font-size:19px;font-weight:400;color:var(--bk-gray);line-height:1.55}
.bk-tp-rule{height:1px;background:var(--bk-line);margin:34px 0 26px}
.bk-tp-facts{display:flex;flex-wrap:wrap;gap:34px}
.bk-tp-facts div b{display:block;font-size:25px;font-weight:800;letter-spacing:-.01em}
.bk-tp-facts div span{font-size:11.5px;color:var(--bk-faint);letter-spacing:.05em}
.bk-tp-note{margin-top:28px;font-size:12.5px;color:var(--bk-faint);line-height:1.75}
.bk-tp-note code{background:#F3F4F6;border-radius:3px;padding:1px 5px;font-size:11.5px}

/* 目录 */
.bk-toc{background:#fff;border:1px solid var(--bk-line);border-radius:4px;
  box-shadow:0 2px 10px rgba(15,23,42,.05);padding:48px 62px 52px;margin-bottom:30px}
.bk-toc-h{font-size:11px;letter-spacing:.24em;color:var(--bk-faint);font-weight:700;
  text-align:center;margin-bottom:6px}
.bk-toc-t{font-family:var(--bk-serif);font-size:29px;font-weight:700;text-align:center;
  margin-bottom:34px;letter-spacing:.14em}
.bk-toc-ch{margin-top:22px}
.bk-toc-ch:first-child{margin-top:0}
.bk-toc-ch a{display:flex;align-items:baseline;gap:11px;text-decoration:none;color:var(--bk-ink);
  padding:5px 0}
.bk-toc-ch a:hover span{color:var(--ac)}
.bk-toc-ch b{font-size:13px;font-weight:800;color:var(--ac);white-space:nowrap;min-width:56px}
.bk-toc-ch span{font-size:16px;font-weight:700;white-space:nowrap}
.bk-toc-ch i,.bk-toc-sec i{flex:1;border-bottom:1px dotted #CBD5E1;transform:translateY(-3px)}
.bk-toc-ch em,.bk-toc-sec em{font-style:normal;font-size:13px;color:var(--bk-gray);
  font-variant-numeric:tabular-nums;min-width:26px;text-align:right}
.bk-toc-sec a{display:flex;align-items:baseline;gap:11px;text-decoration:none;color:var(--bk-gray);
  padding:3px 0 3px 67px;font-size:13.5px}
.bk-toc-sec a:hover{color:var(--bk-blue)}
.bk-toc-sec span{white-space:nowrap}
.bk-toc-foot{margin-top:30px;padding-top:18px;border-top:1px solid var(--bk-line);
  display:flex;justify-content:space-between;font-size:12px;color:var(--bk-faint)}

/* 书页 */
.bk-sheet{position:relative;margin:0 auto 26px;max-width:1180px;
  height:calc(720px * var(--bk-scale))}
.bk-paper{width:1280px;height:720px;transform:scale(var(--bk-scale));transform-origin:top left;
  background:#fff;overflow:hidden;position:relative;
  box-shadow:0 1px 3px rgba(15,23,42,.09),0 8px 26px rgba(15,23,42,.07);border-radius:3px}
.bk-folio{position:absolute;left:0;right:0;bottom:-21px;display:flex;justify-content:space-between;
  align-items:center;font-size:11px;color:var(--bk-faint);padding:0 3px;
  font-variant-numeric:tabular-nums}
.bk-folio em{font-style:normal;font-size:10.5px;opacity:.75}
.bk-folio span{font-weight:600}
/* 隐藏各讲自带的分页脚注，避免与书本统一页码（.bk-folio）重复/冲突 */
.bk-paper .pagenum{display:none !important}

/* 章扉页内容 */
.bk-opener{width:100%;height:100%;display:flex;background:#fff;position:relative}
.bk-opener::after{content:"";position:absolute;left:0;right:0;bottom:0;height:6px;background:var(--ac)}
.bk-op-left{width:352px;flex:none;background:var(--ac);color:#fff;padding:74px 46px;
  display:flex;flex-direction:column;justify-content:center;position:relative;overflow:hidden}
.bk-op-left::before{content:"";position:absolute;right:-70px;bottom:-70px;width:230px;height:230px;
  border-radius:50%;background:rgba(255,255,255,.09)}
.bk-op-cn{font-size:17px;opacity:.85;letter-spacing:.16em;margin-bottom:4px}
.bk-op-num{font-size:112px;font-weight:800;line-height:.92;letter-spacing:-.04em}
.bk-op-en{margin-top:16px;font-size:11.5px;letter-spacing:.2em;opacity:.8;font-weight:600}
.bk-op-right{flex:1;padding:70px 60px 62px;display:flex;flex-direction:column}
.bk-op-right h1{margin:0;font-size:46px;font-weight:800;letter-spacing:-.02em;line-height:1.14}
.bk-op-right h1 small{display:block;font-size:19px;font-weight:400;color:var(--bk-gray);
  margin-top:11px;letter-spacing:0}
.bk-op-lead{margin:22px 0 0;font-size:15px;line-height:1.85;color:#4B5563;max-width:660px}
.bk-op-meta{display:flex;gap:9px;margin:22px 0 0}
.bk-op-meta span{font-size:11.5px;color:var(--ac);background:color-mix(in srgb,var(--ac) 9%,#fff);
  border:1px solid color-mix(in srgb,var(--ac) 26%,#fff);border-radius:999px;padding:3px 12px;
  font-weight:600}
.bk-op-secs{list-style:none;margin:auto 0 0;padding:20px 0 0;border-top:1px solid var(--bk-line)}
.bk-op-secs li{display:flex;align-items:baseline;gap:10px;padding:5.5px 0;font-size:13.5px;
  color:#4B5563}
.bk-op-secs li i{flex:1;border-bottom:1px dotted #D1D8E0;transform:translateY(-3px)}
.bk-op-secs li em{font-style:normal;font-size:12px;color:var(--bk-faint);
  font-variant-numeric:tabular-nums}

/* 附录代码 */
.bk-apx{background:#fff;border:1px solid var(--bk-line);border-radius:4px;
  box-shadow:0 2px 10px rgba(15,23,42,.05);padding:46px 56px 52px;margin-top:34px}
.bk-apx-k{font-size:11px;letter-spacing:.22em;color:#B45309;font-weight:700}
.bk-apx h2{margin:9px 0 8px;font-size:31px;font-weight:800;letter-spacing:-.01em}
.bk-apx-lead{font-size:14px;color:var(--bk-gray);line-height:1.75;max-width:760px;margin:0 0 26px}
.bk-code-index{display:grid;grid-template-columns:repeat(auto-fill,minmax(268px,1fr));gap:7px;
  margin-bottom:34px}
.bk-code-group{grid-column:1/-1;font-size:11.5px;font-weight:700;color:var(--bk-faint);
  letter-spacing:.08em;margin-top:12px;padding-bottom:3px}
.bk-code-group:first-child{margin-top:0}
.bk-code-link{display:block;padding:8px 12px;border:1px solid var(--bk-line);border-radius:8px;
  text-decoration:none;color:inherit}
.bk-code-link:hover{border-color:var(--bk-blue);background:#F8FBFF}
.bk-code-link b{display:block;font-size:12.5px;font-family:ui-monospace,"Cascadia Code",Consolas,monospace;
  color:#0F766E}
.bk-code-link span{display:block;font-size:11.5px;color:var(--bk-gray);margin-top:2px;line-height:1.45}
.bk-code-card{border:1px solid var(--bk-line);border-radius:10px;margin-bottom:10px;overflow:hidden;
  scroll-margin-top:64px}
.bk-code-head{display:flex;align-items:center;gap:13px;padding:12px 16px;cursor:pointer;
  background:#FAFBFC;user-select:none}
.bk-code-head:hover{background:#F3F6FA}
.bk-code-no{font-size:11px;font-weight:800;color:#fff;background:#94A3B8;border-radius:5px;
  padding:2px 7px;font-variant-numeric:tabular-nums;flex:none}
.bk-code-card.open .bk-code-no{background:var(--bk-blue)}
.bk-code-meta{flex:1;min-width:0}
.bk-code-meta b{display:block;font-size:13px;font-family:ui-monospace,"Cascadia Code",Consolas,monospace;
  color:#0F766E}
.bk-code-meta span{display:block;font-size:12px;color:var(--bk-gray);margin-top:1px}
.bk-code-lines{font-size:11px;color:var(--bk-faint);flex:none}
.bk-code-arrow{font-size:11px;color:var(--bk-faint);transition:transform .2s;flex:none}
.bk-code-card.open .bk-code-arrow{transform:rotate(180deg)}
.bk-code-body{display:none;border-top:1px solid var(--bk-line)}
.bk-code-card.open .bk-code-body{display:block}
.bk-code-body pre{margin:0;padding:18px 20px;overflow-x:auto;background:#FBFCFD;
  max-height:560px;overflow-y:auto}
.bk-code-body code{font-family:ui-monospace,"Cascadia Code","JetBrains Mono",Consolas,monospace;
  font-size:12.3px;line-height:1.72;color:#334155;white-space:pre;tab-size:4}
.bk-code-body .kw{color:#7C3AED;font-weight:600}
.bk-code-body .st{color:#0E7490}
.bk-code-body .cm{color:#94A3B8;font-style:italic}
.bk-code-body .nu{color:#B45309}
.bk-code-body .fn{color:#2563EB}
.bk-code-path{padding:9px 20px;border-top:1px solid var(--bk-line);font-size:11.5px;
  color:var(--bk-faint);background:#fff}

/* 版权页 */
.bk-colophon{margin-top:34px;padding:30px 56px 34px;background:#fff;border:1px solid var(--bk-line);
  border-radius:4px;font-size:12.5px;color:var(--bk-gray);line-height:1.9}
.bk-colophon b{color:var(--bk-ink)}
.bk-colophon code{background:#F3F4F6;border-radius:3px;padding:1px 5px;font-size:11.5px}

/* 回到顶部 */
#bk-up{position:fixed;right:26px;bottom:26px;width:38px;height:38px;border-radius:50%;
  border:1px solid var(--bk-line);background:#fff;color:var(--bk-gray);cursor:pointer;font-size:15px;
  box-shadow:0 3px 12px rgba(15,23,42,.10);display:none;z-index:55}
#bk-up.on{display:block}
#bk-up:hover{color:var(--bk-blue);border-color:var(--bk-blue)}

/* 搜索命中 */
.bk-nav-ch.dim{display:none}
.bk-nav-ch li.dim{display:none}

/* ==================== 打印：每页一张 16:9 ==================== */
@media print{
  @page{size:960pt 540pt;margin:0}
  :root{--bk-scale:1 !important}
  body{background:#fff}
  #bk-side,#bk-top,#bk-bar,#bk-up,.bk-search{display:none !important}
  #bk-main{padding:0 !important}
  .bk-wrap{max-width:none;padding:0;margin:0}
  .bk-sheet{margin:0 !important;max-width:none;width:960pt;height:540pt;overflow:hidden;
    page-break-after:always;break-after:page;position:relative}
  .bk-paper{box-shadow:none !important;border-radius:0 !important;transform:none !important;
    transform-origin:top left !important;width:960pt !important;height:540pt !important;
    padding:0;overflow:hidden !important}
  .bk-paper .ch1,.bk-paper .ch2,.bk-paper .ch3,.bk-paper .ch4,.bk-paper .ch5,
  .bk-paper .ch6,.bk-paper .ch7,
  .bk-paper section.slide{width:960pt !important;height:540pt !important;
    transform:none !important;position:relative !important;inset:auto !important;
    left:auto !important;top:auto !important;opacity:1 !important;visibility:visible !important}
  .bk-folio{display:none !important}
  .bk-title-page,.bk-toc{border:none;box-shadow:none;page-break-after:always;break-after:page;
    width:960pt;height:540pt;padding:32pt 48pt;overflow:hidden;margin:0}
  .bk-title-page h1{font-size:36pt}
  .bk-apx,.bk-colophon{display:none !important}
  .bk-sheet:last-of-type{page-break-after:auto;break-after:auto}
}
/* ==================== 各讲原始样式（已作用域隔离） ==================== */
/*__CSS__*/
</style>
</head>
<body>

<aside id="bk-side">
  <div class="bk-brand">
    <div class="bk-b-k">AI AGENT 系列培训</div>
    <h1>AI Agent 实战手册</h1>
    <p>从装上第一个 Agent，到把它送进生产</p>
  </div>
  <div class="bk-search"><input id="bk-q" type="search" placeholder="筛选章节标题…" autocomplete="off"></div>
  <div id="bk-nav">
    <div class="bk-nav-extra" style="margin-top:0;padding-top:0;border:none">
      <a href="#bk-cover"><b>—</b>扉页与目录</a>
    </div>
    <!--__NAV__-->
    <div class="bk-nav-extra">
      <a href="#bk-appendix"><b>附</b>配套代码（17 个脚本）</a>
    </div>
  </div>
</aside>

<div id="bk-top">
  <button id="bk-burger" title="收起 / 展开目录">☰</button>
  <div id="bk-crumb"><b>扉页</b></div>
  <div class="bk-tools">
    <button onclick="bkPrint()">打印 / 导出 PDF</button>
    <button onclick="bkAll(1)">展开全部代码</button>
  </div>
  <div id="bk-pageno"><b>—</b> / __TOTAL__</div>
</div>
<div id="bk-bar"><i></i></div>

<main id="bk-main"><div class="bk-wrap">

  <section class="bk-title-page" id="bk-cover">
    <div class="bk-tp-k">AI AGENT 系列培训 · 整合版 v2</div>
    <h1>AI Agent 实战手册</h1>
    <h2>从装上第一个 Agent，到把它送进生产<br>七章一条主线：用起来 → 懂原理 → 会开发 → 能落地 → 看远方</h2>
    <div class="bk-tp-rule"></div>
    <div class="bk-tp-facts">
      <div><b>7</b><span>章</span></div>
      <div><b>__TOTAL__</b><span>页</span></div>
      <div><b>17</b><span>配套脚本</span></div>
      <div><b>23</b><span>条参考资料</span></div>
      <div><b>1</b><span>个文件</span></div>
    </div>
    <p class="bk-tp-note">
      全书为单一 HTML 文件，离线可读，浏览器 <code>Ctrl</code>+<code>F</code> 可全书搜索。<br>
      左侧目录树跳转，<code>←</code> <code>→</code> 逐页翻，<code>Ctrl</code>+<code>P</code> 导出 16:9 PDF。
    </p>
  </section>

  <section class="bk-toc" id="bk-toc">
    <div class="bk-toc-h">CONTENTS</div>
    <div class="bk-toc-t">目　录</div>
    <!--__TOC__-->
    <div class="bk-toc-sec" style="margin-top:22px">
      <a href="#bk-appendix"><span>附录 · 配套代码（17 个可运行脚本）</span><i></i><em>后附</em></a>
    </div>
    <div class="bk-toc-foot">
      <span>整合版 v2 · 2026-08-03</span>
      <span>全书 __TOTAL__ 页</span>
    </div>
  </section>

  <!--__SHEETS__-->

  <section class="bk-apx" id="bk-appendix">
    <div class="bk-apx-k">APPENDIX</div>
    <h2>附录 · 配套代码</h2>
    <p class="bk-apx-lead">17 个可运行脚本，覆盖第二、三、四章的全部演示。纯 CPU 可跑，Python 3.10+。
      点击任意条目展开完整源码；代码已内嵌在本文件中，离线可读。</p>
    <div class="bk-code-index"><!--__CODETOC__--></div>
    <!--__CODEBODY__-->
  </section>

  <section class="bk-colophon">
    <b>关于这本书</b><br>
    本书由七份独立培训胶片整合而成，已完成内容去重与衔接标注：协议（第 1 章点名 / 第 3 章入门 / 第 5 章分层）、
    ReAct（第 3 章原理 / 第 4 章代码）、训练三步（第 2 章历史 / 第 3 章选型）。<br>
    第 6 章采用概念版，其工程章 3 页已并入第 3 章。<br>
    原始文件保留于 <code>C:\Users\think\WorkBuddy\aippt2~7、aipp4</code> 与 <code>D:\文档\aippt</code>，未做改动。<br>
    版本记录见 <code>VERSIONS.md</code>　｜　整合版 v2 · 2026-08-03
  </section>

</div></main>

<button id="bk-up" onclick="scrollTo({top:0,behavior:'smooth'})" title="回到顶部">↑</button>

<script>
var BK = { meta: __META__, total: __TOTAL__ };

/* ---- 缩放：让 1280×720 的页面适配容器宽度 ---- */
function bkFit(){
  var wrap = document.querySelector('.bk-wrap');
  if(!wrap) return;
  var w = wrap.clientWidth - 60;
  document.documentElement.style.setProperty('--bk-scale', Math.min(1, w/1280).toFixed(4));
}
window.addEventListener('resize', bkFit);

/* ---- 代码展开 ---- */
function bkToggle(el){ el.parentNode.classList.toggle('open'); }
function bkAll(on){
  document.querySelectorAll('.bk-code-card').forEach(function(c){ c.classList.toggle('open', !!on); });
}
document.querySelectorAll('.bk-code-link').forEach(function(a){
  a.addEventListener('click', function(){
    var c = document.querySelector(a.getAttribute('href'));
    if(c) c.classList.add('open');
  });
});

/* ---- 打印 ---- */
function bkPrint(){ bkAll(0); window.print(); }

/* ---- 侧栏折叠 ---- */
document.getElementById('bk-burger').onclick = function(){
  document.body.classList.toggle('wide'); setTimeout(bkFit, 260);
};

/* ---- 滚动同步：当前章 / 页码 / 进度 ---- */
var sheets = [].slice.call(document.querySelectorAll('.bk-sheet'));
var navChs = [].slice.call(document.querySelectorAll('.bk-nav-ch'));
var crumb = document.getElementById('bk-crumb');
var pageno = document.getElementById('bk-pageno');
var bar = document.querySelector('#bk-bar i');
var up = document.getElementById('bk-up');
var cur = -1;

function bkSync(){
  var mid = window.scrollY + innerHeight*0.36, best = null;
  for(var i=0;i<sheets.length;i++){
    if(sheets[i].offsetTop <= mid) best = sheets[i]; else break;
  }
  var doc = document.documentElement;
  bar.style.width = (window.scrollY/(doc.scrollHeight-innerHeight)*100).toFixed(2)+'%';
  up.classList.toggle('on', window.scrollY > 600);

  if(!best){
    if(cur!==0){ crumb.innerHTML='<b>扉页与目录</b>'; pageno.innerHTML='<b>—</b> / '+BK.total;
      navChs.forEach(function(n){n.classList.remove('on');}); cur=0; }
    return;
  }
  var p = +best.dataset.page, ci = +best.dataset.ch;
  if(p===cur) return;
  cur = p;
  var m = BK.meta[ci-1];
  var t = best.dataset.title || '';
  crumb.innerHTML = '<b>第 '+m.n+' 章　'+m.t+'</b>' + (t ? '<i>›</i>'+t : '');
  pageno.innerHTML = '<b>'+p+'</b> / '+BK.total;
  navChs.forEach(function(n){ n.classList.toggle('on', +n.dataset.ch===ci); });
  var on = document.querySelector('.bk-nav-ch.on');
  if(on){
    var links = [].slice.call(on.querySelectorAll('li a')), pick=null;
    links.forEach(function(a){ if(+a.getAttribute('href').slice(2) <= p) pick=a; });
    links.forEach(function(a){ a.classList.toggle('cur', a===pick); });
  }
}
addEventListener('scroll', bkSync, {passive:true});

/* ---- 键盘：←→ 逐页 ---- */
addEventListener('keydown', function(e){
  if(/input|textarea/i.test(e.target.tagName)) return;
  if(e.ctrlKey||e.metaKey||e.altKey) return;
  var i = sheets.findIndex(function(s){ return +s.dataset.page === cur; });
  if(e.key==='ArrowRight'||e.key==='PageDown'){
    e.preventDefault(); var n=sheets[i+1]||sheets[0];
    if(i<0) n=sheets[0]; scrollTo({top:n.offsetTop-58,behavior:'smooth'});
  } else if(e.key==='ArrowLeft'||e.key==='PageUp'){
    e.preventDefault();
    if(i<=0){ scrollTo({top:0,behavior:'smooth'}); }
    else scrollTo({top:sheets[i-1].offsetTop-58,behavior:'smooth'});
  } else if(e.key==='Home'){ e.preventDefault(); scrollTo({top:0,behavior:'smooth'}); }
  else if(e.key==='End'){ e.preventDefault();
    scrollTo({top:sheets[sheets.length-1].offsetTop-58,behavior:'smooth'}); }
  else if(e.key==='p'||e.key==='P'){ e.preventDefault(); bkPrint(); }
});

/* ---- 侧栏搜索筛选 ---- */
document.getElementById('bk-q').addEventListener('input', function(e){
  var q = e.target.value.trim().toLowerCase();
  navChs.forEach(function(n){
    var hitCh = n.querySelector('.bk-nav-ch-t span').textContent.toLowerCase().indexOf(q)>=0;
    var any = hitCh;
    n.querySelectorAll('li').forEach(function(li){
      var hit = !q || li.textContent.toLowerCase().indexOf(q)>=0;
      li.classList.toggle('dim', !(hit||hitCh));
      if(hit) any = true;
    });
    n.classList.toggle('dim', !!q && !any);
    if(q && any) n.classList.add('on');
  });
});

/* ---- 点击章标题展开/收起 ---- */
document.querySelectorAll('.bk-nav-ch-t').forEach(function(a){
  a.addEventListener('click', function(){
    setTimeout(function(){
      navChs.forEach(function(n){ n.classList.remove('on'); });
      a.parentNode.classList.add('on');
    }, 30);
  });
});

bkFit(); bkSync();

/* ---- 调试参数：?at=code1 立即定位 ---- */
(function(){
  try{
    var at = new URL(location.href).searchParams.get('at');
    if(!at) return;
    var id = /^\d+$/.test(at) ? 'p' + at : at;
    var el = document.getElementById(id);
    if(!el) return;
    document.documentElement.style.scrollBehavior = 'auto';
    document.documentElement.scrollTop = el.offsetTop - 58;
    cur = -1; bkSync();
  }catch(e){
    document.title = 'JERR:' + e.message;
  }
})();
addEventListener('beforeprint', function(){ document.body.classList.add('printing'); });
</script>
</body>
</html>
'''

if __name__ == '__main__':
    main()

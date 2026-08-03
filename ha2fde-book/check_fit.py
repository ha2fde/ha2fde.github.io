# -*- coding: utf-8 -*-
"""
用无头 Chromium 实测分章版有没有内容被裁切，并和拆分前的 book.html 做对照。

判定依据：每页幻灯片 .slide 是 overflow:hidden 的定高盒子，
若 slide.scrollHeight > slide.clientHeight，说明内容溢出、被裁掉了。

用法：
  python3 -m pip install --user playwright
  python3 -m playwright install chromium
  python3 check_fit.py
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = '/tmp/fitcheck'
ORIG = '/tmp/book.orig.html'          # 拆分前的原件（对照组）
PAGES = ['index.html'] + ['ch%02d.html' % i for i in range(1, 8)] + ['appendix.html']

VIEWPORT = {'width': 1600, 'height': 1000}

# 逐页量：溢出量、已应用的 --fit
PROBE = r'''
() => {
  const out = [];
  document.querySelectorAll('.bk-sheet').forEach(sh => {
    const slide = sh.querySelector('section.slide, .bk-opener');
    if(!slide) return;
    const over = slide.scrollHeight - slide.clientHeight;
    const fit  = getComputedStyle(sh).getPropertyValue('--fit').trim() || '1';
    /* 几何断言：缩放后的 .bk-fit 必须落在纸面内。
       只看 scrollHeight 查不出「.bk-fit 比纸面还大、被纸面裁掉」这种错。 */
    const paper = sh.querySelector('.bk-paper');
    let gw = 0, gh = 0;
    if(paper){
      const pr = paper.getBoundingClientRect();
      const el = sh.querySelector('.bk-fit') || slide;
      const er = el.getBoundingClientRect();
      gw = Math.round(er.width  - pr.width);
      gh = Math.round(er.height - pr.height);
    }
    out.push({page: +sh.dataset.page, over: over, fit: parseFloat(fit),
              gw: gw, gh: gh, title: sh.dataset.title || ''});
  });
  return out;
}
'''


def run(pw, url, label):
    br = pw.chromium.launch()
    pg = br.new_page(viewport=VIEWPORT, device_scale_factor=2)
    pg.goto(url, wait_until='load')
    pg.wait_for_timeout(1500)          # 等字体 + bkFitPages 跑完
    rows = pg.evaluate(PROBE)
    br.close()
    return rows


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit('缺 playwright，先跑：\n'
                 '  python3 -m pip install --user playwright\n'
                 '  python3 -m playwright install chromium')

    if not os.path.isdir(SHOTS):
        os.makedirs(SHOTS)

    with sync_playwright() as pw:
        # ---------- 对照组：拆分前的单文件 ----------
        before = []
        if os.path.exists(ORIG):
            before = run(pw, 'file://' + ORIG, 'book.html(原)')
            bad = [r for r in before if r['over'] > 1]
            print('【拆分前 book.html】%d 页中 %d 页内容被裁切' % (len(before), len(bad)))
            for r in sorted(bad, key=lambda x: -x['over'])[:12]:
                print('   p%-4d 溢出 %4dpx  %s' % (r['page'], r['over'], r['title'][:34]))
        else:
            print('（没找到 %s，跳过对照）' % ORIG)

        # ---------- 实验组：分章版 ----------
        print('\n【分章版】')
        allrows, clipped, scaled = [], [], []
        for f in PAGES:
            rows = run(pw, 'file://' + os.path.join(HERE, f), f)
            for r in rows:
                r['file'] = f
            allrows += rows
            clipped += [r for r in rows if r['over'] > 1]
            scaled += [r for r in rows if r['fit'] < 0.999]
            print('  %-14s %3d 页，缩放过 %2d 页，仍被裁 %d 页'
                  % (f, len(rows), len([r for r in rows if r['fit'] < 0.999]),
                     len([r for r in rows if r['over'] > 1])))

        print('\n合计 %d 页：自动缩放 %d 页，仍被裁切 %d 页'
              % (len(allrows), len(scaled), len(clipped)))

        if clipped:
            print('\n仍被裁切（需要继续修）：')
            for r in sorted(clipped, key=lambda x: -x['over'])[:20]:
                print('   %s p%-4d 溢出 %4dpx  fit=%.3f  %s'
                      % (r['file'], r['page'], r['over'], r['fit'], r['title'][:30]))

        spill = [r for r in allrows if r.get('gw', 0) > 1 or r.get('gh', 0) > 1]
        print('\n几何断言：%d 页的 .bk-fit 超出纸面%s'
              % (len(spill), '' if not spill else '（会被纸面裁掉，必须修）'))
        for r in sorted(spill, key=lambda x: -max(x['gw'], x['gh']))[:20]:
            print('   %s p%-4d 超出 宽%+dpx 高%+dpx  fit=%.3f  %s'
                  % (r['file'], r['page'], r['gw'], r['gh'], r['fit'], r['title'][:28]))

        # ---------- 给缩得最狠的几页截图，供肉眼复核 ----------
        worst = sorted(scaled, key=lambda x: x['fit'])[:6]
        if worst:
            print('\n缩放最狠的 %d 页，截图存到 %s：' % (len(worst), SHOTS))
            br = pw.chromium.launch()
            pg = br.new_page(viewport=VIEWPORT, device_scale_factor=2)
            for r in worst:
                pg.goto('file://' + os.path.join(HERE, r['file']), wait_until='load')
                pg.wait_for_timeout(1200)
                el = pg.query_selector('#p%d .bk-paper' % r['page'])
                if not el:
                    continue
                el.scroll_into_view_if_needed()
                pg.wait_for_timeout(250)
                out = os.path.join(SHOTS, 'p%03d.png' % r['page'])
                el.screenshot(path=out)
                print('   p%-4d fit=%.3f  %-30s → %s' % (r['page'], r['fit'], r['title'][:28], out))
            br.close()

        json.dump(allrows, open(os.path.join(SHOTS, 'report.json'), 'w'),
                  ensure_ascii=False, indent=1)
        print('\n明细：%s/report.json' % SHOTS)


if __name__ == '__main__':
    main()

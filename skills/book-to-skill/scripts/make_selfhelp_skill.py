#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Зарегистрировать self-help скилл из готового дистиллята + копию в архив !LAMA.

Usage:
  python make_selfhelp_skill.py --name self-help-<тема> --desc "Use when ..." \
      --source "E:/.../первоисточник.pdf" --body distillate.md [--category self-help]

Шаги: собрать frontmatter + тело -> записать напрямую в
<hermes>/skills/<category>/<name>/SKILL.md (прямая запись работает: `hermes skills list`
показывает local/enabled; для тел ~100К skill_manage create ненадёжен) ->
скопировать в ~/Documents/!LAMA/skills/<category>/<name>/.
Проверь вывод: desc без кавычек <= 60 символов, SKILL.md <= 100000 символов.
"""
import argparse, os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', required=True)
    ap.add_argument('--desc', required=True)
    ap.add_argument('--source', required=True)
    ap.add_argument('--body', required=True)
    ap.add_argument('--category', default='self-help')
    args = ap.parse_args()

    localappdata = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~/AppData/Local')
    hermes_root = os.path.join(localappdata, 'hermes', 'skills')
    archive_root = os.path.join(os.path.expanduser('~'), 'Documents', '!LAMA', 'skills')

    body = open(args.body, encoding='utf-8').read()
    fm = (
        '---\n'
        f'name: {args.name}\n'
        f'description: "{args.desc}"\n'
        'version: 1.0.0\n'
        'author: Hermes Agent (дистилляция книги)\n'
        'license: MIT\n'
        'platforms: [linux, macos, windows]\n'
        f'source: "{args.source}"\n'
        'metadata:\n'
        '  hermes:\n'
        '    tags: [self-help, psychology]\n'
        '---\n\n'
    )
    content = (fm + body).replace('\r\n', '\n')
    for root in (hermes_root, archive_root):
        d = os.path.join(root, args.category, args.name)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, 'SKILL.md')
        open(p, 'w', encoding='utf-8').write(content)
        print('wrote', p, len(content), 'chars')
    print(f'desc len (без кавычек): {len(args.desc)}  (<=60)')
    print(f'SKILL.md: {len(content)} chars (<=100000)')


if __name__ == '__main__':
    main()

import win32com.client as win32
import os, sys

# DOC/RTF -> UTF-8 text via MS Word COM. Usage: python extract_word_docs.py <out_dir> <file1> <file2> ...
# Why: antiword fails on RTF-masquerading-as-.doc; naive RTF parsers emit fonttbl/hex garbage.
out_dir = sys.argv[1]
files = sys.argv[2:]
word = win32.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for path in files:
        slug = os.path.splitext(os.path.basename(path))[0]
        try:
            doc = word.Documents.Open(path, ReadOnly=True, AddToRecentFiles=False)
            text = doc.Content.Text
            doc.Close(False)
            with open(os.path.join(out_dir, slug + '.txt'), 'w', encoding='utf-8') as f:
                f.write(text)
            print(f'{slug}: {len(text)} chars')
        except Exception as e:
            print(f'{slug}: ERROR {e}')
finally:
    word.Quit()

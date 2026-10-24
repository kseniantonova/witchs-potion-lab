"""Package the unchanged static game for Pages; requires only Python 3."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import re
import shutil
import struct

ROOT = Path(__file__).resolve().parent
OUTPUT = (ROOT / 'dist').resolve()
FILES = ['index.html', 'style.css', 'layout.css', 'start.css', 'final.css',
         'failure.css', 'data.js', 'script.js']
ART = ['lab-background', 'witch-neutral', 'witch-happy', 'cauldron-normal',
       'cauldron-bubbling', 'ingredient-tile', 'mouse-one', 'mice-five',
       'goose-one', 'geese-four', 'sheep-one', 'sheep-six']


def local_reference(value, parent=ROOT):
    """Require exact-case, relative paths that also work under a repo subpath."""
    url = urlsplit(value)
    if url.scheme or url.netloc or not url.path:
        return
    if url.path.startswith(('/', '\\')):
        raise ValueError('Root-relative asset path: ' + value)
    path = parent / unquote(url.path)
    if not path.resolve().is_relative_to(ROOT):
        raise ValueError('Asset outside project: ' + value)
    relative = path.relative_to(ROOT)
    current = ROOT
    for part in relative.parts:
        if part not in {entry.name for entry in current.iterdir()}:
            raise ValueError('Missing asset or incorrect filename case: ' + value)
        current /= part
    if relative.as_posix() not in FILES:
        raise ValueError('Referenced asset is not included in the build: ' + value)


class AssetParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('src', 'href') and value:
                local_reference(value)


def main():
    FILES.extend('public/assets/witch-lab/' + name + '.png' for name in ART)
    for name in FILES:
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            raise ValueError('Missing or unsupported source file: ' + name)
        if path.suffix == '.png':
            header = path.read_bytes()[:24]
            if header[:8] != b'\x89PNG\r\n\x1a\n' or not all(struct.unpack('>II', header[16:24])):
                raise ValueError('Invalid PNG: ' + name)
    AssetParser().feed((ROOT / 'index.html').read_text(encoding='utf-8'))
    for path in ROOT.glob('*.css'):
        for match in re.finditer(r'url\(\s*[\'\"]?([^\'\"\)]+)', path.read_text(encoding='utf-8')):
            local_reference(match.group(1).strip(), path.parent)
    script = (ROOT / 'script.js').read_text(encoding='utf-8')
    if "const assetRoot = 'public/assets/witch-lab/';" not in script:
        raise ValueError('Check the runtime image base path before publishing.')
    # Guard the resolved target before cleaning a previous build on Windows.
    if OUTPUT.parent != ROOT or OUTPUT.name != 'dist':
        raise ValueError('Build output must stay inside this project.')
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    for name in FILES:
        target = OUTPUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    (OUTPUT / '.nojekyll').touch()
    print(f'Build OK: {len(FILES)} original game files, including {len(ART)} PNGs, in dist/.')


if __name__ == '__main__':
    main()

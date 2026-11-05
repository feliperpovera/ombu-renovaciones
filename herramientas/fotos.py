# Convierte las fotos originales de fotos/ (jpg, jpeg, png o webp, subidas a mano o desde el panel)
# en dist/fotos/NOMBRE.webp (1600 px) y NOMBRE-800.webp.
# Solo procesa las nuevas o cambiadas (compara una huella del archivo). Escribe dist/fotos/medidas.json.
# Uso: npm run construir (o python3 herramientas/fotos.py)
import hashlib, json, pathlib
from PIL import Image, ImageOps

src, out = pathlib.Path('fotos'), pathlib.Path('dist/fotos')
out.mkdir(parents=True, exist_ok=True)
mfile = out / 'medidas.json'
medidas = json.loads(mfile.read_text()) if mfile.exists() else {}
nuevas = 0
for f in sorted(p for p in src.iterdir() if p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp')):
    huella = hashlib.md5(f.read_bytes()).hexdigest()[:12]
    if medidas.get(f.stem, [0, 0, ''])[2:] == [huella] and (out / f'{f.stem}.webp').exists():
        continue
    im = ImageOps.exif_transpose(Image.open(f)).convert('RGB')
    for w, suf in ((1600, ''), (800, '-800')):
        r = im.copy(); r.thumbnail((w, w))
        r.save(out / f'{f.stem}{suf}.webp', 'WEBP', quality=72, method=4)
        if not suf: medidas[f.stem] = [*r.size, huella]
    nuevas += 1
mfile.write_text(json.dumps(dict(sorted(medidas.items())), indent=0))
print(nuevas, 'fotos nuevas ·', len(medidas), 'en total')

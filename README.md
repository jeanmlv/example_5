# example_5


from pathlib import Path
import hashlib

# Localizar a pasta ard_data
PASTA = Path.home() / "OneDrive - JNJ" / "Desktop" / "ard_data"

ZIP = PASTA / "QUASAR_ALL_ARD.zip"
DESTINO = PASTA / "quasar_partes"

TAMANHO_PARTE = 25 * 1024 * 1024  # 25 MiB

if not ZIP.is_file():
    raise FileNotFoundError(f"ZIP não encontrado: {ZIP}")

DESTINO.mkdir(exist_ok=True)

# Evitar misturar partes antigas com novas
if list(DESTINO.glob("QUASAR_ALL_ARD.zip.part*")):
    raise RuntimeError(
        "Já existem partes nesta pasta. "
        "Remova ou mova as partes antigas antes de executar."
    )

sha256 = hashlib.sha256()
numero = 0

with ZIP.open("rb") as origem:
    while True:
        bloco = origem.read(TAMANHO_PARTE)

        if not bloco:
            break

        numero += 1
        sha256.update(bloco)

        nome = f"{ZIP.name}.part{numero:03d}"
        caminho = DESTINO / nome
        caminho.write_bytes(bloco)

        print(f"Criado: {nome} ({len(bloco) / 1024**2:.2f} MiB)")

hash_original = sha256.hexdigest()

(DESTINO / "QUASAR_SHA256.txt").write_text(
    f"{hash_original}  {ZIP.name}\n",
    encoding="utf-8"
)

print(f"\nTotal de partes: {numero}")
print(f"SHA-256: {hash_original}")
print(f"Pasta: {DESTINO}")

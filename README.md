# example_5

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

# Pasta onde estão os ARDs
INPUT = Path.home() / "OneDrive - JNJ" / "Desktop" / "ard_data"

# Identificar automaticamente os ARDs do QUASAR
FILES = sorted(INPUT.glob("*quasar*ard*.xlsx"))

# Arquivo ZIP de saída
OUTPUT = INPUT / "QUASAR_ALL_ARD.zip"

print(f"Pasta: {INPUT}")
print(f"Arquivos encontrados: {len(FILES)}")

for file in FILES:
    print(f" - {file.name}")

if len(FILES) != 6:
    raise RuntimeError(
        f"Esperados 6 arquivos, encontrados {len(FILES)}. "
        "Confira a seleção antes de compactar."
    )

with ZipFile(
    OUTPUT,
    mode="w",
    compression=ZIP_DEFLATED,
    compresslevel=9
) as archive:

    for file in FILES:
        archive.write(file, arcname=file.name)
        print(f"Adicionado: {file.name}")

size_mb = OUTPUT.stat().st_size / (1024 ** 2)

print(f"\nZIP criado com sucesso: {OUTPUT}")
print(f"Tamanho final: {size_mb:.2f} MB")

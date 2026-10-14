# example_5

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

INPUT = Path(
    r"C:\Users\JMende95\OneDrive - JNJ\Desktop\ard_data"
)

FILES = [
    "CNTO1959UC03001_quasar_ind1_wk32_ard_20260619.xlsx",
    "CNTO1959UC03001_quasar_ind2_wk32_ard_20260621.xlsx",
    "CNTO1959UC03001_quasar_maint_wk44_ard_20260616.xlsx",
    "CNTO1959UC03001_quasar_lte_wk92_ard_20261012.xlsx",
    "CNTO1959UC03001_quasar_lte_wk140_ard_20261013.xlsx",
    "CNTO1959UC03001_quasar_lte_wk188_ard_20261013.xlsx",
]

OUTPUT = INPUT / "QUASAR_ALL_ARD.zip"

missing = [name for name in FILES if not (INPUT / name).is_file()]

if missing:
    raise FileNotFoundError(f"Arquivos ausentes: {missing}")

with ZipFile(
    OUTPUT,
    mode="w",
    compression=ZIP_DEFLATED,
    compresslevel=9
) as archive:
    for name in FILES:
        archive.write(INPUT / name, arcname=name)
        print(f"Adicionado: {name}")

size_mb = OUTPUT.stat().st_size / (1024 ** 2)

print(f"\nZIP criado: {OUTPUT}")
print(f"Tamanho: {size_mb:.2f} MB")

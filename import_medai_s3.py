#!/usr/bin/env python3
"""Reusable Med.AI S3 -> Domino importer. Python 3.8+; AWS CLI required.

Credentials are requested with getpass and never written to disk by this script.
Run in a real terminal (not the RStudio console).
"""
import getpass
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit

BASE = Path('/domino/datasets/local/clinical-trial-data')
REGION = 'us-east-1'


def ask(label, secret=False):
    if secret:
        return getpass.getpass(label)
    return input(label).strip()


def parse_s3(value):
    parsed = urlsplit(value.strip())
    if parsed.scheme != 's3' or not parsed.netloc or not parsed.path.strip('/'):
        raise ValueError('Informe um caminho completo s3://bucket/prefixo/')
    if parsed.query or parsed.fragment or '..' in parsed.path.split('/'):
        raise ValueError('Caminho S3 invalido.')
    return 's3://{}/{}/'.format(parsed.netloc, parsed.path.strip('/'))


def main():
    print('\n=== MED.AI S3 -> DOMINO IMPORTER ===')
    source = parse_s3(ask('Cole o S3 Location completo: '))
    name = ask('Nome da pasta de destino (ex. CNTO1959UCO3001-QUASAR-LTE-WK188): ')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,149}', name) or name in ('.', '..'):
        raise ValueError('Nome de pasta invalido: use letras, numeros, -, _ ou ponto.')
    target = BASE / name
    print('\nOrigem: {}'.format(source))
    print('Destino: {}'.format(target))
    if ask('Confirmar caminhos? Digite SIM: ') != 'SIM':
        print('Cancelado.')
        return

    # Copy each credential in Med.AI before responding to the corresponding prompt.
    print('\nGere credenciais temporarias novas no Med.AI.')
    key = ask('Access Key ID (cole e Enter): ', secret=True).strip()
    secret = ask('Secret Access Key (cole e Enter): ', secret=True).strip()
    token = ask('Session Token (cole e Enter): ', secret=True).strip()
    if not all((key, secret, token)):
        raise ValueError('Uma ou mais credenciais estao vazias.')

    env = os.environ.copy()
    # Prevent conflicting AWS profile credentials / role configuration.
    for item in ('AWS_PROFILE', 'AWS_DEFAULT_PROFILE', 'AWS_ROLE_ARN', 'AWS_WEB_IDENTITY_TOKEN_FILE',
                 'AWS_CONTAINER_CREDENTIALS_FULL_URI', 'AWS_CONTAINER_CREDENTIALS_RELATIVE_URI'):
        env.pop(item, None)
    env.update(AWS_ACCESS_KEY_ID=key, AWS_SECRET_ACCESS_KEY=secret,
               AWS_SESSION_TOKEN=token, AWS_DEFAULT_REGION=REGION,
               AWS_EC2_METADATA_DISABLED='true', AWS_PAGER='')
    del key, secret, token

    print('\n1/3 Verificando acesso ao prefixo S3...')
    check = subprocess.run(['aws', 's3', 'ls', source], env=env, check=False)
    if check.returncode:
        raise RuntimeError('Falha de acesso ao S3. Verifique credenciais, expiracao e prefixo.')

    print('\n2/3 Simulando sincronizacao (sem transferir arquivos)...')
    dry = subprocess.run(['aws', 's3', 'sync', source, str(target), '--dryrun', '--no-progress'],
                         env=env, check=False)
    if dry.returncode:
        raise RuntimeError('Falha no dry-run. Nenhum arquivo foi transferido.')

    print('\nA simulacao terminou. Revise os arquivos acima.')
    if ask('Digite TRANSFERIR para baixar os arquivos: ') != 'TRANSFERIR':
        print('Cancelado sem transferencia.')
        return

    target.mkdir(parents=True, exist_ok=True)
    print('\n3/3 Transferindo...')
    result = subprocess.run(['aws', 's3', 'sync', source, str(target), '--no-progress'],
                            env=env, check=False)
    if result.returncode:
        raise RuntimeError('Transferencia com erro. Revise a saida; alguns arquivos podem ter sido copiados.')
    print('\nTransferencia concluida. Pastas no destino:')
    for item in sorted(target.iterdir()):
        print(' - {}'.format(item.name))
    print('\nDestino: {}'.format(target))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, EOFError, KeyboardInterrupt, FileNotFoundError) as exc:
        print('\nErro/cancelamento: {}'.format(exc), file=sys.stderr)
        sys.exit(1)

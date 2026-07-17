import os
import re
import sys
import json
import shutil
import zipfile
import subprocess
from datetime import datetime
from io import BytesIO

import requests


REPO = os.environ.get("GITHUB_REPOSITORY")
RUN_ID = os.environ.get("RUN_ID")
TOKEN = os.environ.get("AUTO_FIX_GH_PAT")
ACTOR = os.environ.get("GITHUB_ACTOR", "auto-fixer")

API_BASE = f"https://api.github.com/repos/{REPO}"


def download_run_logs(run_id):
    url = f"{API_BASE}/actions/runs/{run_id}/logs"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}
    r = requests.get(url, headers=headers, allow_redirects=True, stream=True, timeout=60)
    if r.status_code != 200:
        print(f"Falha ao baixar logs: {r.status_code}")
        return None
    # r.content is a zip archive
    return BytesIO(r.content)


def search_patterns_in_logs(zip_bytes):
    found = set()
    z = zipfile.ZipFile(zip_bytes)
    for name in z.namelist():
        try:
            data = z.read(name).decode('utf-8', errors='ignore')
        except Exception:
            continue
        if "version '3.1' with architecture" in data or re.search(r"version '\d+\.\d+' with architecture", data):
            found.add('quote-python-versions')
        if "Unrecognized named-value: 'secrets'" in data or "Unrecognized named-value: secrets" in data:
            found.add('remove-secrets-in-if')
        if "coverage.xml" in data and "No files were found with the provided path: coverage.xml" in data:
            found.add('coverage-missing-artifact')
    return list(found)


def apply_fix_quote_versions(path):
    with open(path, 'r', encoding='utf-8') as f:
        txt = f.read()
    new = re.sub(r"python-version:\s*\[(.*?)\]",
                 lambda m: "python-version: [" + ", ".join([f"'{s.strip()}" + "'" if not s.strip().startswith("'") else s.strip() for s in m.group(1).split(',')]) + "]",
                 txt)
    if new != txt:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new)
        return True
    return False


def apply_fix_remove_secrets_if(path):
    with open(path, 'r', encoding='utf-8') as f:
        txt = f.read()
    new = re.sub(r"if:\s*\${{[^}]*secrets\.[^}]*}}\s*",
                 "if: ${{ github.event.repository.private == false }}\n",
                 txt)
    # also handle more specific pattern
    new = new.replace("${{ secrets.CODECOV_TOKEN != '' || github.event.repository.private == false }}", "${{ github.event.repository.private == false }}")
    if new != txt:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new)
        return True
    return False


def make_branch_and_pr(changes_desc):
    ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    branch = f"autofix/{ts}"
    subprocess.run(['git', 'config', 'user.name', ACTOR], check=True)
    subprocess.run(['git', 'config', 'user.email', f"{ACTOR}@users.noreply.github.com"], check=True)
    subprocess.run(['git', 'checkout', '-b', branch], check=True)
    subprocess.run(['git', 'add', '.github/workflows/ci.yml'], check=True)
    subprocess.run(['git', 'commit', '-m', f"Auto-fix: {changes_desc}"], check=True)
    remote_url = f"https://{TOKEN}@github.com/{REPO}.git"
    subprocess.run(['git', 'push', '--set-upstream', remote_url, branch], check=True)
    # create PR
    pr_title = f"Auto-fix: {changes_desc}"
    pr_body = "This PR was created automatically by the Auto Fixer workflow after detecting failures in a previous run. Please review."
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}
    data = {"title": pr_title, "head": branch, "base": "main", "body": pr_body}
    r = requests.post(f"{API_BASE}/pulls", headers=headers, json=data, timeout=30)
    if r.status_code in (200,201):
        pr = r.json()
        print(f"PR criado: {pr.get('html_url')}")
    else:
        print(f"Falha ao criar PR: {r.status_code} {r.text}")


def main():
    if not TOKEN or not REPO or not RUN_ID:
        print("Variáveis necessárias ausentes. Saindo.")
        sys.exit(0)

    # avoid acting on Auto Fixer runs
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}
    rr = requests.get(f"{API_BASE}/actions/runs/{RUN_ID}", headers=headers, timeout=30)
    if rr.status_code != 200:
        print("Não foi possível obter informações do run")
        sys.exit(0)
    run_info = rr.json()
    workflow_name = run_info.get('name', '')
    if 'Auto Fixer' in workflow_name or 'auto-fix' in workflow_name:
        print("Run do Auto Fixer detectado — evitando loop.")
        sys.exit(0)

    print("Baixando logs do run...")
    zip_bytes = download_run_logs(RUN_ID)
    if not zip_bytes:
        print("Não há logs disponíveis")
        sys.exit(0)

    patterns = search_patterns_in_logs(zip_bytes)
    print("Padrões detectados:", patterns)
    if not patterns:
        print("Nenhuma condição conhecida encontrada para auto-correção.")
        sys.exit(0)

    path = '.github/workflows/ci.yml'
    changed = False
    descs = []
    if 'quote-python-versions' in patterns:
        ok = apply_fix_quote_versions(path)
        if ok:
            changed = True
            descs.append('quote-python-versions')
    if 'remove-secrets-in-if' in patterns:
        ok = apply_fix_remove_secrets_if(path)
        if ok:
            changed = True
            descs.append('remove-secrets-in-if')

    if changed:
        make_branch_and_pr(','.join(descs))
    else:
        print('Nenhuma alteração aplicada.')


if __name__ == '__main__':
    main()

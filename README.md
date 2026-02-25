# Immich Infrastructure Stack

Kompletna infrastruktura dla Immich i usług towarzyszących, uruchamiana jako zestaw
Docker Compose na maszynie wirtualnej działającej na Proxmox.

- **Host:** Proxmox  
- **Node:** theBrain  
- **VM ID:** 495  
- **Lokalizacja stacku:** `/opt`

Projekt zaprojektowany tak, aby był przenośny, powtarzalny i stabilny — z własnym
hookiem `pre-commit`, oddzielnymi konfiguracjami i pełną izolacją danych
wyłączonych z repozytorium.

---

## Table of Contents

- #struktura-repo
- [Wymagania](#wymagania)
- [Instalacja](#instalacja)
- #konfiguracja-środowiska
- [Opis usług](#opis-usług)
- #uruchamianie-usług
- [Backup i restore](#backup-i-restore)
- [Hook pre‑commit](#hook-pre-commit)
- [Aktualizacje](#aktualizacje)
- #rozwiązywanie-problemów
- [Licencja](#licencja)

---

## Struktura repo
/opt
├── generate_env_example.py        # Generator szablonu .env
├── hawser/                        # Warstwa komunikacyjna dla Dockhand
│   └── docker-compose.yaml
├── immich/
│   ├── backup/                    # Backupy bazy (wykluczone z repo)
│   └── docker-compose.yaml
├── immich-power-tools/            # Narzędzia administracyjne Immich
│   ├── docker-compose.yml
│   └── immich.code-workspace
├── pre_commit_hook.py             # Walidacje przed commitem
└── stacks/

Pliki danych, wolumenów i zmienne środowiskowe (`.env*`) są ignorowane przez `.gitignore`.

---

## Wymagania

- Linux (Proxmox VM)
- Docker + Docker Compose v2
- Python 3.x
- Uprawnienia zapisu w `/opt`

---

## Instalacja

*(sekcja pozostawiona pusta dokładnie tak, jak ją zostawiłeś — możesz uzupełnić później)*

---

## Konfiguracja środowiska

Każdy stack (`immich`, `hawser`, `immich-power-tools`) używa własnego pliku `.env`.

### Generowanie przykładowego `.env`


cd /opt
python3 generate_env_example.py > .env.example

Następnie w każdym katalogu:


cd /opt/immich
cp ../.env.example .env
nano .env

Przykładowe wartości:


TZ=Europe/Warsaw
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
DB_NAME=

Pliki `.env` są wyłączone z repozytorium.

---

## Opis usług

### Immich
Główna aplikacja do zarządzania zdjęciami i filmami, działająca w oparciu o PostgreSQL, backend i frontend.

### Immich Power Tools
Zestaw narzędzi dla administratora Immich, służących do diagnostyki i utrzymania.

### Hawser
Warstwa pośrednia do komunikacji z Dockhand — pełni rolę mostu i integratora usług.

---

## Uruchamianie usług

### Immich


cd /opt/immich
docker compose pull
docker compose up -d
docker compose ps

Logi:


docker compose logs -f --tail=200

### Hawser


cd /opt/hawser
docker compose up -d

### Immich Power Tools


cd /opt/immich-power-tools
docker compose up -d

### Restart / Stop / Down


docker compose restart
docker compose stop
docker compose down

---

## Backup i restore

Katalog `immich/backup/` jest ignorowany przez Git i przeznaczony na dumpy.

### Backup bazy Immich


cd /opt/immich
DATE=$(date +%F)
docker compose exec -T postgres pg_dump -U "$DB_USER" "$DB_NAME" 
| gzip > backup/db-$DATE.sql.gz

### Restore


cd /opt/immich
gunzip -c backup/db-YYYY-MM-DD.sql.gz 
| docker compose exec -T postgres psql -U "$DB_USER" -d "$DB_NAME"

---

## Hook pre‑commit

Repozytorium używa własnego mechanizmu walidacji przed każdym commitem.

### Instalacja hooka


cat > .git/hooks/pre-commit <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
python3 pre_commit_hook.py
EOF
chmod +x .git/hooks/pre-commit

---

## Aktualizacje
### Dockhand lub manualnie


cd /opt/immich
docker compose pull
docker compose up -d
docker compose logs -f --tail=200

---

## Rozwiązywanie problemów


---

## Licencja


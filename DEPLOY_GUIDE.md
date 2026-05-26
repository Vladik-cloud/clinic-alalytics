# Деплой с нуля: пошагово для новичка

## Что такое VPS

**VPS** — это удалённый компьютер в интернете (Linux), который работает 24/7.  
Вы арендуете его у хостинга (~300–500 ₽/мес), заходите по SSH с Mac и запускаете там Docker с вашим проектом.

Проверяющий откроет в браузере **ваш домен** → увидит отчёт.

---

## Шаг 0. Что должно быть готово на Mac

- [x] Проект работает локально: `make up` → http://localhost:3000
- [x] Файл дампа: `data/dump.dump` (~111 MB)
- [x] Код на GitHub: https://github.com/Vladik-cloud/clinic-alalytics

---

## Можно ли бесплатно?

**Да, но не «вообще без регистрации».** Нужен хотя бы один из вариантов:

| Вариант | Цена | Подходит для ТЗ? | Минусы |
|---------|------|------------------|--------|
| **Oracle Cloud Free** | 0 ₽ навсегда* | ✅ Лучший бесплатный | Регистрация с картой, иногда капризный signup |
| **Hetzner / Timeweb** | ~300–500 ₽/мес | ✅ Проще всего | Не бесплатно |
| **Cloudflare Tunnel** с Mac | 0 ₽ | ⚠️ Спорно | Mac должен быть включён; это не классический VPS |
| **Render / Railway** | лимиты | ⚠️ Сложно | Наш `docker-compose` + дамп 111 MB — неудобно |

\*Always Free: VM до ~4 CPU / 24 GB RAM (ARM), хватает с запасом.

**Для сдачи ТЗ** проверяющему обычно нужна **стабильная ссылка https://...** — это даёт VPS (платный или Oracle Free).

Домен бесплатно: **sslip.io** (см. шаг 2) — покупать `.ru` не обязательно.

---

## Шаг 1. Арендовать VPS (15 минут)

Любой провайдер с Ubuntu и Docker. Примеры:

| Провайдер | Сайт | Что выбрать |
|-----------|------|-------------|
| Timeweb | timeweb.cloud | VPS, Ubuntu 22.04, 2 GB RAM |
| Selectel | selectel.ru | Облачный сервер, Ubuntu |
| Hetzner | hetzner.com | CX22 (если карта проходит) |
| **Oracle Cloud (бесплатно)** | cloud.oracle.com | Always Free → Ubuntu ARM VM, 2+ GB RAM |

### Oracle Cloud Free (если хотите 0 ₽)

1. Зарегистрируйтесь на https://cloud.oracle.com (нужна карта, списания нет на Always Free).
2. Compute → Instances → Create — **Ampere A1**, 2 OCPU, 12 GB RAM (в пределах free).
3. Image: **Ubuntu 22.04**.
4. Скачайте SSH-ключ или задайте пароль.
5. Public IP — это ваш `ВАШ_IP` для `ssh` и `scp`.

Дальше — те же шаги 3–9 ниже.

При создании сервера:

1. ОС: **Ubuntu 22.04**
2. RAM: **минимум 2 GB**
3. Диск: **20 GB**
4. Запомните **IP-адрес** (например `185.12.34.56`)
5. Запомните **логин** (часто `root` или `ubuntu`) и **пароль** (или загрузите SSH-ключ)

---

## Шаг 2. Домен (для HTTPS) — 10 минут

Проверяющему нужна ссылка вида `https://что-то.ru`, не просто IP.

**Вариант A — свой домен** (Reg.ru, Timeweb, Namecheap):

1. Купите домен, например `clinic-analytics.ru`
2. В DNS добавьте запись:
   - Тип: **A**
   - Имя: `@` (или `www`)
   - Значение: **IP вашего VPS**
3. Подождите 5–30 минут

**Вариант B — бесплатно без покупки** (для теста):

Если IP VPS = `185.12.34.56`, домен будет:

`185-12-34-56.sslip.io`

(точки в IP заменяете на дефисы). A-запись настраивать не нужно — он уже указывает на ваш IP.

В `.env` на сервере тогда:

`CORS_ORIGINS=https://185-12-34-56.sslip.io`

---

## Шаг 3. Подключиться к VPS с Mac (2 минуты)

В терминале на Mac:

```bash
ssh root@185.12.34.56
```

(подставьте свой IP и логин; при первом входе напишите `yes`, введите пароль)

Вы внутри сервера, приглашение вида `root@server:~#`.

---

## Шаг 4. Установить Docker на VPS (5 минут)

На сервере (после `ssh`):

```bash
apt update
apt install -y git docker.io docker-compose
```

Если `docker-compose-plugin` не находится (часто на CloudVPS / ISPmanager) — используйте `docker-compose` (с дефисом) вместо `docker compose`.

Если логин не `root`, ещё:

```bash
usermod -aG docker $USER
exit
```

и снова `ssh ...` (чтобы группа docker применилась).

---

## Шаг 5. Скачать проект на VPS (2 минуты)

На сервере:

```bash
git clone https://github.com/Vladik-cloud/clinic-alalytics.git
cd clinic-alalytics
cp .env.example .env
nano .env
```

В nano измените:

```
POSTGRES_PASSWORD=любой-длинный-секрет-123
CORS_ORIGINS=https://ВАШ-ДОМЕН
```

Сохранить: `Ctrl+O`, Enter, `Ctrl+X`.

---

## Шаг 6. Загрузить дамп с Mac на VPS (5–15 минут)

**Новое окно терминала на Mac** (не закрывая SSH, или закройте ssh — не важно):

```bash
cd /Users/uladzik/Desktop/Projects/clinic-alalytics
scp data/dump.dump root@185.12.34.56:~/clinic-alalytics/data/dump.dump
```

(замените IP и пользователя)

---

## Шаг 7. Запустить приложение на VPS (10–20 минут)

Снова зайдите на сервер: `ssh root@185.12.34.56`

```bash
cd ~/clinic-alalytics
chmod +x scripts/deploy-on-server.sh
./scripts/deploy-on-server.sh
```

Первый раз Postgres **импортирует дамп** — может занять 10–15 минут. Смотреть прогресс:

```bash
docker-compose -f docker-compose.vps.yml logs -f db
```

Ждёте строку: `Database initialization complete`.

Проверка на сервере:

```bash
curl -s http://127.0.0.1:3000/api/health
```

Должно быть что-то вроде `{"status":"ok",...}`.

---

## Шаг 8. Включить HTTPS (Caddy) (10 минут)

На сервере:

```bash
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update && apt install -y caddy
nano /etc/caddy/Caddyfile
```

Содержимое (одна строка домена — ваш):

```
ваш-домен.ru {
    reverse_proxy 127.0.0.1:3000
}
```

Для sslip.io:

```
185-12-34-56.sslip.io {
    reverse_proxy 127.0.0.1:3000
}
```

```bash
systemctl reload caddy
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable
```

Откройте в браузере на Mac: **https://ваш-домен.ru** — должен открыться отчёт.

---

## Шаг 9. Что отправить проверяющему

1. Ссылка на сайт: `https://ваш-домен.ru`
2. Ссылка на GitHub: `https://github.com/Vladik-cloud/clinic-alalytics`

Дамп и пароли **не** отправляете.

Подробный шаблон письма: [SUBMISSION.md](./SUBMISSION.md)

---

## Если что-то сломалось

| Симптом | Что сделать |
|---------|-------------|
| `ssh: connection refused` | Проверьте IP, включён ли сервер в панели хостинга |
| `Permission denied` | Неверный пароль / нужен SSH-ключ из панели |
| Отчёт пустой / 5 врачей | Дамп не залили → повторите шаг 6 и 7 с `./scripts/deploy-on-server.sh` |
| 502 / не открывается сайт | `docker compose ... ps` — все healthy? Caddy настроен? |
| Долго «грузится» | Импорт дампа ещё идёт → `logs -f db` |

---

## Краткая схема

```
Mac                          VPS (облако)
───                          ────────────
data/dump.dump  ──scp──►     ~/clinic-alalytics/data/
git push        ──────►      git clone
                             docker compose up
                             Caddy → https://домен
                                      ▲
Проверяющий ──────────────────────────┘ открывает в браузере
```

# Что отправить проверяющему

1. **Работающий сервис:** http://62-182-102-237.sslip.io  
   Отчёт: выручка врачей и перенаправляемость, фильтр по датам (дамп ClinicIQ).

2. **Репозиторий:** https://github.com/Vladik-cloud/clinic-alalytics

3. **Запуск локально:**
   ```bash
   git clone https://github.com/Vladik-cloud/clinic-alalytics.git
   cd clinic-alalytics
   # data/dump.dump — не в git, положить вручную
   make up
   open http://localhost:3000
   ```

4. **Тесты:** `make test`, `make test-integration`

5. **Архитектура:** `ARCHITECTURE.md`

Не отправлять: `data/dump.dump`, `.env`, пароли SSH.

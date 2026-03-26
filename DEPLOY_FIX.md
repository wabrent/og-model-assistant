# 🚀 Quick Deploy Fix

## Проблема
На Render **0 models available** — модели не загружаются автоматически при старте.

## Решение
Добавлена **автосинхронизация** при старте приложения в `main.py`.

## Что изменено
- ✅ `main.py` — добавлена автосинхронизация моделей при старте
- ✅ При запуске приложение автоматически загрузит все модели из OpenGradient API
- ✅ Если синхронизация не пройдёт — будет лог с ошибкой и инструкцией

---

## 📤 Как задеплоить

### Вариант 1: Через Git (рекомендуется)

```bash
cd og-model-assistant-pro

# Проверить изменения
git status

# Закоммитить изменения
git add main.py
git commit -m "fix: add auto-sync on startup to load models"

# Запушить (триггерит автодеплей на Render)
git push origin main
```

### Вариант 2: Через Render Dashboard

1. Зайти на https://dashboard.render.com
2. Выбрать сервис `og-model-assistant`
3. Нажать **Manual Deploy** → **Deploy Latest Commit**
4. Или подключить репозиторий если ещё не подключён

---

## ✅ Как проверить

После деплоя:

1. **Проверить логи:**
   ```
   Render Dashboard → Logs
   ```
   Искать строки:
   - `🔄 Starting initial model sync...`
   - `✅ Initial model sync completed!`

2. **Проверить API:**
   ```bash
   curl https://og-model-assistant.onrender.com/api/sync/status
   ```
   
   Ожидаемый ответ:
   ```json
   {
     "is_syncing": false,
     "last_sync_at": "2026-03-26T...",
     "models_count": 2247,
     "status": "idle"
   }
   ```

3. **Проверить главную:**
   ```
   https://og-model-assistant.onrender.com/
   ```
   Должно показывать **2,247+ AI моделей** вместо "0 models"

---

## 🔧 Ручная синхронизация (если нужно)

Если автосинхронизация не сработала:

```bash
# Через API
curl -X POST https://og-model-assistant.onrender.com/api/sync/trigger

# Или через Swagger UI
https://og-model-assistant.onrender.com/docs
```

---

## 🐛 Возможные проблемы

### 1. Таймаут при синхронизации
**Проблема:** Синхронизация 2247 моделей занимает ~30-60 секунд

**Решение:** Render может убить процесс по таймауту. Нужно:
- Увеличить таймаут в Render Dashboard
- Или запускать синхронизацию в background task

### 2. Ошибка PRIVATE_KEY
**Проблема:** Нет доступа к OpenGradient API

**Решение:** Проверить в Render Dashboard → Environment:
```
PRIVATE_KEY=0x807aa72bd90119bf8ef49a201ded88326ca2812fc2430f8d1cafff342a707e65
```

### 3. Пустая база данных
**Проблема:** PostgreSQL создаётся с нуля при каждом деплое

**Решение:** Использовать persistent disk для БД (платная функция Render)
ИЛИ запускать синхронизацию после каждого деплоя

---

## 📊 Ожидаемый результат

После успешного деплоя:
- ✅ **2,247 моделей** загружено
- ✅ Поиск работает
- ✅ Чат работает
- ✅ Аналитика работает

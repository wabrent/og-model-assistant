# 📘 Инструкция для Qwen Code (Следующие Сессии)

## 🎯 О Проекте

**OpenGradient Model Hub Assistant** — AI-ассистент для поиска моделей в OpenGradient Hub.

**Стек:**
- Backend: FastAPI + SQLAlchemy (SQLite)
- Frontend: Vanilla JS + CSS (один файл index.html)
- AI: OpenGradient API (GROK-4-Fast)
- Деплой: Render.com (бесплатный тариф)

**URL:** https://og-model-assistant.onrender.com/

---

## ✅ ЧТО УЖЕ РЕАЛИЗОВАНО (НЕ МЕНЯТЬ!)

### Рабочие функции:
1. ✅ **Умный поиск моделей** — `/api/models/search`
2. ✅ **AI Чат** — `/api/chat` (GROK-4-Fast)
3. ✅ **Голосовой ввод** — Web Speech API
4. ✅ **Дашборд пользователя** — уровни, XP, статистика
5. ✅ **Система достижений** — 10 достижений
6. ✅ **Live статус моделей** — зелёные/красные индикаторы
7. ✅ **Токены + Faucet** — 0.1 OPG каждые 5 часов
8. ✅ **Мобильная версия** — responsive design
9. ✅ **Анимации** — карточки, кнопки, уведомления

### Последние коммиты:
```bash
git log -5 --oneline
# 573fb64 fix: handle missing model_statuses table gracefully
# 3acabee fix: add cache busting version
# 7ab1905 feat: add live model status indicators
# ce32c9d feat: add user dashboard, stats tracking and achievements system
```

---

## 📁 СТРУКТУРА ПРОЕКТА

```
opengradientapp/
└── og-model-assistant-pro/
    ├── api/                      # API роутеры
    │   ├── models_router.py      # Поиск моделей
    │   ├── chat_router.py        # AI чат
    │   ├── analytics_router.py   # Статистика
    │   ├── sync_router.py        # Синхронизация
    │   ├── tokens_router.py      # Токены/faucet
    │   ├── user_stats_router.py  # Дашборд/достижения
    │   └── model_status_router.py # Live статус (НОВЫЙ!)
    ├── services/                 # Бизнес-логика
    │   ├── opengradient_service.py
    │   ├── model_service.py
    │   ├── chat_service.py
    │   ├── token_service.py
    │   ├── user_stats_service.py # Дашборд
    │   └── model_status_service.py # Статус (НОВЫЙ!)
    ├── models/
    │   └── db_models.py          # SQLAlchemy модели
    ├── static/
    │   └── index.html            # ВЕСЬ FRONTEND (один файл!)
    ├── main.py                   # FastAPI приложение
    ├── requirements.txt          # Зависимости
    └── .env                      # Переменные окружения
```

---

## ⚠️ КРИТИЧЕСКИ ВАЖНО (НЕ ЛОМАТЬ!)

### 1. **База Данных — SQLite**
```python
DATABASE_URL=sqlite+aiosqlite:///./og_assistant.db
```
- **НЕ менять на PostgreSQL** без необходимости
- Render использует SQLite на бесплатном тарифе
- Таблицы: `models`, `user_tokens`, `user_stats`, `user_achievements`, `model_statuses`

### 2. **OpenGradient API**
```python
PRIVATE_KEY=0x807aa72bd90119bf8ef49a201ded88326ca2812fc2430f8d1cafff342a707e65
```
- Используется для доступа к OpenGradient Hub API
- **OPG approval: 1.0** (не 10.0! экономим токены)
- Faucet: 0.1 OPG каждые 5 часов (официальный лимит)

### 3. **Frontend — ОДИН ФАЙЛ**
- `static/index.html` — **ВЕСЬ frontend в одном файле**
- CSS в `<style>` (1400+ строк)
- JS в `<script>` (600+ строк)
- **НЕ разделять** на отдельные файлы!

### 4. **Render Деплой**
- Автосборка при `git push`
- Команда: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Кэш браузера** — добавлять `?v=2` к статике
- **Таблицы БД** создаются через `init_db()` при старте

---

## 🚀 КАК ДОБАВЛЯТЬ НОВЫЕ ФУНКЦИИ

### Правильный порядок:

1. **Модель БД** (если нужно)
   ```python
   # models/db_models.py
   class NewFeature(Base):
       __tablename__ = "new_features"
       id = Column(Integer, primary_key=True)
       # ...
   ```

2. **Сервис**
   ```python
   # services/new_feature_service.py
   class NewFeatureService:
       async def do_something(self, db: AsyncSession):
           # ...
   ```

3. **API Router**
   ```python
   # api/new_feature_router.py
   router = APIRouter(prefix="/api/new-feature", tags=["New Feature"])
   
   @router.get("")
   async def get_feature(db: AsyncSession = Depends(get_db)):
       # ...
   ```

4. **Добавить в main.py**
   ```python
   from api.new_feature_router import router as new_feature_router
   app.include_router(new_feature_router)
   ```

5. **Frontend** (в index.html)
   - CSS в `<style>`
   - HTML в нужную секцию
   - JS в `<script>`

6. **Коммит и пуш**
   ```bash
   git add -A
   git commit -m "feat: описание新功能"
   git push origin main
   ```

---

## ❌ ЧТО НЕ ДЕЛАТЬ (ОШИБКИ)

### 1. **НЕ менять структуру БД без миграций**
```python
# ❌ ПЛОХО: Добавить поле без проверки
class Model(Base):
    new_field = Column(String)  # Ошибка если таблица есть!

# ✅ ХОРОШО: Использовать try/except
try:
    result = await db.execute(select(NewTable))
except:
    # Таблицы нет — создать или вернуть default
    return []
```

### 2. **НЕ разделять index.html**
```bash
# ❌ ПЛОХО: Создать separate CSS/JS файлы
static/css/style.css
static/js/app.js

# ✅ ХОРОШО: Всё в index.html
<style>...</style>
<script>...</script>
```

### 3. **НЕ использовать сложные зависимости**
```python
# ❌ ПЛОХО: Добавлять тяжелые библиотеки
pip install tensorflow pandas numpy

# ✅ ХОРОШО: Использовать встроенные или легкие
pip install httpx  # для HTTP запросов
```

### 4. **НЕ ломать совместимость с Render Free**
```python
# ❌ ПЛОХО: Требовать PostgreSQL/Redis
DATABASE_URL=postgresql://...  # Нет на free тарифе!

# ✅ ХОРОШО: SQLite по умолчанию
DATABASE_URL=sqlite+aiosqlite:///./og_assistant.db
```

---

## 🛠️ ЧАСТЫЕ ЗАДАЧИ (ГОТОВЫЕ РЕШЕНИЯ)

### Добавить новую таблицу в БД:
```python
# 1. models/db_models.py
class NewTable(Base):
    __tablename__ = "new_tables"
    id = Column(Integer, primary_key=True)

# 2. main.py (создать при старте)
await init_db()  # Уже есть — таблицы создадутся автоматически
```

### Добавить API endpoint:
```python
# api/new_router.py
from fastapi import APIRouter, Depends
from core.database import get_db

router = APIRouter(prefix="/api/new", tags=["New"])

@router.get("")
async def get_new(db: AsyncSession = Depends(get_db)):
    return {"message": "OK"}

# main.py
from api.new_router import router as new_router
app.include_router(new_router)
```

### Добавить UI элемент:
```html
<!-- static/index.html -->
<!-- 1. CSS в <style> -->
.new-button {
    background: var(--gradient-1);
    padding: 12px 24px;
    border-radius: 20px;
}

<!-- 2. HTML в нужную секцию -->
<button class="new-button" onclick="doSomething()">Click Me</button>

<!-- 3. JS в <script> -->
async function doSomething() {
    const r = await fetch('/api/new');
    const data = await r.json();
    showToast('✅', 'Done!');
}
```

---

## 📊 ТЕКУЩИЕ API ENDPOINTS

```
GET  /api/health              # Health check
GET  /api/models              # Все модели
POST /api/models/search       # Поиск моделей
GET  /api/models/status       # Live статус (НОВЫЙ!)
POST /api/chat                # AI чат
GET  /api/analytics/stats     # Статистика
GET  /api/user/stats          # Дашборд пользователя
GET  /api/user/achievements   # Достижения
POST /api/tokens/faucet/claim # Claim faucet
GET  /api/tokens/balance      # Баланс токенов
POST /api/sync/trigger        # Синхронизация моделей
```

---

## 🐛 ОТЛАДКА

### Проверить логи на Render:
1. https://dashboard.render.com
2. Выбрать сервис `og-model-assistant`
3. Вкладка **Logs**

### Локальные логи:
```bash
# Включить debug логи
LOG_LEVEL=DEBUG python main.py

# Логи в папке logs/
logs/app_2026-03-27.log
logs/error_2026-03-27.log
```

### Проверить БД:
```python
import asyncio
from core.database import async_session_maker
from models.db_models import Model

async def check_db():
    async with async_session_maker() as db:
        # Проверить таблицу
        result = await db.execute(select(Model).limit(1))
        print(result.scalars().all())

asyncio.run(check_db())
```

---

## 📞 КОНТАКТЫ (ЕСЛИ ЧТО-ТО НЕ ПОНЯТНО)

**GitHub:** https://github.com/wabrent/og-model-assistant  
**Render:** https://og-model-assistant.onrender.com  
**OpenGradient:** https://hub.opengradient.ai

---

## 💡 СОВЕТЫ

1. **Всегда проверяй `git status`** перед коммитом
2. **Тестируй локально** перед пушем на Render
3. **Добавляй `?v=2`** к статике для сброса кэша
4. **Используй try/except** для новых таблиц БД
5. **Смотри логи** если что-то не работает

---

**Удачи! 🚀**

*Последнее обновление: 27 марта 2026*

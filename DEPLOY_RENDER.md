# 🚀 Деплой на Render.com — Пошаговая инструкция

## 📋 Шаг 1: Подготовка

### 1.1. Создайте аккаунт на Render
1. Перейдите на https://render.com
2. Click **"Sign Up"**
3. Войдите через **GitHub** (рекомендуется) или email

### 1.2. Подготовьте репозиторий
Ваш проект должен быть на GitHub:
```bash
cd c:\Users\waabrent\Documents\trae_projects\opengradientapp\og-model-assistant-pro
git init
git add .
git commit -m "Initial commit for Render deployment"
git branch -M main
git remote add origin <ваш-repo-url>
git push -u origin main
```

---

## 📋 Шаг 2: Создание Web Service

### 2.1. Создайте новый сервис
1. В дашборде Render click **"New +"** → **"Web Service"**
2. Выберите **"Connect a repository"**
3. Выберите ваш репозиторий `og-model-assistant-pro`

### 2.2. Заполните настройки

| Поле | Значение |
|------|----------|
| **Name** | `og-model-assistant` |
| **Region** | `Frankfurt (Germany)` |
| **Branch** | `main` |
| **Root Directory** | (оставьте пустым) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python main.py` |

### 2.3. Выберите тариф
- **Instance Type**: `Free` ($0/мес)

---

## 📋 Шаг 3: Environment Variables

Click **"Environment"** → **"Add Environment Variable"**:

```bash
# OpenGradient
PRIVATE_KEY=0x807aa72bd90119bf8ef49a201ded88326ca2812fc2430f8d1cafff342a707e65

# Database (Render создаст автоматически)
DATABASE_URL=<сгенерируется автоматически>

# Redis (Render создаст автоматически)
REDIS_URL=<сгенерируется автоматически>

# API
API_HOST=0.0.0.0
API_PORT=10000

# Bots (если нужны)
TELEGRAM_BOT_TOKEN=ваш_токен
DISCORD_BOT_TOKEN=ваш_токен

# Logging
LOG_LEVEL=INFO
```

> ⚠️ **Важно**: Render автоматически создаст PostgreSQL и Redis. Скопируйте их URL после создания!

---

## 📋 Шаг 4: Создание базы данных

### 4.1. Создайте PostgreSQL
1. В дашборде click **"New +"** → **"PostgreSQL"**
2. Name: `og-assistant-db`
3. Region: `Frankfurt`
4. Plan: `Free`
5. Click **"Create Database"**

### 4.2. Скопируйте DATABASE_URL
После создания:
1. Перейдите в созданную базу
2. Скопируйте **Internal Database URL**
3. Вставьте в Environment Variables вашего Web Service

### 4.3. Создайте Redis
1. В дашборде click **"New +"** → **"Redis"**
2. Name: `og-assistant-redis`
3. Region: `Frankfurt`
4. Plan: `Free`
5. Click **"Create Database"**

### 4.4. Скопируйте REDIS_URL
1. Перейдите в созданный Redis
2. Скопируйте **Internal Database URL**
3. Вставьте в Environment Variables

---

## 📋 Шаг 5: Деплой

1. Click **"Create Web Service"**
2. Ждите 3-5 минут (лог деплоя внизу)
3. После успеха получите URL: `https://og-model-assistant-xxxx.onrender.com`

---

## 📋 Шаг 6: Проверка

Откройте в браузере:
- **Главная**: `https://og-model-assistant-xxxx.onrender.com/`
- **API Health**: `https://og-model-assistant-xxxx.onrender.com/api/health`
- **Docs**: `https://og-model-assistant-xxxx.onrender.com/docs`

---

## ⚠️ Возможные проблемы

### ❌ Ошибка: "Build failed"
**Решение**: Проверьте логи, убедитесь что `requirements.txt` корректен

### ❌ Ошибка: "Database connection failed"
**Решение**: Проверьте DATABASE_URL в Environment Variables

### ❌ Ошибка: "Redis connection failed"
**Решение**: Проверьте REDIS_URL в Environment Variables

### ❌ Сервис "засыпает"
**Решение**: Настройте UptimeRobot (см. инструкцию ниже)

---

## 🎯 Готово!

Ваш проект работает на Render! 🎉

URL: `https://og-model-assistant-xxxx.onrender.com`

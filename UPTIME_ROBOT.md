# ⏰ UptimeRobot — Чтобы сервис не засыпал

Render засыпает через **15 минут** без активности. UptimeRobot будет пинговать сервис каждые 5 минут!

---

## 📋 Шаг 1: Регистрация

1. Перейдите на https://uptimerobot.com/
2. Click **"Sign Up"**
3. Зарегистрируйтесь через email (бесплатно)

---

## 📋 Шаг 2: Создание монитора

### 2.1. Добавьте новый монитор
1. В дашборде click **"Add New Monitor"**
2. Заполните:

| Поле | Значение |
|------|----------|
| **Friendly Name** | `OG Model Assistant` |
| **Monitor Type** | `HTTP(s)` |
| **URL** | `https://og-model-assistant-xxxx.onrender.com/api/health` |
| **Monitoring Interval** | `5 minutes` |

### 2.2. Advanced Settings (опционально)
- **Timeout**: 30 секунд
- **HTTP Method**: GET

### 2.3. Сохраните
Click **"Create Monitor"**

---

## 📋 Шаг 3: Проверка

Через 5-10 минут:
1. Статус изменится на **"Up"** ✅
2. Ваш Render-сервис не будет засыпать!

---

## 🎯 Как это работает

```
UptimeRobot → каждые 5 мин → /api/health
                                    ↓
                              Render просыпается
                                    ↓
                              Сервис работает ⚡
```

---

## ⚠️ Важно

- **Бесплатно**: 50 мониторов, интервал от 5 мин
- **Не ставьте интервал < 5 мин** — это платный тариф
- **Используйте /api/health** — это быстрый endpoint

---

## 🔄 Альтернативы

### Cron-Job.org
https://cron-job.org/ru/
- Бесплатно: 10 проверок каждые 5 мин
- Интерфейс на русском

### Self-hosted скрипт
Если есть свой сервер:
```bash
*/5 * * * * curl https://og-model-assistant-xxxx.onrender.com/api/health
```

---

## ✅ Готово!

Теперь ваш сервис **никогда не заснёт**! 🎉

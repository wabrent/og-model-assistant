# 🚀 Deploy to Vercel (FREE - No Sleep!)

## Почему Vercel?

| Render (Free) | Vercel (Free) |
|---------------|---------------|
| ❌ Засыпает через 15 мин | ✅ Всегда активен |
| ❌ 30-60 сек пробуждение | ✅ Мгновенный ответ |
| ❌ Ограничения CPU | ✅ Без ограничений |
| ✅ $7/мес за без сна | ✅ **Бесплатно** |

---

## 📤 Деплой за 5 минут

### Шаг 1: Установи Vercel CLI

```bash
npm install -g vercel
```

Или скачай с https://vercel.com/download

---

### Шаг 2: Залогинься

```bash
vercel login
```

Выбери GitHub (рекомендуется).

---

### Шаг 3: Задеплой

```bash
cd og-model-assistant-pro
vercel
```

**Первый деплой:**
- Ответь на вопросы:
  - `Set up and deploy?` → **Yes**
  - `Which scope?` → Выбери аккаунт
  - `Link to existing project?` → **No**
  - `What's your project's name?` → **og-model-assistant**
  - `In which directory is your code?` → **.**
  - `Want to override settings?` → **No**

---

### Шаг 4: Настрой переменные окружения

После первого деплоя:

```bash
vercel env add PRIVATE_KEY
# Вставь: 0x807aa72bd90119bf8ef49a201ded88326ca2812fc2430f8d1cafff342a707e65
# Выбери: Production, Development, Preview

vercel env add DATABASE_URL
# Вставь: sqlite+aiosqlite:///./og_assistant.db
# Выбери: Production, Development, Preview
```

**Или через Dashboard:**
1. https://vercel.com/dashboard
2. Выбери проект `og-model-assistant`
3. Settings → Environment Variables
4. Добавь:
   - `PRIVATE_KEY` = `0x807aa72bd90119bf8ef49a201ded88326ca2812fc2430f8d1cafff342a707e65`
   - `DATABASE_URL` = `sqlite+aiosqlite:///./og_assistant.db`

---

### Шаг 5: Перезадеплой

```bash
vercel --prod
```

---

## ✅ Готово!

Твой URL: `https://og-model-assistant.vercel.app`

**Преимущества:**
- ✅ **Не засыпает** — всегда онлайн
- ✅ **Быстро** — глобальный CDN
- ✅ **Бесплатно** — без скрытых платежей
- ✅ **Auto-deploy** — при пуше в GitHub
- ✅ **HTTPS** — автоматически

---

## 🔄 Auto-deploy при пуше

Если подключишь GitHub репозиторий:

1. https://vercel.com/new
2. Import Git Repository
3. Выбери `wabrent/og-model-assistant`
4. Root Directory: `og-model-assistant-pro`
5. Add Environment Variables
6. Deploy

Теперь при каждом `git push` — **автоматический деплой**!

---

## 📊 Мониторинг

- **Deployments:** https://vercel.com/dashboard
- **Analytics:** Включи в Settings
- **Logs:** `vercel logs`

---

## 🆘 Troubleshooting

### Ошибка: "Build failed"

Проверь логи:
```bash
vercel logs --debug
```

### Ошибка: "Module not found"

Убедись что `requirements.txt` в папке `og-model-assistant-pro/`

### Ошибка: "Database not found"

Vercel не поддерживает PostgreSQL на бесплатном тарифе. 
**Решение:** Используй SQLite (уже настроено) или подключи внешний PostgreSQL:
- https://neon.tech (бесплатно)
- https://supabase.com (бесплатно)

---

## 🎯 Migration с Render

1. Задеплой на Vercel (инструкция выше)
2. Проверь что всё работает
3. Обнови домен (если есть) на Vercel
4. Удали проект на Render (чтобы не списывали $7)

---

## 💡 Pro Tips

- Используй `vercel --prod` для продакшена
- `vercel ls` — список всех проектов
- `vercel rm <project>` — удалить проект
- `vercel env ls` — список переменных

---

**Vercel Docs:** https://vercel.com/docs  
**Python on Vercel:** https://vercel.com/docs/python

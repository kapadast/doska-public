# Doska — Personal Task Board & Human Skill Quantification

English is below. The same description in Russian is at the end: [Доска — личная доска и оцифровка навыков](#доска--личная-доска-и-оцифровка-навыков).

Pull requests, review comments, and suggested changes are welcome. Open an issue or send a pull request if a formula, a step, or a source should be corrected.

Doska is a single-page personal task board, habit tracker, time logger, and journal built around an explicit model for **quantifying human skills**.

Most productivity tools confuse time spent with competence. Doska separates them. Years of experience are treated as tenure. Experience points (XP) measure practice volume. Mastery is recorded on an independent **0–10,000 scale** across ten semantic steps and only moves when backed by an external test, norm, or verified real-world outcome.

The application runs on a zero-dependency Python HTTP server with a vanilla JavaScript frontend and stores state in a single JSON file or SQLite database.

---

## Core Principles

1. **Practice does not automatically equal mastery.** Logging hours, finishing tasks, or checking off habits fills the practice bar (XP), not the mastery score.
2. **Evidence-gated progression.** When a skill's XP bar reaches the threshold for the next rank, the rank does not increase on its own. The skill enters a **candidate state** (`level < 10` and `xp >= threshold`). Moving to the next rank requires passing the examination or verification criteria for that tier.
3. **A failed test resets the experience bar, not the rank.** The skill's XP returns to `0`, the start of the same step. The verified rank stays. Removing a task or unchecking a habit only subtracts XP (floored at `0`) and does not lower the rank.
4. **Domain separation.** Physical and cognitive capacities are measured against standardized tests and age/sex cohort norms. Professional skills are measured by verified business outcomes, autonomy, reliability, and transferability across contexts.

---

## Skill Architecture

The system tracks **8 core capacities** (`Навыки`) and **10 applied subskills** (`Субнавыки`), plus a composite **Content Systems** ladder (`ct`) in the benchmark reference.

### Core Capacities (`Навыки`)

| ID | Skill | Construct | Primary Measurement / Scale |
|---|---|---|---|
| `str` | **Strength** | Force production in standardized movements | Consecutive strict push-ups, handgrip dynamometry (best of 3), 5x sit-to-stand; IPF GL Points for barbell totals |
| `per` | **Perception** | Signal detection and selective attention under interference | Human Benchmark reaction time (median of 5 on one device), NIH Toolbox Flanker, UFOV (ms) |
| `end` | **Endurance** | Aerobic work capacity in a single chosen modality | Field time-trial on a fixed route, heart rate recovery, cycling FTP (W/kg) or laboratory CPET ($\text{VO}_2\text{peak}$) |
| `cha` | **Charisma** | Perceived influence and affability in a shared context | General Charisma Inventory (Tskhay et al., 2018) rated by external observers (1–5 scale), RMET, recorded talks |
| `int` | **Intelligence** | General reasoning on novel problems | CRT (Cognitive Reflection Test), Berlin Numeracy Test, ICAR16 percentile, clinical WAIS-IV/V Full Scale IQ |
| `agi` | **Agility** | Postural control, balance, and functional mobility | Single-leg stance (eyes open/closed), sit-and-reach, Sitting-Rising Test (SRT, 0–10), 505 agility test (s) |
| `lck` | **Calibration** | Probabilistic forecasting accuracy | Brier score across closed predictions ($0$ = perfect, $0.25$ = coin flip), calibration curve, Good Judgment Open |
| `wil` | **Willpower** | Self-regulation and commitment execution | Daily adherence to nutrition target; 8-week log of pre-registered commitments and recovery time after lapses |

### Applied Subskills (`Субнавыки`)

| ID | Subskill | Construct | Primary Measurement / Scale |
|---|---|---|---|
| `an` | **Analytics** | Turning business questions and data into verified decisions | Verified decision cases, forecast error, SQL/modeling checks, SFIA `DAAN` levels |
| `fc` | **Forecasting** | Numerical prediction of outcomes and post-fact error tracking | Closed numerical forecasts, median absolute percentage error (MAPE), bias, interval calibration |
| `mp` | **Marketplaces** | E-commerce unit economics and operational cycle management | 90-day SKU P&L, contribution margin (CM3), ad spend share (ACoS/DRR), inventory turnover, operational autonomy |
| `mk` | **Marketing** | Market research, positioning, offers, channels, and causal profit | Controlled experiments with baseline, incremental profit, ROMI, break-even $\text{ROAS} = 1 / \text{margin}$, $\text{LTV:CAC} \ge 3$ |
| `au` | **Automation** | Converting recurring processes into reliable software/AI flows | Live automations in production, net hours saved per month, success rate ($\ge 95\%$), mean time to recovery (MTTR), SFIA `BPRE` |
| `bk` | **Books (Reading)** | Reading, retention, synthesis, and applied ideas | 12-month book registry, 48-hour retention checks, 3-minute WPM + 5 comprehension questions, complete book cards |
| `en` | **English** | Reading, listening, speaking, and writing proficiency | EF SET 50, Cambridge English Scale (100–220+), CEFR profile (A1–C2) with recorded speech and unassisted writing |
| `site` | **Vibe Coding** | Shipping maintainable software via AI prompting, testing, and ops | Live products, active users, uptime, git rollback, clean-machine restore under 1 hour, SFIA `PROG` |
| `spk` | **Public Speaking** | Structured speech delivery that shifts audience understanding | Recorded talks across formats, external rubric ratings, Toastmasters contest progression |
| `med` | **Meditation** | Attentional awareness and non-judgmental return to focus | Session regularity, 8-week practice protocol, objective attention tests (attentional blink / Flanker) |
| `ent` | **Entrepreneurship** | Building profitable systems that operate without the founder | Realized cash flow, owner distributions, share of operations running without daily founder involvement, exits |

---

## The 0–10,000 Mastery Scale

Every scored skill uses a **0–10,000 mastery scale** (`masteryScore`) accompanied by an uncertainty spread (`±masterySpread`).

### Semantic Steps

The scale is divided into 10 steps of 1,000 points:

$$\text{Step} = \min\left(10,\ \left\lfloor \frac{\text{Score}}{1000} \right\rfloor + 1\right)$$

| Score Range | Step | Stage Name | Meaning |
|---|---|---|---|
| `0` | 0 | Unrated / None | No verified baseline |
| `1–999` | 1 | Familiarity | Basic literacy or introductory awareness |
| `1000–1999` | 2 | By Instruction | Executes a task using a checklist under supervision |
| `2000–2999` | 3 | Template Adaptation | Adapts a standard template to a familiar case |
| `3000–3999` | 4 | Independent Task | Solves a standalone problem end-to-end |
| `4000–4999` | 5 | Repeatable Practice | Consistently delivers across multiple cycles |
| `5000–5999` | 6 | Measured Process | Manages a process with stable metrics and error detection |
| `6000–6999` | 7 | Integrated System | Connects multiple functions into a profitable/reliable contour |
| `7000–7999` | 8 | Operates Without Author | Another operator runs and repairs the system via documentation |
| `8000–8999` | 9 | Sustainable Scale | Method works across multiple products, accounts, or domains |
| `9000–10000` | 10 | Method Transfer / Benchmark | Replicated externally across industries or world-class standard |

### Measured Reference Scales (`1000` to `10000`)

Each step is anchored to an observable metric across the 10 tiers (`1000, 2000, ..., 10000`):

- **Strength (`str`):** IPF GL Points `[20, 30, 40, 50, 60, 70, 80, 90, 100, 113.19]` (plus cohort percentile ladders for strict push-ups from $\le 4$ up to $43+$ and bench-to-bodyweight ratios).
- **Perception (`per`):** UFOV threshold in ms (lower is better) `[1500, 1200, 900, 700, 482, 350, 250, 150, 100, 50]`; Human Benchmark reaction time bands from $>420\text{ ms}$ down to $<205\text{ ms}$.
- **Endurance (`end`):** Cycling FTP in W/kg `[1.0, 1.5, 1.75, 2.45, 3.1, 3.75, 4.4, 5.05, 5.41, 6.4]` and FRIEND $\text{VO}_2\text{peak}$ age percentiles.
- **Charisma (`cha`):** External General Charisma Inventory mean `[1.0, 1.67, 2.33, 2.83, 3.67, 4.0, 4.17, 4.5, 4.83, 5.0]` out of 5.
- **Intelligence (`int`):** Clinical WAIS-IV Full Scale IQ `[55, 70, 80, 90, 100, 110, 120, 130, 145, 160]`.
- **Agility (`agi`):** 505 Change-of-Direction test in seconds `[3.2, 3.0, 2.8, 2.6, 2.5, 2.4, 2.28, 2.22, 2.15, 2.05]` and single-leg stance / SRT thresholds.
- **Calibration (`lck`):** Brier score across 100 closed forecasts `[0.50, 0.40, 0.32, 0.27, 0.25, 0.20, 0.15, 0.10, 0.05, 0.01]`.
- **Willpower (`wil`):** Brief Self-Control Scale `[13, 20, 26, 32, 39, 45, 50, 55, 60, 65]` out of 65.
- **Analytics (`an`):** Verified decision cases / forecast error `[1 / ≤40%, 2 / ≤35%, 3 / ≤30%, 4 / ≤27%, 5 / ≤24%, 7 / ≤21%, 10 / ≤18%, 15 / ≤15%, 20 / ≤12%, 30 / ≤10%]`.
- **Forecasting (`fc`):** Closed numerical forecasts / median absolute error `[3 / ≤50%, 5 / ≤40%, 10 / ≤35%, 20 / ≤30% (bias ≤20%), 30 / ≤25% (bias ≤15%), 50 / ≤20% (bias ≤10%), 75 / ≤17%, 100 / ≤15% (2 domains), 200 / ≤12% (3 domains), 300 / ≤10% (bias ≤5%, 3 domains)]`.
- **Marketplaces (`mp`):** Annual CM3 profit / margin `[$1k / ≥5%, $3k / ≥7%, $10k / ≥10%, $30k / ≥12%, $100k / ≥15%, $300k / ≥17%, $1M / ≥20%, $3M / ≥22%, $10M / ≥25%, $30M / ≥28%]`.
- **Marketing (`mk`):** Incremental profit from controlled tests `[$1k (1 test), $3k (2), $10k (3), $30k (4), $100k (5), $300k (7), $1M (10), $3M (15), $10M (20), $30M (30)]`.
- **Content (`ct`):** Qualified audience actions per year `[10, 30, 100, 300, 1k, 3k, 10k, 30k, 100k, 300k]`.
- **Automation (`au`):** Net hours saved / run reliability `[10 / ≥80%, 30 / ≥85%, 100 / ≥90%, 300 / ≥95%, 1k / ≥97%, 3k / ≥98%, 10k / ≥98.5%, 30k / ≥99%, 100k / ≥99.5%, 300k / ≥99.9%]`.
- **Books (`bk`):** Books per year / 30-day retention `[2 / ≥50%, 5 / ≥55%, 10 / ≥60%, 20 / ≥65%, 30 / ≥70%, 40 / ≥75%, 50 / ≥80%, 60 / ≥82%, 75 / ≥85%, 100 / ≥90%]`.
- **English (`en`):** Cambridge English Scale `[100, 120, 140, 154, 160, 169, 176, 185, 200, 220+]`.
- **Vibe Coding (`site`):** Live products, users, and uptime from a `≤8h prototype` up to `5 products, 100k MAU, 99.9% availability`.
- **Public Speaking (`spk`):** Verified speeches from `1 talk (3 listeners)` to `Toastmasters World Champion`.
- **Meditation (`med`):** Cumulative practice and attentional stability from `10 min × 3 for 4 weeks` to `10,704 hours with reduced attentional blink`.
- **Entrepreneurship (`ent`):** Realized value and autonomous systems from `$1k (1 system, 1 yr)` to `$1B (7 systems, 3 exits)`.

---

## Formulas & Progression Mechanics

### 1. Rank & Hero XP Thresholds

Each skill has a discrete rank `level` from `1` to `10`. The XP required to fill the current rank bar is:

$$\text{Skill XP Needed}(\text{level}) = 40 + (\text{level} - 1) \times 20$$

- Rank 1 $\rightarrow$ 2 requires `40 XP`
- Rank 5 $\rightarrow$ 6 requires `120 XP`
- Rank 9 $\rightarrow$ 10 requires `200 XP` (Rank 10 is the cap)

The character (Hero) has a global level with threshold:

$$\text{Hero XP Needed}(\text{level}) = 20 + (\text{level} - 1) \times 10$$

### 2. Cross-Skill Acceleration (`boostedXp`)

Certain core capacities accelerate practice XP earned in applied subskills:

- **Intelligence (`int`)** accelerates: `an`, `mp`, `au`, `site`, `en`, `mk`.
- **Intelligence (`int`) + Perception (`per`)** accelerate `bk` using a weighted composite rank:

$$L_{\text{eff}} = 0.7 \times \max(L_{\text{int}}, L_{\text{per}}) + 0.3 \times \min(L_{\text{int}}, L_{\text{per}})$$

Each rank above 1 adds $+3\%$ XP, capped at $+30\%$:

$$\text{Boost Factor} = \min\Big(1.30,\ 1 + 0.03 \times \max(0,\ L_{\text{eff}} - 1)\Big)$$

$$\text{Awarded XP} = \text{round}(\text{Base XP} \times \text{Boost Factor})$$

*(Rationale: meta-analyses on general mental ability and training acquisition, $r = 0.36\text{–}0.51$.)*

### 3. Subskill-to-Capacity Feed (`skillFeed`)

Practicing certain subskills feeds a fraction of base XP into underlying capacities:

- **Meditation (`med`) $\rightarrow$ Perception (`per`):** $0.5 \times \text{base XP}$
- **Books (`bk`) $\rightarrow$ Intelligence (`int`):** $0.25 \times \text{base XP}$
- **Public Speaking (`spk`) $\rightarrow$ Charisma (`cha`):** $0.5 \times \text{base XP}$

### 4. Sleep Multiplier (`sleepFactor`)

If sleep hours are logged for the day, positive XP awards are scaled by recovery quality (gold and verified ranks are unaffected):

| Sleep Logged | XP Multiplier |
|---|---|
| Not logged or $\ge 7\text{ h}$ | $1.00\times$ |
| $6\text{ to } <7\text{ h}$ | $0.95\times$ |
| $5\text{ to } <6\text{ h}$ | $0.85\times$ |
| $4\text{ to } <5\text{ h}$ | $0.75\times$ |
| $<4\text{ h}$ | $0.60\times$ |

### 5. Tasks & Evidence Multipliers

Checking off a task on the board grants:
- **Hero:** $+8\text{ XP}$ and $+2\text{ gold}$
- **Primary skill:** $+10\text{ base XP}$
- **Secondary skills (up to 2):** $+5\text{ base XP}$ each

Adding a **proof level** (`proof`) to a task increases the skill XP:
- `1` (Action taken): $+1$ to primary skill
- `2` (Fact / volume / metric): $+2$ to primary, $+1$ to each secondary skill
- `3` (Before $\rightarrow$ After result): $+3$ to primary, $+1$ to each secondary skill
- `4` (External artifact: link, file, report): $+4$ to primary, $+1$ to each secondary skill

### 6. Time Logs (`Занятость`)

- **Rate:** $2\text{ XP}$ per full $30\text{ minutes}$ of focused work.
- **Secondary skills:** Minutes count at $50\%$ rate.
- **Daily cap:** Maximum $12\text{ XP}$ per skill per day from time logs.
- **Hero:** $+1\text{ XP}$ per $30\text{ minutes}$, capped at $+4\text{ XP}$ per day. No gold is awarded for raw time.

### 7. Physical Activity (`Активность`)

Physical training is logged separately from work time:
- **Walking:** $+1\text{ Endurance XP}$ per $2,000\text{ steps}$ (estimated duration: $\text{steps} / 100$ minutes).
- **Cycling:** $+1\text{ Endurance XP}$ per $10\text{ minutes}$ (if duration is omitted, estimated at $3\text{ min/km}$) plus $+1\text{ XP}$ per $100\text{ m}$ of elevation gain.
- **Strength training:** $+1\text{ Strength XP}$ per $3\text{ working sets}$ or per $10\text{ minutes}$.
- **Daily caps:** Maximum $12\text{ Endurance XP}$ and $12\text{ Strength XP}$ per day. Hero receives half the combined points, capped at $+4\text{ XP}$ per day.

### 8. Nutrition & Willpower (`Питание`)

Resting and sedentary maintenance calories use the Mifflin–St Jeor equation (male constant $+5$) with a $1.2$ sedentary multiplier:

$$\text{Sedentary Maintenance} = \text{round}\Big((10 \times \text{weight}_{\text{kg}} + 6.25 \times \text{height}_{\text{cm}} - 5 \times \text{age} + 5) \times 1.2\Big)$$

Active movement burn ($\text{net kcal}$) is averaged across the active date span using metabolic equivalents (METs):
- **Cycling:** $(6.8 - 1) \times 3.5 \times \text{weight}_{\text{kg}} / 200 \times \text{minutes}$
- **Walking:** $(3.5 - 1) \times 3.5 \times \text{weight}_{\text{kg}} / 200 \times (\text{steps} / 100)$
- **Strength:** $(5.0 - 1) \times 3.5 \times \text{weight}_{\text{kg}} / 200 \times \text{minutes}$

$$\text{Target kcal} = \max(1400,\ \text{Sedentary Maintenance} + \text{Average Active Burn} - 500)$$

- **Macros:** $\text{Protein} = \text{round}(1.6 \times \text{goal}_{\text{kg}})$, $\text{Fat} = \text{round}(0.8 \times \text{weight}_{\text{kg}})$, $\text{Carbs} = \max(0,\ \text{round}((\text{Target kcal} - 4\text{P} - 9\text{F}) / 4))$.
- **Willpower XP:** Each logged day where $0 < \text{kcal} \le \text{Target kcal}$ grants $+1\text{ Willpower XP}$.

### 9. Reading Profile Score (`bookScore`)

Book cards are evaluated over a rolling 12-month window. A card is **complete** only if it contains an unassisted summary (`thought`), two distinct connections (`link`, `link2`), a concrete action (`action`), and an observed result (`result`).

$$\text{Reading Profile Score} = \text{round}\left(10000 \times \left(0.15 \min\left(1, \frac{N}{30}\right) + 0.30 \min\left(1, \frac{N}{20}\right) + 0.30 \min\left(1, \frac{N}{20}\right) + 0.25 \min\left(1, \frac{N}{10}\right)\right)\right)$$

where $N$ is the number of complete cards in the last 365 days (weights: Volume $15\%$, Comprehension $30\%$, Connection to experience $30\%$, Application $25\%$).

### 10. Journal Reflection

- Any daily journal entry grants $+1\text{ Hero XP}$.
- Tagging the reflection type grants capacity XP:
  - **Observation:** $+1\text{ Perception}$
  - **Conclusion:** $+1\text{ Intelligence},\ +1\text{ Perception}$
  - **Behavior change:** $+2\text{ Intelligence},\ +1\text{ Perception}$

---

## Market Role Mapping

Doska links skills to labor market roles without double-counting:

- **Core professional roles (`an`, `mk`, `mp`, `au`, `ct`, `site`):** Anchored to US BLS / O*NET medians and P10–P90 bands (e.g., Management Analysts, Marketing Managers, Systems Analysts, Online Merchants) and regional net equivalents.
- **Verification layer (`fc`):** Does not carry a standalone salary; validates analytical and planning credibility.
- **Market access (`en`):** Unlocks international compensation bands for a core role rather than adding a separate percentage premium.
- **Thresholds & amplifiers (`int`, `cha`, `spk`, `lck`, `wil`):** Act as entry gates or seniority multipliers inside management, consulting, sales, or research roles.
- **Owner contour (`ent`):** Evaluated via net cash flow, owner distributions, and business equity rather than wages.

---

## Running Locally

1. Install **Python 3.10+**.
2. Start the server:

```bash
python server.py
```

3. Open `http://127.0.0.1:8765` in your browser.

On first launch, the server reads from the empty template `example-board.json`.

---

## Configuration & Privacy

Environment variables are documented in `.env.example`:

- `HOST` (default `127.0.0.1`)
- `PORT` (default `8765`)
- `DOSKA_STATE` (default `example-board.json`)
- `DOSKA_SQLITE` (optional path to SQLite database)
- `DOSKA_AUTH=1` (enables cookie-based authentication)
- `DOSKA_PUBLIC_URL` (base URL for OAuth callbacks)
- `DOSKA_GOOGLE_ENV`, `DOSKA_DEEPSEEK_ENV`, `DOSKA_FAL_ENV` (optional paths to external key files for Google login, AI board helper, and voice transcription)

Working board data (`data.json`, `board.json`, `*.sqlite*`, `backups/`) and all credential files (`*.env`, `session.key`, `google.allow`, `secrets/`) are excluded via `.gitignore`.

---

## Contributions

Corrections to formulas, scales, sources, and wording are welcome. Open a pull request or leave a comment on an issue. Personal board data does not belong in this repository.

---

# Доска — личная доска и оцифровка навыков

Доска — личная страница задач, привычек, учёта времени и дневника. Вокруг неё собрана явная модель **оцифровки человеческих навыков**.

Обычные списки дел путают потраченное время и умение. Доска их разделяет. Годы — это стаж. Очки опыта (XP) — объём практики. Мастерство лежит на отдельной шкале **0–10 000** из десяти смысловых ступеней и сдвигается только новым тестом, нормой или проверенным результатом.

Программа — сервер на Python без сторонних библиотек и страница на обычном JavaScript. Состояние хранится в одном JSON-файле или в базе SQLite.

Пул-реквесты, комментарии к проверке и предложенные правки приветствуются. Если формула, ступень или источник неточны — открой issue или пришли pull request.

---

## Принципы

1. **Практика сама по себе не равна мастерству.** Часы, закрытые задачи и галочки привычек заполняют полоску опыта (XP), а не балл мастерства.
2. **Рост ранга только по доказательству.** Когда опыт доходит до порога следующего ранга, ранг сам не растёт. Навык становится **кандидатом** (`level < 10` и `xp >= порога`). Следующий ранг открывается после экзамена или проверки этой ступени.
3. **Проваленный тест обнуляет шкалу опыта, ранг не снижает.** Опыт этого навыка возвращается на `0`, начало той же ступени. Удаление записи или снятая галочка уменьшают опыт, не ниже `0`, и ранг тоже не понижают.
4. **Разные области меряются по-разному.** Физические и когнитивные способности — тестом с нормой пола и возраста. Профессиональные навыки — проверенным результатом, самостоятельностью, надёжностью и переносом на другой контекст.

---

## Архитектура навыков

Система ведёт **8 базовых способностей** (`Навыки`) и **10 прикладных субнавыков** (`Субнавыки`). В справочнике ориентиров есть ещё составная шкала контент-систем (`ct`).

### Базовые способности (`Навыки`)

| ID | Навык | Что меряет | Основная шкала |
|---|---|---|---|
| `str` | **Сила** | Усилие в стандартных движениях | Отжимания подряд, хват динамометром (лучшая из 3), 5 вставаний; IPF GL для суммы трёх движений |
| `per` | **Восприятие** | Обнаружение сигнала и выбор нужного стимула при помехах | Human Benchmark, медиана 5 попыток на одном устройстве; NIH Toolbox Flanker; UFOV, мс |
| `end` | **Выносливость** | Аэробная работа в одной выбранной модальности | Один и тот же маршрут, восстановление пульса, FTP велосипеда (Вт/кг) или лабораторный CPET (VO2peak) |
| `cha` | **Харизма** | Влияние и располагающая манера в общем контексте | General Charisma Inventory (Tskhay и др., 2018) от внешних наблюдателей, шкала 1–5; RMET; записи выступлений |
| `int` | **Интеллект** | Рассуждение на новых задачах | CRT, Berlin Numeracy, перцентиль ICAR16, клинический WAIS-IV/V |
| `agi` | **Ловкость** | Равновесие и функциональная подвижность | Стойка на одной ноге (глаза открыты и закрыты), наклон сидя, SRT 0–10, тест 505, секунды |
| `lck` | **Калибровка** | Точность заранее записанных вероятностей | Brier: 0 — идеально, 0,25 — как монетка; кривая калибровки; Good Judgment Open |
| `wil` | **Воля** | Саморегуляция и доведение обязательства | День внутри нормы калорий; 8 недель заранее записанных обязательств и время возврата после срыва |

### Прикладные субнавыки (`Субнавыки`)

| ID | Субнавык | Что меряет | Основная шкала |
|---|---|---|---|
| `an` | **Аналитика** | Вопрос и данные превращаются в проверяемое решение | Кейсы с решением, ошибка прогноза, SQL, уровни SFIA DAAN |
| `fc` | **Прогнозирование** | Числовой прогноз и ошибка после факта | Закрытые прогнозы, медианная абсолютная ошибка, перекос, проверка интервалов |
| `mp` | **Маркетплейсы** | Экономика и операционный цикл продаж | P&L по SKU за 90 дней, CM3, доля рекламы, оборачиваемость, доля цикла без ежедневного участия |
| `mk` | **Маркетинг** | Рынок, оффер, каналы и причинная прибыль | Эксперимент с базой сравнения, добавочная прибыль, ROMI, порог ROAS = 1 / маржа, LTV:CAC ≥ 3 |
| `au` | **Автоматизация** | Повторяемый процесс в контролируемом потоке | Живые автоматизации, чистые часы экономии, успешность запусков ≥ 95 %, время восстановления, SFIA BPRE |
| `bk` | **Книги** | Чтение, удержание, синтез и применение | Реестр за 12 месяцев, проверка через 48 часов, 3 минуты и 5 вопросов, полная карточка |
| `en` | **Английский** | Чтение, аудирование, речь и письмо | EF SET 50, Cambridge English Scale 100–220+, профиль CEFR A1–C2, запись речи и письмо без подсказки |
| `site` | **Вайб-кодинг** | Рабочая программа через постановку задач, проверку и запуск | Живые продукты, пользователи, доступность, откат в git, восстановление на чистой машине быстрее часа, SFIA PROG |
| `spk` | **Выступления** | Подготовленная речь под цель аудитории | Записи разных форматов, внешняя рубрика, ступени Toastmasters |
| `med` | **Медитация** | Замечать происходящее и возвращать внимание | Регулярность, протокол 8 недель, объективный тест внимания |
| `ent` | **Предпринимательство** | Прибыльные системы без ежедневного участия основателя | Денежный поток, выплаты владельцу, доля операций без основателя, выходы |

---

## Шкала мастерства 0–10 000

У каждого оцениваемого навыка есть балл `masteryScore` от 0 до 10 000 и погрешность `±masterySpread`.

### Смысловые ступени

Десять ступеней по 1000 очков:

Шаг = min(10, floor(балл / 1000) + 1)

| Баллы | Шаг | Имя ступени | Смысл |
|---|---|---|---|
| `0` | 0 | Не оценено | Нет подтверждённой базы |
| `1–999` | 1 | Знакомство | Бытовая грамотность |
| `1000–1999` | 2 | По инструкции | Делает по чек-листу под присмотром |
| `2000–2999` | 3 | Адаптирует шаблон | Меняет типовой шаблон под знакомый случай |
| `3000–3999` | 4 | Отдельная задача | Закрывает задачу от начала до конца |
| `4000–4999` | 5 | Повторяемая практика | Держит результат несколько циклов |
| `5000–5999` | 6 | Процесс с метриками | Ведёт процесс и замечает ошибки |
| `6000–6999` | 7 | Интегрированная система | Связывает части в рабочий контур |
| `7000–7999` | 8 | Работает без автора | Другой человек ведёт и чинит по инструкции |
| `8000–8999` | 9 | Устойчивый масштаб | Метод живёт на нескольких продуктах или площадках |
| `9000–10000` | 10 | Перенос метода | Метод повторён снаружи или достиг эталона |

### Измеримые ориентиры (1000 … 10 000)

- **Сила:** IPF GL `[20, 30, 40, 50, 60, 70, 80, 90, 100, 113.19]` и процентили отжиманий от ≤ 4 до 43+.
- **Восприятие:** UFOV, мс, меньше лучше `[1500, 1200, 900, 700, 482, 350, 250, 150, 100, 50]`; реакция Human Benchmark от > 420 мс до < 205 мс.
- **Выносливость:** FTP, Вт/кг `[1.0, 1.5, 1.75, 2.45, 3.1, 3.75, 4.4, 5.05, 5.41, 6.4]` и возрастные процентили VO2peak.
- **Харизма:** внешний GCI `[1.0, 1.67, 2.33, 2.83, 3.67, 4.0, 4.17, 4.5, 4.83, 5.0]` из 5.
- **Интеллект:** WAIS-IV IQ `[55, 70, 80, 90, 100, 110, 120, 130, 145, 160]`.
- **Ловкость:** тест 505, секунды `[3.2, 3.0, 2.8, 2.6, 2.5, 2.4, 2.28, 2.22, 2.15, 2.05]`.
- **Калибровка:** Brier на 100 прогнозах `[0.50, 0.40, 0.32, 0.27, 0.25, 0.20, 0.15, 0.10, 0.05, 0.01]`.
- **Воля:** Brief Self-Control Scale `[13, 20, 26, 32, 39, 45, 50, 55, 60, 65]` из 65.
- **Аналитика:** кейсы / ошибка прогноза `[1 / ≤40%, 2 / ≤35%, 3 / ≤30%, 4 / ≤27%, 5 / ≤24%, 7 / ≤21%, 10 / ≤18%, 15 / ≤15%, 20 / ≤12%, 30 / ≤10%]`.
- **Прогнозирование:** закрытые прогнозы / медианная ошибка `[3 / ≤50%, 5 / ≤40%, 10 / ≤35%, 20 / ≤30% и перекос ≤20%, 30 / ≤25% и перекос ≤15%, 50 / ≤20% и перекос ≤10%, 75 / ≤17%, 100 / ≤15% в 2 областях, 200 / ≤12% в 3 областях, 300 / ≤10% и перекос ≤5% в 3 областях]`.
- **Маркетплейсы:** годовая прибыль CM3 / маржа `[$1 тыс. / ≥5%, $3 тыс. / ≥7%, $10 тыс. / ≥10%, $30 тыс. / ≥12%, $100 тыс. / ≥15%, $300 тыс. / ≥17%, $1 млн / ≥20%, $3 млн / ≥22%, $10 млн / ≥25%, $30 млн / ≥28%]`.
- **Маркетинг:** добавочная прибыль контрольных тестов `[$1 тыс. и 1 тест, $3 тыс. и 2, $10 тыс. и 3, $30 тыс. и 4, $100 тыс. и 5, $300 тыс. и 7, $1 млн и 10, $3 млн и 15, $10 млн и 20, $30 млн и 30]`.
- **Контент:** квалифицированные действия за год `[10, 30, 100, 300, 1 тыс., 3 тыс., 10 тыс., 30 тыс., 100 тыс., 300 тыс.]`.
- **Автоматизация:** часы экономии / успешность `[10 / ≥80%, 30 / ≥85%, 100 / ≥90%, 300 / ≥95%, 1 тыс. / ≥97%, 3 тыс. / ≥98%, 10 тыс. / ≥98,5%, 30 тыс. / ≥99%, 100 тыс. / ≥99,5%, 300 тыс. / ≥99,9%]`.
- **Книги:** книги за год / удержание через месяц `[2 / ≥50%, 5 / ≥55%, 10 / ≥60%, 20 / ≥65%, 30 / ≥70%, 40 / ≥75%, 50 / ≥80%, 60 / ≥82%, 75 / ≥85%, 100 / ≥90%]`.
- **Английский:** Cambridge English Scale `[100, 120, 140, 154, 160, 169, 176, 185, 200, 220+]`.
- **Вайб-кодинг:** от прототипа ≤ 8 часов до 5 продуктов, 100 тыс. активных пользователей в месяц и доступности 99,9 %.
- **Выступления:** от 1 речи на 3 слушателя до чемпиона мира Toastmasters.
- **Медитация:** от 10 минут × 3 в течение 4 недель до 10 704 часов практики с меньшим attentional blink.
- **Предпринимательство:** от $1 тыс., 1 система, 1 год до $1 млрд, 7 систем, 3 выхода.

---

## Формулы

### 1. Пороги ранга и героя

Опыт до следующего ранга навыка: `40 + (уровень − 1) × 20`.

- С ранга 1 на 2 нужно 40.
- С ранга 5 на 6 нужно 120.
- С ранга 9 на 10 нужно 200. Ранг 10 — потолок.

Опыт героя до следующего уровня: `20 + (уровень − 1) × 10`.

### 2. Ускорение субнавыков

Интеллект ускоряет аналитику, маркетплейсы, автоматизацию, вайб-кодинг, английский и маркетинг. Книги ускоряют интеллект и восприятие вместе:

Эффективный уровень = 0,7 × больший из двух + 0,3 × меньший из двух.

Каждый ранг выше 1 даёт +3 % опыта, не больше +30 %:

Множитель = min(1,30; 1 + 0,03 × max(0; эффективный уровень − 1)).

Начисленный опыт = округление(базовый опыт × множитель).

Основа: общий ум предсказывает успех обучения, r = 0,36–0,51.

### 3. Перелив в базовые способности

- Медитация → восприятие: половина базового опыта.
- Книги → интеллект: четверть базового опыта.
- Выступления с обратной связью → харизма: половина базового опыта.

### 4. Сон

Если за день записан сон, положительный опыт умножается. Монеты и ранг не режутся.

| Сон | Множитель |
|---|---|
| Нет записи или 7 часов и больше | 1,00 |
| 6–7 часов | 0,95 |
| 5–6 часов | 0,85 |
| 4–5 часов | 0,75 |
| Меньше 4 часов | 0,60 |

### 5. Задачи и доказательства

Галочка задачи:

- Герой: +8 опыта и 2 монеты.
- Основной навык: +10 базового опыта.
- Каждый дополнительный навык, не больше двух: +5.

Уровень доказательства в карточке:

- 1, действие: +1 основному.
- 2, факт, объём, число: +2 основному и +1 каждому дополнительному.
- 3, было → стало: +3 основному и +1 каждому дополнительному.
- 4, внешний файл, ссылка, отчёт: +4 основному и +1 каждому дополнительному.

### 6. Занятость

- 2 опыта за каждые полные 30 минут.
- Минуты дополнительного навыка считаются вполовину.
- Не больше 12 опыта в день на один навык.
- Герою 1 за 30 минут, не больше 4 в день. Монет за сырое время нет.
- Маркетплейсы кормят маркетплейсы. Маркетинг кормит маркетинг. Чтение кормит книги, а книги отдают четверть базового опыта интеллекту. Спорт в занятости опыт не даёт.

### 7. Активность

- Ходьба: 1 к выносливости за 2000 шагов. Минуты для сводки: шаги ÷ 100.
- Велосипед: 1 за 10 минут. Если минут нет — 3 минуты на каждый километр. Ещё 1 за 100 м набора высоты.
- Силовая: 1 к силе за 3 рабочих подхода или за 10 минут.
- Потолок дня: 12 выносливости и 12 силы. Герою половина суммы, не больше 4. Монет нет.

### 8. Питание и воля

Поддержка сидя по Миффлину — Сан Жеору, мужская константа +5, множитель 1,2:

Округление((10 × вес в кг + 6,25 × рост в см − 5 × возраст + 5) × 1,2).

Расход движения, чистые килокалории:

- Велосипед: (6,8 − 1) × 3,5 × вес / 200 × минуты.
- Ходьба: (3,5 − 1) × 3,5 × вес / 200 × (шаги / 100).
- Силовая: (5 − 1) × 3,5 × вес / 200 × минуты.

Цель калорий = max(1400; поддержка сидя + средний расход движения − 500).

Белок = округление(1,6 × целевой вес). Жир = округление(0,8 × текущий вес). Углеводы = max(0; округление((цель − 4×белок − 9×жир) / 4)).

День, где калории больше нуля и не выше цели, даёт воле +1.

### 9. Профиль чтения

Окно — 12 месяцев. Карточка полная, только если есть пересказ без книги, две разные связи, действие и результат.

Балл = округление(10 000 × (0,15 × min(1; N/30) + 0,30 × min(1; N/20) + 0,30 × min(1; N/20) + 0,25 × min(1; N/10))).

N — число полных карточек за 365 дней. Веса: объём 15 %, понимание 30 %, связь с опытом 30 %, применение 25 %.

### 10. Дневник

- Любая запись: герой +1.
- Наблюдение: восприятие +1.
- Вывод: интеллект +1 и восприятие +1.
- Изменение поведения: интеллект +2 и восприятие +1.

---

## Связь с рынком

Балл не переводится в деньги напрямую.

- Профессиональное ядро (`an`, `mk`, `mp`, `au`, `ct`, `site`) сопоставляется с медианой и полосой P10–P90 роли в США по BLS / O*NET и с региональными ориентирами net.
- Прогнозирование (`fc`) отдельной зарплаты не имеет. Оно проверяет аналитику фактом.
- Английский открывает международную версию роли и не добавляет вторую надбавку поверх зарплаты этой роли.
- Интеллект, харизма, выступления, калибровка и воля — порог или усилитель внутри роли, не отдельный тариф.
- Предпринимательство считается денежным потоком владельца, выплатами и стоимостью доли, не окладом.

---

## Запуск

1. Установи Python 3.10 или новее.
2. Запусти `python server.py`.
3. Открой `http://127.0.0.1:8765`.

При первом запуске берётся пустой `example-board.json`.

---

## Настройки и приватность

Переменные лежат в `.env.example`:

- `HOST` (по умолчанию `127.0.0.1`)
- `PORT` (по умолчанию `8765`)
- `DOSKA_STATE` (по умолчанию `example-board.json`)
- `DOSKA_SQLITE` (необязательный путь к базе)
- `DOSKA_AUTH=1` включает вход по cookie
- `DOSKA_PUBLIC_URL` — адрес для обратного вызова входа через Google
- `DOSKA_GOOGLE_ENV`, `DOSKA_DEEPSEEK_ENV`, `DOSKA_FAL_ENV` — пути к файлам ключей вне репозитория

Рабочие данные (`data.json`, `board.json`, базы, `backups/`) и секреты (`.env`, `session.key`, `google.allow`, `secrets/`) исключены в `.gitignore`. Личную доску в этот репозиторий не клади.

---

## Правки

Поправки формул, шкал, источников и формулировок приветствуются. Открой pull request или оставь комментарий в issue.

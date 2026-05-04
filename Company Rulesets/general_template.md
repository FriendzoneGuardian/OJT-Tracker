---
type: ruleset_template
version: 1.0
---

# 🧹 OJT Maid's Ruleset Guide: [Company Name]

*Goshujin-sama! It seems you need help organizing the rules for another workplace? I've prepared this template just for you! Please fill in the blanks so I can keep your schedule perfectly tidy!*

---

## 🎩 **Maid's Memo: How to use this template**
1. Replace all the text inside the **`[ brackets ]`** with the actual rules of the company.
2. If you want the AI to generate the rules for you, paste the **Opening Prompt** below into your favorite LLM!
3. Ensure the **Technical Configuration Block** at the bottom matches the hours you've set!

---

## 📝 **1. Opening Prompt (Copy this!)**
> "Master, I need you to generate a company policy regarding attendance. Please define the official hours for the Morning Shift and Afternoon Shift. Also, specify the penalties for being late or leaving early (undertime). Make sure to include a JSON block at the end with the keys: morning_start, morning_end, afternoon_start, afternoon_end, and penalty_per_15_mins_minutes."

---

## 🕒 **2. Official Shift Schedule**
- **Morning Shift:** [ e.g. 08:00 AM ] – [ e.g. 12:00 PM ]
- **Lunch Break:** [ e.g. 12:00 PM ] – [ e.g. 01:00 PM ]
- **Afternoon Shift:** [ e.g. 01:00 PM ] – [ e.g. 05:00 PM ]

## ⚖️ **3. Transmutation Rules (The "Naughty List")**
*Master, if you're late, I'll have to deduct some time from your total hours! Here's how we'll calculate it:*

- **Grace Period:** [ e.g. 15 minutes ]
- **Penalty Logic:** [ e.g. For every 15 minutes of lateness or undertime, we deduct 30 minutes from the total rendered hours. ]

---

## ⚙️ **Technical Configuration Block**
*Master, don't touch this part unless you know what you're doing! This is the secret code the Tracker uses to stay smart!*

```json
{
  "grace_period_minutes": [ e.g. 15 ],
  "morning_start": "[ HH:MM ]",
  "morning_end": "[ HH:MM ]",
  "afternoon_start": "[ HH:MM ]",
  "afternoon_end": "[ HH:MM ]",
  "penalty_per_15_mins_minutes": [ e.g. 30 ]
}
```

*I'll be waiting for you to finish, Master! Good luck with your OJT!* 💖

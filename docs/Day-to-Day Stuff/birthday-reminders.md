
# Google Calendar Birthday Reminder Automation

This setup creates recurring Google Calendar reminders for birthdays listed in a Google Sheet. It generates 3 reminders for each birthday:

- One month before
- One week before
- One day before (labeled as "Tomorrow is...")

Each of these reminders is a separate all-day event that repeats annually for 30 years.

---

## 1. Sheet Setup

Create a Google Sheet with the following structure:

| Name   | Birthday       |
|--------|----------------|
| Rosa   | 6/25/2025      |
| Jeremy | 11/12/2025     |

- Dates must include the full year (present year not birth).
- Format: `MM/DD/YYYY`

---

## 2. Script Setup

Open the Script Editor:

```
Extensions → Apps Script
```

Delete any existing code and paste the script below.

---

## 3. Script: Create Recurring Reminder Events

```javascript
function createCustomBirthdayReminders() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const calendar = CalendarApp.getDefaultCalendar();
  const data = sheet.getDataRange().getValues();

  for (let i = 1; i < data.length; i++) {
    const name = data[i][0];
    const rawDate = data[i][1];
    if (!name || !rawDate) continue;

    const birthday = new Date(rawDate);
    const baseDate = new Date(birthday.getFullYear(), birthday.getMonth(), birthday.getDate());

    const reminders = [
      { daysBefore: 30, label: "One month to" },
      { daysBefore: 7, label: "One week to" },
      { daysBefore: 1, label: "Tomorrow is" }
    ];

    for (const reminder of reminders) {
      const reminderDate = new Date(baseDate);
      reminderDate.setDate(reminderDate.getDate() - reminder.daysBefore);

      const title = `🎉 ${reminder.label} ${name}'s birthday`;
      const dateStr = reminderDate.toDateString();

      const alreadyExists = calendar
        .getEventsForDay(reminderDate)
        .some(e => e.getTitle() === title);

      if (alreadyExists) {
        Logger.log(`Skip: "${title}" already exists on ${dateStr}`);
        continue;
      }

      Logger.log(`Create: "${title}" on ${dateStr}`);

      try {
        safeCall(() =>
          calendar.createAllDayEventSeries(
            title,
            reminderDate,
            CalendarApp.newRecurrence().addYearlyRule().times(30),
            {
              description: `${reminder.label} ${name}'s birthday`
            }
          )
        );
      } catch (e) {
        Logger.log(`Error: Could not create "${title}" on ${dateStr} — ${e.message}`);
      }

      Utilities.sleep(1000);
    }
  }

  Logger.log("Done: birthday reminders created.");
}
```

---

## 4. Script: Delete Old Recurring Reminder Events

Use this to clean up old birthday reminders created in previous runs (e.g. if the data was wrong).

```javascript
function deleteOldBirthdayEventSeries() {
  const calendar = CalendarApp.getDefaultCalendar();
  const cutoffDate = new Date("2024-01-01");
  const events = calendar.getEvents(new Date("1990-01-01"), cutoffDate);
  let deletedCount = 0;

  for (let event of events) {
    const title = event.getTitle();
    const dateStr = event.getStartTime().toDateString();

    if (title.includes("Birthday")) {
      try {
        if (event.isRecurringEvent()) {
          Logger.log(`Delete (series): "${title}" on ${dateStr}`);
          safeCall(() => event.getEventSeries().deleteEventSeries());
        } else {
          Logger.log(`Delete (single): "${title}" on ${dateStr}`);
          safeCall(() => event.deleteEvent());
        }
        deletedCount++;
      } catch (e) {
        Logger.log(`Error deleting "${title}" on ${dateStr}: ${e.message}`);
      }

      Utilities.sleep(1000);
    }
  }

  Logger.log(`Done: deleted ${deletedCount} event(s).`);
}
```

---

## 5. Shared Helper

This avoids API throttling errors from Google.

```javascript
function safeCall(callback) {
  let attempts = 0;
  let delay = 1000;
  while (attempts < 5) {
    try {
      return callback();
    } catch (e) {
      if (e.message.includes("too many")) {
        Logger.log(`Throttle: retrying in ${delay}ms`);
        Utilities.sleep(delay);
        delay *= 2;
        attempts++;
      } else {
        throw e;
      }
    }
  }
  throw new Error("Too many retries.");
}
```

---

## 6. Usage

### To create reminders:
- Select `createCustomBirthdayReminders` in the Apps Script UI
- Run it
- Grant permissions on first run

### To clean up old ones:
- Run `deleteOldBirthdayEventSeries`

Logs can be viewed with `View → Logs` in the Script Editor.

---

## 7. Modifications & Use Cases

The script is designed to create three recurring reminders per birthday. Below are some common ways to change this behavior, with clear instructions.

---

### A. Only Create One Reminder (e.g. Day Before)

```javascript
const reminders = [
  { daysBefore: 1, label: "Tomorrow is" }
];
```

---

### B. Add a Same-Day Reminder

```javascript
const reminders = [
  { daysBefore: 1, label: "Tomorrow is" },
  { daysBefore: 0, label: "Today is" }
];
```

---

### C. Change the Number of Years the Events Repeat

Replace `.times(30)` with `.times(10)` to repeat for 10 years instead.

---

### D. Use a Different Calendar

```javascript
const calendar = CalendarApp.getCalendarsByName("Birthday Reminders")[0];
```

---

### E. Use a Column to Filter Who Gets Reminders

Add a `"Yes"` column and filter with:

```javascript
const flag = data[i][2];
if (!name || !rawDate || flag !== "Yes") continue;
```

---

### F. Change the Reminder Titles

```javascript
const title = `🎉 ${reminder.label} ${name}'s birthday`;
```

Modify as needed, e.g., remove emoji, add year, etc.

---

### Tip: Test With One Row

```javascript
for (let i = 1; i < 2; i++) { // Only run on row 2
```

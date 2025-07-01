
# Automatic Birthday Reminders for Google Calendar

Never forget a birthday again! This guide shows you how to automatically create birthday reminders in your Google Calendar using a simple Google Sheet. 

**What this does:**
- Creates 3 automatic reminders for each birthday:
  - 1 month before

  - 1 week before  

  - 1 day before (labeled as "Tomorrow is...")

- Reminders repeat every year for 30 years

- Works with any number of birthdays


**What you need:**
- A Google account (free)
- 15-20 minutes to set up
- No programming experience required!

---

## Step 1: Create Your Birthday List

First, we'll create a simple list of birthdays in Google Sheets.

**Instructions:**
1. Go to [sheets.google.com](https://sheets.google.com) and create a new spreadsheet
2. In the first row, type these headers:
   - Cell A1: `Name`
   - Cell B1: `Birthday`
3. Add birthdays in the rows below like this:

| Name   | Birthday       |
|--------|----------------|
| Rosa   | 6/25/2025      |
| Jeremy | 11/12/2025     |

**Important notes:**
- Use this year's date (not their birth year)
- Use the MM/DD/YYYY format (month/day/year)
- You can add as many people as you want

---

## Step 2: Open the Code Editor

Now we'll add some automated instructions (called a "script") to make the magic happen.

**Instructions:**
1. In your Google Sheet, click on `Extensions` in the top menu
2. Click on `Apps Script` from the dropdown
3. A new tab will open - this is Google's code editor
4. You'll see some sample code - delete everything in the big text box
5. Leave this tab open - we'll use it in the next step

**Don't worry!** You don't need to understand the code. Just think of it as a recipe that tells Google what to do.

---

## Step 3: Add the Birthday Reminder Recipe

Copy and paste this "recipe" into the code editor you opened in Step 2.

**Instructions:**
1. Copy ALL the code below (click and drag to select, then Ctrl+C or Cmd+C)
2. Go back to your Apps Script tab
3. Paste it into the empty text box (Ctrl+V or Cmd+V)

**The Recipe (copy everything between the lines):**

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

## Step 4: Add the Cleanup Recipe (Optional but Recommended)

This recipe helps you delete old reminders if you make mistakes or want to start over.

**Instructions:**
1. Scroll down in your Apps Script editor
2. Copy and paste this second recipe below the first one

**The Cleanup Recipe:**

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

## Step 5: Add the Helper Recipe

This last piece prevents errors when Google gets too busy. Add it below the other recipes.

**The Helper Recipe:**

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

## Step 6: Run Your Birthday Reminder System

Now let's make it work!

### To Create Your Reminders:

1. **Choose the function:** At the top of your Apps Script editor, you'll see a dropdown that probably says "Select function". Click on it and choose `createCustomBirthdayReminders`

2. **Run it:** Click the triangular "Play" button (▶️) next to the dropdown

3. **Grant permissions:** The first time you run this, Google will ask for permissions:
   - Click "Review permissions" 
   - Choose your Google account
   - Click "Advanced" then "Go to [your project name]"
   - Click "Allow"

4. **Wait:** The system will create all your reminders. This might take a minute or two.

### To Clean Up Old Reminders (if needed):

1. **Choose the cleanup function:** In the dropdown, select `deleteOldBirthdayEventSeries`
2. **Run it:** Click the play button
3. **Check the results:** This will remove old birthday reminders

### How to See What Happened:

- Click `View` in the top menu, then `Logs` to see what the system did
- Check your Google Calendar - you should see your new birthday reminders!

---

## Customization Options (For Advanced Users)

Want to change how the reminders work? Here are some easy modifications you can make. Find the section in your code that looks like this and change it:

```javascript
const reminders = [
  { daysBefore: 30, label: "One month to" },
  { daysBefore: 7, label: "One week to" },
  { daysBefore: 1, label: "Tomorrow is" }
];
```

---

### Option A: Only Get Reminders the Day Before

Replace the reminders section with:

```javascript
const reminders = [
  { daysBefore: 1, label: "Tomorrow is" }
];
```

---

### Option B: Add a Same-Day Reminder

Replace the reminders section with:

```javascript
const reminders = [
  { daysBefore: 1, label: "Tomorrow is" },
  { daysBefore: 0, label: "Today is" }
];
```

---

### Option C: Change How Many Years the Reminders Repeat

Look for this part: `.times(30)` and change the number. For example:
- `.times(10)` = reminders for 10 years
- `.times(50)` = reminders for 50 years

---

### Option D: Use a Different Calendar

If you have multiple calendars, you can specify which one to use. Replace this line:

```javascript
const calendar = CalendarApp.getDefaultCalendar();
```

With this (change "Birthday Reminders" to your calendar name):

```javascript
const calendar = CalendarApp.getCalendarsByName("Birthday Reminders")[0];
```

---

### Option E: Only Create Reminders for Certain People

Add a third column called "Create Reminder" in your spreadsheet with "Yes" or "No" for each person. Then add this code to filter:

```javascript
const flag = data[i][2];
if (!name || !rawDate || flag !== "Yes") continue;
```

---

### Option F: Change the Reminder Text

Find this line and modify the text:

```javascript
const title = `🎉 ${reminder.label} ${name}'s birthday`;
```

For example, to remove the emoji:
```javascript
const title = `${reminder.label} ${name}'s birthday`;
```

---

### Testing Tip: Start with Just One Person

To test your changes, you can make the code only process the first person in your list. Change this line:

```javascript
for (let i = 1; i < data.length; i++) {
```

To this:
```javascript
for (let i = 1; i < 2; i++) { // Only processes row 2 (first person)
```

Remember to change it back when you're ready to process everyone!

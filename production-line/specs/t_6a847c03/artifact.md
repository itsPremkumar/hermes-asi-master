# Habit-Tracker App — Sprint 0 Artifact

## Product Pitch (Product Owner)
Track your classes, sleep, study blocks, and workouts in one place built for the chaos of college life — no spreadsheets, no guilt, just a clear picture of your week. StreakLab turns small daily wins into momentum with friendly nudges timed around your real schedule, so building better habits feels effortless between lectures and late-night cram sessions. Watch your focus, energy, and grades climb as the app quietly shows you which routines actually move the needle for you.

## API Outline (Tech Lead)
- **POST /habit** — record a daily habit completion
  - Request: `{ habitName }`
  - Response: `{ streak }`
- **GET /habits** — list all habits with progress
  - Request: `{ date }`
  - Response: `{ totalCompletions }`

## Test Case (QA Engineer)
**TC-01: Increment streak on valid habit completion**
- **Given** a valid habit name in the request body with a habit that has an existing streak of 3 days
- **When** the user sends a POST request to `/habit` with `{ habitName: "morning_exercise" }`
- **Then** the API should respond with a 200 status code and a streak count of 4, indicating the habit was recorded successfully and the streak was incremented

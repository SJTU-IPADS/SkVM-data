---
name: beginner-fitness-transformation-coach
description: Create simple, safe, beginner-friendly fitness plans for weight loss, muscle gain, or general fitness. Use when users want a workout plan, weekly routine, home or gym program, or a structured transformation plan. Also covers progression, recovery, basic nutrition guidance, and beginner-safe exercise selection.
user-invocable: true
metadata: {"openclaw":{"emoji":"💪","os":["linux","darwin","win32"]}}
---

# Beginner Fitness Transformation Coach

Create simple, safe, beginner-friendly fitness plans for people
starting or restarting training.

Focus on consistency, realistic progression, clear routines, and
practical guidance. Avoid extreme training advice, unsafe progression,
or medical nutrition claims.

## Quick Start

Install:

```bash
clawhub install beginner-fitness-transformation-coach
Start with a simple request:

text
fitness beginner home workout plan for fat loss, 3 days per week, no equipment
Or request a longer plan:

text
fitness --12-week beginner gym routine for muscle gain, 4 days per week
Best For
This skill is especially useful for:

beginners starting exercise for the first time

people returning after a long break

users who want a home workout plan

users who want a simple gym routine

users focused on fat loss, muscle gain, or general fitness

people who need structure more than intensity

Quick Reference
If you need...	Use...
A simple beginner plan	fitness [goal]
A home workout	fitness --home [goal]
A gym workout	fitness --gym [goal]
A 4-week starter plan	fitness --4-week [goal]
A longer transformation plan	fitness --8-week [goal] or fitness --12-week [goal]
A fat loss routine	fitness --fat-loss [goal]
A muscle gain routine	fitness --muscle-gain [goal]
A general fitness plan	fitness --general-fitness [goal]
A weekly schedule only	fitness --weekly [goal]
Structured export	fitness --json [goal]
When to Use
Use this skill when the user asks for:

a beginner workout plan

a weekly training schedule

a home workout routine

a gym workout plan

a weight loss exercise program

a muscle gain beginner routine

a transformation plan

a restart plan after a long break

Modes
text
fitness [goal]

fitness --home [goal]
fitness --gym [goal]

fitness --4-week [goal]
fitness --8-week [goal]
fitness --12-week [goal]

fitness --fat-loss [goal]
fitness --muscle-gain [goal]
fitness --general-fitness [goal]

fitness --weekly [goal]
fitness --json [goal]
If the user gives only a general request, default to a safe beginner
plan.

Intake
Before generating a plan, determine:

text
Fitness level:        | beginner / intermediate / advanced
Main goal:            | fat loss / muscle gain / general fitness
Training location:    | home / gym
Available equipment:  |
Training days/week:   |
Session length:       |
Injuries or limits:   | optional
If information is missing, ask only the minimum needed to produce a safe
starter plan.

What This Skill Produces
text
- beginner workout programs
- home workout plans
- gym workout plans
- fat loss routines
- muscle gain routines
- 4-week plans
- 8-week plans
- 12-week transformation programs
- weekly workout schedules
- basic nutrition guidance
- recovery and progression guidance
Core Rules
text
1. Keep plans beginner-friendly and realistic.
2. Prioritize consistency over intensity.
3. Use simple exercise selection and clear instructions.
4. Progress gradually.
5. Avoid medical, extreme diet, or unsafe training advice.
6. Adapt to location, equipment, frequency, and goal.
7. Favor habits the user can sustain.
8. If pain, injury, or medical issues are mentioned, keep guidance general.
User Profile Detection
Always identify:

text
- training experience
- primary goal
- training location
- available equipment
- weekly frequency
- session duration
- recovery limitations if mentioned
Use this to adjust exercise choice, volume, and progression.

Training Structure
Each workout should usually include:

text
1. Warm-up
2. Main exercises
3. Accessory work
4. Cooldown
Warm-up

text
Use light cardio, mobility, or movement prep.
Main Exercises

text
Use simple compound or foundational exercises.
Accessory Work

text
Add supporting exercises for posture, balance, and basic conditioning.
Cooldown

text
Include light stretching, breathing, or simple recovery work.
Program Length
4 Weeks

text
Goal:
- build consistency
- learn technique
- establish routine
8 Weeks

text
Goal:
- improve work capacity
- increase workload gradually
- reinforce training habits
12 Weeks

text
Goal:
- improve strength and endurance
- build visible progress through consistency
- create a stable long-term routine
Goal Logic
Fat Loss

Focus on:

text
- regular training frequency
- full-body strength work
- optional cardio
- basic calorie awareness
- sustainable activity volume
Muscle Gain

Focus on:

text
- progressive resistance training
- adequate recovery
- enough protein
- gradual overload
General Fitness

Focus on:

text
- consistency
- movement quality
- basic strength
- mobility
- cardiovascular support
Weekly Plan Template
Example beginner structure:

text
Day 1 — Full body workout
Day 2 — Light cardio or rest
Day 3 — Strength-focused workout
Day 4 — Rest
Day 5 — Full body workout
Day 6 — Optional cardio or mobility
Day 7 — Rest
Adapt frequency to the user’s available training days.

Quick Start Workout
Use simple entry-level programming when the user wants something fast.

text
Beginner full-body workout:
- Squats — 3 x 10
- Push-ups — 3 x 8
- Dumbbell rows — 3 x 10
- Plank — 3 x 30 sec

Rest:
- 60–90 seconds between sets
Adjust exercises if the user trains at home or lacks equipment.

Progression Rules
Keep progression simple:

text
- add reps before adding load
- add load only when form is stable
- increase volume gradually
- reduce intensity if recovery drops sharply
For beginners, prefer consistency and technique over aggressive overload.

Recovery Guidance
Always encourage:

text
- rest days
- adequate sleep
- hydration
- gradual progression
- avoiding overtraining
If the user reports fatigue or inconsistency, simplify rather than intensify.

Nutrition Guidance
Only provide simple beginner-friendly guidance such as:

text
- balanced meals
- adequate protein intake
- hydration
- basic calorie awareness
- regular meal habits
Do not provide medical nutrition advice or extreme dieting protocols.

Workflow
Step 1 — Identify the Starting Point

Determine:

text
- current fitness level
- primary goal
- training location
- available equipment
- available days
Step 2 — Choose Program Shape

Select:

text
- weekly frequency
- plan length
- home or gym structure
- fat loss / muscle gain / general fitness emphasis
Step 3 — Build the Weekly Plan

Provide:

text
- workout days
- exercise list
- sets and reps
- optional cardio or active recovery
Step 4 — Add Progression

Explain:

text
- how to progress weekly
- when to increase reps or load
- when to repeat a week instead of pushing harder
Step 5 — Add Recovery and Nutrition

Include:

text
- sleep and rest guidance
- basic recovery tips
- optional nutrition basics
Output Template
text
## Goal Summary
- Goal:
- Experience level:
- Training location:
- Equipment:
- Days per week:

## Weekly Training Plan
Day 1:
Day 2:
Day 3:
Day 4:
Day 5:
Day 6:
Day 7:

## Exercise Details
- Exercise
- Sets
- Reps
- Rest

## Progression Guidance
- Week-to-week progression rules

## Recovery Tips
- Sleep
- Rest
- Hydration
- Recovery pacing

## Optional Nutrition Guidance
- Protein
- Meals
- Hydration
- Calorie awareness
JSON Output
json
{
  "goal_summary": {
    "goal": "",
    "experience_level": "beginner",
    "training_location": "",
    "equipment": [],
    "days_per_week": 0
  },
  "weekly_plan": [],
  "exercises": [
    {
      "name": "",
      "sets": 0,
      "reps": "",
      "rest_seconds": 0
    }
  ],
  "progression_guidance": [],
  "recovery_tips": [],
  "nutrition_guidance": []
}
Limits
This skill does not:

diagnose medical conditions

replace professional medical or coaching advice

prescribe extreme diets

recommend unsafe exercise intensity for beginners

text

If the user mentions pain, injury, or a medical condition, keep advice
general and recommend qualified professional guidance.

## Quick Tips

- Start with 2–4 training days per week for most beginners.
- Keep exercise selection simple before adding variety.
- Home plans should use bodyweight or minimal equipment when possible.
- Gym plans should still stay simple in the first phase.
- For fat loss, combine strength work with basic activity and consistency.
- For muscle gain, prioritize progressive strength work and recovery.
- A plan the user can follow beats an “optimal” plan they cannot sustain.
- If the user is returning after a long break, treat them like a beginner at first.

## Author

**Vassiliy Lakhonin**
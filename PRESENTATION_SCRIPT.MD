# LiftLab Presentation Script (4:45)

## Slide 1: Solution Summary (45 sec) - Deron
LiftLab solves workout boredom with AI-powered exercise suggestions...

## Slide 2: Features (45 sec) - Alex
- Exercise Library with YouTube videos
- Routine Builder with drag-and-drop
- AI-Powered Remixing
- Active Workout Timer
- Dashboard with progress charts

## Slide 3: Model Design (45 sec) - Aiden
Our database uses 6 SQLModel classes:
- User (authentication)
- Exercise (exercise library)
- Routine (workout plans)
- RoutineExercise (junction table)
- WorkoutSession (tracking)
- ExerciseLog (performance)

## Slide 4: System Design (45 sec) - Deron
5-layer architecture: Presentation → Application → Service → Repository → Data

## Slide 5: URL + QR Code (15 sec) - Alex
https://liftlab-jy0x.onrender.com
Test: bob / bobpass

## Slide 6: Demonstration (1:30) - All
- Login as bob
- Browse Exercise Library (click for YouTube)
- Create Routine
- AI Remix button
- Start Workout with timer
- View Dashboard charts
from .user import User
from .exercise import Exercise
from .routine import Routine
from .routine_exercise import RoutineExercise
from .workout_log import WorkoutSession, ExerciseLog

def setup_relationships():
    from .user import User
    from .routine import Routine
    from .workout_log import WorkoutSession
    
    User.routines = Relationship(back_populates="user")
    User.workout_sessions = Relationship(back_populates="user")
    Routine.user = Relationship(back_populates="routines")
    WorkoutSession.user = Relationship(back_populates="workout_sessions")
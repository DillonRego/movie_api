The code for this assignment would not function correctly if multiple api calls for read and write come in simultaneously.
This is because the calls to the Supabase are not atomic, so read and write calls in many different orders will cause race conditions
Additionally the way the code is currently written will make the code work poorly if delete calls are added since the id for conversation
has no logic for decreasing.

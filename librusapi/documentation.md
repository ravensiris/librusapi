
# Table of Contents

1.  [Currently supported features](#org5f4440b)
2.  [Quick start](#org92d3a6f)


<a id="org5f4440b"></a>

# Currently supported features

-   Authorizing using Librus username and password (check \`librusapi.token\`)
-   Getting lesson units on your timetable (check \`librusapi.timetable\`)


<a id="org92d3a6f"></a>

# Quick start

Minimal implementation of getting your timetable

    from librusapi.token import get_token
    from librusapi import timetable
    
    token = get_token('username', 'password')
    lesson_units = timetable.lesson_units(token)
    
    for lu in lesson_units:
        print(lu)


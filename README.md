# nuke-render-manager
Render manager for Nuke.

# Functionality

This little app makes it possible for you to create a queue of renders, similar to a render farm, but running locally on your machine.
It runs one command at a time.


# Why?

I created this because of a necessity. In the studio I'm working some scenes are very heavy (8K resolution) and Nuke's GUI has some problem with clearing memory buffers apparently.
I have tried many cache clearing commands in menu.py/init.py and nothing solved it.

Then I learned that Nuke can render from CMD, which is the way render farms work, and rendering like this has a crucial difference from GUI. 
Rendering from CMD forces memory clearance every rendered frame, thus solving my issue.

It started as a .bat file which had the same function, only it rendered one .nk at a time.


# Details

In this little application you can select as many .nk files as you want, set it's parameters (which write node you want to render from, or if you want to execute all writes [leave the write field empty]) and frame range.
You can also move it up or down in the queue.

# Requirements

- You need to set NUKE_EXE environment variable. (ex: NUKE_EXE = Nuke16.0.exe     |    This was my case)
- You may also need to add your Nuke folder in Path env variable. (ex: Path = ...;...;C:\ProgramFiles\Nuke16.0v2;...;    | Usually holds manny values.)
- Available Nuke license.
   - You CAN use a Nuke render license, BUT you must omit the "-i" in the command building function. This is the first def from 'runner.py'. Otherwise it will use your interactive available license (the one you use to work, no problems with that whatsoever so far).

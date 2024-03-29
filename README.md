# Grammar Patterns - Software R&D (Python [Pyglet/OpenGL] Videogame)

[![IMAGE ALT TEXT](http://img.youtube.com/vi/FeQ5_zvD_fM/0.jpg)](http://www.youtube.com/watch?v=FeQ5_zvD_fM "Grammar Patterns")

![alt text](print_grammar_pattern.png)

This software was created in the context of a research project. It is a memorization game, with voice instructions and keyboard interaction, used to gather scientific data regarding language patterns recognition. This project was created for a research group on the Psychology School at the University of Minho (coord. Ana Paula Soares), for studying grammar patterns learning skills in children. An article was published in a scientific journal with some results: “Do children with Specific Language Impairment (SLI) present implicit learning (IL) deficits? Evidence from an Artificial Grammar Learning (AGL) paradigm”  [http://dx.doi.org/10.1186/s12913-018-3444-8]( http://dx.doi.org/10.1186/s12913-018-3444-8).
This tool was used mainly with children, from different ages, in order to test the evolution/differences of grammar pattern memorization skills. The tool as a playful narrative (a fairy asking to water tree seeds) and 2 different phases: one is exposition to grammar patterns in the form of seed colors, followed by a test asking to repeat the correct pattern (too make sure the user is paying attention); the 2nd phase tests how well the brain remembers the different patterns, exposing new examples and asking if they are correct. This software collects in the background various time samples in milliseconds (e.g. time between each keyboard key pressed; time between an exposition and the user reaction; total time for each test phase, etc.)
Note: when the app runs, it asks if you would like to use the fixed version (1) or the interactive one (2), but only the 1st fully works, the 2nd one is an initial prototype (with mouse animations and interactions with a rainy cloud) but later we opted for a timed fixed version and this was dropped (it crashes mid-way – the fix is easy but we never needed this version again so I never implemented it).

This software were created with Python and OpenGL. It was made with short deadlines and many radical changes along the way, so the code is a little messy, it needs refactoring.
To run execute the file "main.py": you need to have Python 2.7 installed and a version of Pyglet (just do "pip install pyglet" in the command line to get it). Or if you don't have Python run the file "main.exe": it is a compiled version made with pyinstall.

## Note: 
The code and game concept are mine so I can give open-source access to it, you are free to adapt this code/tool for other projects, but the concept, scientific component and narrator voices were born in a research context, so you should contact the original research group that came up with the project. If you would like to collaborate or get access to the data of the scientific component please contact the research group (Ana Paula Soares, University of Minho: asoares@psi.uminho.pt). 

## How to use: 
Just follow the instructions on screen: the first console screen asks for user data and game mode (only the 1st fully works), after that it launches in full screen an animated version with a narrator (masculine or feminine depending on the user gender): just follow the instructions. After it is done the user data (like time between answers or key press's, wrong answers, etc.) is saved in the "Saves" folder. The questions that appear on screen (the seeds sequences) are in the files "phase1_sequences.txt" and "phase2_sequences.txt", if you edit them it changes the questions during the game (each number corresponds to a different gem/seed color).

## Contacts:
My Homepage: [www.paulojorgepm.net](http://www.paulojorgepm.net)

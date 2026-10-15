# Presenter run-script: investigating which brain regions are implicated in stress

- **Prepare before students arrive.**
  - Open the notebook and run section 1 to load the toolkit.
  - Open the MRI clip; show only the first two minutes.
  - Keep the main workshop to about an hour; the fMRI material is a separate bonus.
  - Treat the notebook as the screen to show and this script as your speaking notes.
  - The core story is a researcher testing candidate brain regions: collect scans, solve their mismatch, measure the regions, then assess evidence for their involvement in stress.

- **Opening: give the team a question, not a list of technologies.**
  - Say: “You are a researcher. You want to know what happens in the brain when people are stressed. Which regions are involved, and how could you find evidence?”
  - Take a few ideas about how to investigate the question; use them to motivate brain imaging.
  - Say: “Earlier studies suggest some candidate regions. Your team will test those ideas: do measurements from those regions relate to stress in the people you study?”
  - Explain a candidate as a region with a reason to investigate it, not a result already established for this study.
  - Keep candidate names for the atlas activity; introduce scanner mechanisms, registration, and statistics when they become useful for the research.
  - Establish once that these are teaching examples, with real template anatomy and invented PET signals and participant data.
  - Transition: “We have a research question. Our first volunteer has arrived. What information will help us investigate it?”

- **Section 2: give each scanner one clear purpose.**
  - Show the MRI scanner photograph: “First we need to know what tissue is where.”
  - Explain MRI at the level of a strong magnet, radio-wave pulses, and a measured response that becomes a detailed image.
  - Show the two-minute clip; ask students to spot the magnet, pulse, and response.
  - Stop there unless someone asks; no spin equations, pulse sequences, or relaxation constants.
  - Show the PET scanner photograph: “Structure alone does not tell us how cells are using energy.”
  - Introduce a tracer as a substance we can follow because it carries a detectable radioactive tag.
  - Show the matching molecule drawings: FDG resembles glucose, and one OH group is replaced by fluorine-18.
  - Explain only that cells take up FDG and the scanner detects signals from its radioactive decay; brighter signal gives clues about glucose use.
  - Do not turn this into a chemistry quiz or introduce fMRI here.
  - Run the MRI/PET display; ask which view gives sharper boundaries and which shows where FDG collected.
  - Transition: “We have two useful views. But our volunteer had to move between two scanner beds.”

- **Section 3: let students discover the problem, then name it.**
  - Show the zero-correction overlay and pause: “What went wrong when we combined the scans?”
  - Explain that separate visits cannot reproduce head position exactly.
  - Introduce registration once as moving one image to match another.
  - Demonstrate one horizontal move and reset; explain positive x/right, positive y/down, and millimetres.
  - Give students several minutes to try the two correction values, changing one at a time.
  - Offer the outline-free hard mode to students who finish early.
  - Keep the exact solution hidden for now.
  - Transition: “Your eyes say the match improved. How would a computer decide?”

- **Section 4: introduce a number because we now need one.**
  - Describe correlation as comparing two patterns: here, brightness across the images.
  - Explain that the displayed match score rescales the useful correlation range for this exercise; it is not percentage accuracy.
  - Run the score cell, change a correction, and rerun both the image and score cells.
  - Let students make two or three attempts to improve their number.
  - Save negative correlations, sample size, and effect size for the group-data scene.
  - Transition: “We can judge guesses with a number. Could the computer make the guesses for us?”

- **Section 5: automate the job students have just done.**
  - Ask whether the computer will beat their match; run the search animation.
  - Point out guesses that jump around, the changing score, and smaller moves near a good result.
  - Introduce optimiser as the computer's search for a better score.
  - Run the calculated result and compare it with students' best corrections.
  - Reveal the expected correction: x = −7.2 mm, y = +5.3 mm.
  - Do not teach hyperparameter tuning or dwell on the four stage snapshots; use them if the animation is hard to follow.
  - Now give the larger category: “Getting images ready for measurement is preprocessing. Alignment is one part of that.”
  - Mention checking motion, noise, and image quality in one sentence, without opening separate lessons.
  - Transition: “The scans line up. But which patch should we measure?”

- **Section 6: introduce the atlas as the tool needed next.**
  - Say: “We need a map so that different people mean the same place when they name an area.”
  - Introduce atlas as a labelled brain map and explain that structures appear at different slice levels.
  - Show one named region in the explorer, then let students use it as a reference for pictures A–D.
  - Reveal A = insula, B = hippocampus, C = anterior cingulate, D = amygdala.
  - Only after identification, explain that earlier research implicated these four areas, making them candidates to test in our study.
  - Connect their functions to possible stress-related processes: memory/context → hippocampus; emotionally important events → amygdala; body signals → insula; attention and competing responses → anterior cingulate.
  - Give each area one sentence, followed by “These areas have many other jobs and work with many other areas.”
  - Avoid presenting them as four stress switches or predicting that all signals must rise.
  - Transition: “We have the images in place and the map. Now a picture can become a measurement.”

- **Sections 7–8: turn the pictures into comparable numbers.**
  - Run the aligned regional measurements; point from one coloured outline to its bar.
  - Explain the average as combining the PET values inside that named area.
  - Clarify briefly that this slice demonstrates three areas; the fourth is visible at a different level, and a whole-brain study can include it.
  - Show the low- and high-stress example patterns; ask students to predict which bars differ most before interpreting them.
  - Keep the examples framed as deliberately constructed illustrations, not expected clinical stress effects.
  - Do not repeat the scanner explanations or show another misaligned measurement comparison.
  - Transition: “We can see example differences. But which candidate regions have convincing evidence of a relationship with stress across people?”

- **Section 9: finish collecting the study and test confidence in the pattern.**
  - Say: “We repeated the preparation and measurements for every volunteer. Each also rated stress from 0 to 10.”
  - Orient the axes before introducing statistics: each dot is a volunteer; x is stress rating; y is regional PET signal.
  - Start with 10 participants, rerun once, then try 5, 50, and 500.
  - Ask which candidate regions show clearer evidence of involvement and which patterns change when another group is drawn.
  - Connect to the earlier idea: “Correlation compared image patterns before; now it compares two measurements across people.”
  - Explain r as direction and strength of a straight-line relationship; introduce effect size as that strength, not the number of participants.
  - Say: “More people make our estimate steadier. They do not make the underlying relationship stronger.”
  - Ask how many participants students would want and what would influence that choice; there is no universal correct number in this illustration.
  - Explain once that association does not establish cause and effect.
  - The classroom cohort is generated separately from the PET pictures; it is not actual volunteer data or a result extracted from those example scans.
  - Transition: “What can our team responsibly conclude?”

- **Section 10: close the main story before offering another technology.**
  - Return to the opening question: what happens in the brain during stress, and which regions are implicated?
  - Ask which candidates the example data support most clearly and which remain uncertain.
  - Explain that a study tests previous suggestions; it can strengthen support for a region or leave the question unresolved.
  - Distinguish confirming an association in the studied group from proving a universal stress mechanism.
  - Ask a student to tell the path from volunteer to evidence in one sentence.
  - Leave three ideas: research tests candidate regions; complementary scans need preparation; evidence across people determines which candidates receive support.
  - End the main session here, with time for questions.

- **Optional bonus: a new question earns a new technology.**
  - Say: “What if we wanted to follow changes during a task rather than compare PET measurements between visits?”
  - Introduce fMRI here for the first time: repeated MRI images can show small changes related to blood oxygenation.
  - Define BOLD as that oxygen-related signal and an indirect clue about activity; no additional physiology detail is needed.
  - Show individual images before the task-related map, so repetition has a clear purpose.
  - Connect correlation to the now-familiar idea of comparing patterns, here the time course and task timing.
  - Let students change the display threshold; end by distinguishing a visible classroom pattern from a reliable real-study finding.

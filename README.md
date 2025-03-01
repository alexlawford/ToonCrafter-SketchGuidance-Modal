## ___***ToonCrafter_with_SketchGuidance***___

Modification of https://github.com/mattyamonaca/ToonCrafter_with_SketchGuidance to run on Modal.com's AI cloud,
which is in turn an implementation that recreates the SketchGuidance feature of "ToonCrafter".

- https://github.com/ToonCrafter/ToonCrafter
- https://arxiv.org/pdf/2405.17933

https://github.com/user-attachments/assets/f72f287d-f848-4982-8f91-43c49d0370

## How to Run

Note there are **two requirements files**. Locally you need to install requirements_local.txt:

    pip install -r requirements_local.txt

Then run

    modal run app.py

To run the example app. To change the inputs, directly modify the app.py file (for now).

## Issue

Currently refactoring so model download/loading isn't working.
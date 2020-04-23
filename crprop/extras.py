import os


info_message = \
"""Left Mouse Button:        - rotate viewing position\n
Middle Mouse Button:        - translate the scene\n
Right Mouse Button:        - zoom in and out of scene\n
Keys\n
  p, spacebar:        - start or pause the program\n
  q, Esc:        - exit the program\n
  + / -:        - speed up / slow down time step\n
  r:        - start/stop rotation of viewing perspective\n
  s:        - save frames to file (default is no save)\n
  t:        - toggle between a textured Earth and a simple sphere\n
  i:        - toggle printing this screen\n"""


def printText(lineno=0):
    output = info_message.splitlines()[lineno]
    return output


def printHelp():
    print("""\n\n
          ------------------------------------------------------------------------------\n
          Left Mouse Button:        - rotate viewing position\n
          Middle Mouse Button:      - translate the scene\n
          Right Mouse Button:       - zoom in and out of scene\n

          Keys\n
            p, spacebar:            - start or pause the program\n
            q, Esc:                 - exit the program\n
            + / -:                  - speed up / slow down time step\n
            r:                      - start/stop rotation of viewing perspective\n
            s:                      - save frames to file (default is no save)\n
            t:                      - toggle between a textured Earth and a simple sphere\n
            i:                      - toggle printing help message on window\n
          ------------------------------------------------------------------------------\n
          \n""")


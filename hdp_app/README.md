## Overview

This example shows how to execute a spark streaming example on the BigInsights cluster that consumes messages from IBM MessageHub (Kafka).  

## Run the example

To run the examples, in a command prompt window:

   - copy etc/vcap.json_template to vcap.json
   - edit etc/vcap.json with your messagehub connection details
   - change into the directory containing this example and run gradle to execute the example
      - `./gradlew SubmitToYarn` (OS X / *nix)
      - `gradlew.bat SubmitToYarn` (Windows)
   - next run the following command to ensure the application is running on yarn:
      - `./gradlew PsAll` (OS X / *nix)
      - `gradlew.bat PsAll` (Windows)
   - next run the following command inspect the data in HDFS:
      - `./gradlew CatHdfs` (OS X / *nix)
      - `gradlew.bat CatHdfs` (Windows)
   - next open a new terminal window and execute the python script, e.g.
      - `python send_message.py 12345`
   - wait a minute or so, then run
      - `./gradlew CatHdfs` (OS X / *nix)
      - `gradlew.bat CatHdfs` (Windows)
      - You should see the data sent with `send_message.py`

When you have finished run `./gradlew KillAll` to kill the streaming example on the cluster.


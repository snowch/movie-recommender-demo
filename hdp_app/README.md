## Overview

This example shows how to execute a spark streaming example on the BigInsights cluster that consumes messages from IBM MessageHub (Kafka).  

## Run the example

To run the examples, in a command prompt window:

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
      - alternatively, if you are using this alongside the movie recommender web app and have configured the application to use messagehub, you can login as a user to create ratings and these will get picked up by BigInsights.
   - wait a minute or so, then run
      - `./gradlew CatHdfs` (OS X / *nix)
      - `gradlew.bat CatHdfs` (Windows)
      - You should see the data sent with `send_message.py`

When you have finished run `./gradlew KillAll` to kill the streaming example on the cluster.

If you would like a more graphical connection to Hive, check out the BigInsights example project, and run the [SquirrelSQL](https://github.com/IBM-Bluemix/BigInsights-on-Apache-Hadoop/tree/master/examples/SquirrelSQL) example.

You can try the query:

```
SET hive.mapred.supports.subdirectories=true; 
SET mapred.input.dir.recursive=true; 
select * from movie_ratings;
```

This query will return more and more data as ratings are added to the web application.  Note that the spark streaming job works in batches of 60 seconds so it may take a while for the ratings to get picked up by Hive.

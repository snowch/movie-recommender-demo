package biginsights.examples

import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf

import org.apache.spark.streaming.Duration
import org.apache.spark.streaming.Seconds
import org.apache.spark.streaming.StreamingContext
import com.ibm.cds.spark.samples.config.MessageHubConfig
import com.ibm.cds.spark.samples.dstream.KafkaStreaming.KafkaStreamingContextAdapter
import org.apache.kafka.common.serialization.Deserializer
import org.apache.kafka.common.serialization.StringDeserializer

object MessageHubConsumer{
  def main(args: Array[String]) {

    val sc = new SparkConf().setAppName("MessageHubConsumer")
    
    val appArgs = sc.get("spark.driver.args").split("\\s+")

    val kafkaProps = new MessageHubConfig

    kafkaProps.setConfig("bootstrap.servers",   appArgs(0))
    kafkaProps.setConfig("kafka.user.name",     appArgs(1))
    kafkaProps.setConfig("kafka.user.password", appArgs(2))
    kafkaProps.setConfig("api_key",             appArgs(3))
    kafkaProps.setConfig("kafka_rest_url",      appArgs(4))
    kafkaProps.setConfig("kafka.topic",         appArgs(5))

    val username = appArgs(6)

    kafkaProps.createConfiguration()


    val ssc = new StreamingContext( sc, Seconds(30) )

    val stream = ssc.createKafkaStream[String, String, StringDeserializer, StringDeserializer](
      kafkaProps,
      List(kafkaProps.getConfig("kafka.topic"))
      );

    // This will create a file per output which is an anti-pattern in hadoop because
    // hadoop is optimised for larger files.  A production implementation would probably
    // need to periodically merge the small files into a larger file and delete the smaller
    // files.  Example code snippet: http://stackoverflow.com/a/27127343/1033422
    //
    // Note that the hadoop-streaming.jar file can be found here:
    //   /usr/iop/current/hadoop-mapreduce-client/hadoop-streaming.jar
    
    stream.foreachRDD{ rdd =>
      if (rdd.count() > 0) {

        // save each batch in it's own folder to prevent batches overwriting each other
        val uuid = java.util.UUID.randomUUID.toString
        rdd.map(row => row._2).saveAsTextFile (s"hdfs:///user/${username}/movie-ratings/${uuid}")
      }
    }
    ssc.start()
    ssc.awaitTermination()
  }
}

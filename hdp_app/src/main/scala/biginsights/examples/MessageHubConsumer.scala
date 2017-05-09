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


    val ssc = new StreamingContext( sc, Seconds(60) )

    val stream = ssc.createKafkaStream[String, String, StringDeserializer, StringDeserializer](
      kafkaProps,
      List(kafkaProps.getConfig("kafka.topic"))
      );

    stream.foreachRDD{ rdd =>
      // we only want to create a folder in hdfs if we have some data
      if (rdd.count() > 0) {
        def uuid = java.util.UUID.randomUUID.toString
        val outDir = s"hdfs:///user/${username}/test-${uuid}"
        rdd.saveAsTextFile (outDir)
      }
    }

    stream.print()
    ssc.start()
    ssc.awaitTermination()
  }
}

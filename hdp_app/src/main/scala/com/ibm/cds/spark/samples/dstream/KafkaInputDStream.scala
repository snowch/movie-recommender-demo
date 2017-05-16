package com.ibm.cds.spark.samples.dstream

import scala.collection.JavaConversions._
import scala.collection.Map
import scala.reflect.ClassTag
import scala.reflect.classTag
import org.apache.kafka.clients.consumer.ConsumerRecord
import org.apache.kafka.clients.consumer.KafkaConsumer
import org.apache.kafka.common.serialization.Deserializer
import org.apache.spark.Logging
import org.apache.spark.storage.StorageLevel
import org.apache.spark.streaming.StreamingContext
import org.apache.spark.streaming.dstream._
import org.apache.spark.streaming.receiver.Receiver
import org.apache.log4j.Level
import org.apache.log4j.Logger
import java.util.Properties
import com.ibm.cds.spark.samples.config.MessageHubConfig
import org.apache.kafka.common.security.JaasUtils

class KafkaInputDStream[
  K: ClassTag,
  V: ClassTag,
  U <: Deserializer[_]: ClassTag,
  T <: Deserializer[_]: ClassTag](
    ssc : StreamingContext,
    kafkaParams: Map[String, String],
    topics: List[String],
    storageLevel: StorageLevel = StorageLevel.MEMORY_AND_DISK
  ) extends ReceiverInputDStream[(K, V)](ssc) with Logging {

  def getReceiver(): Receiver[(K, V)] = {
      new KafkaReceiver[K, V, U, T](kafkaParams, topics, storageLevel)
  }
}

object KafkaStreaming{
  implicit class KafkaStreamingContextAdapter( val ssc : StreamingContext ){
    def createKafkaStream[K: ClassTag, V: ClassTag, U <: Deserializer[_]: ClassTag, T <: Deserializer[_]: ClassTag](
        bootStrapKafkaConfig: MessageHubConfig,
        topics: List[String]
    ): ReceiverInputDStream[(K, V)] = {
      val kafkaProps = new MessageHubConfig;
      bootStrapKafkaConfig.copyKafkaOptionKeys( kafkaProps)
      kafkaProps.setValueDeserializer[T];
      new KafkaInputDStream[K, V, U, T](ssc, kafkaProps.toImmutableMap, topics)
    }
  }
}

class KafkaReceiver[
  K: ClassTag,
  V: ClassTag,
  U <: Deserializer[_]: ClassTag,
  T <: Deserializer[_]: ClassTag](
    kafkaParams: Map[String,String],
    topics: List[String],
    storageLevel: StorageLevel
  ) extends Receiver[(K, V)](storageLevel) with Logging {

  // Connection to Kafka
  var kafkaConsumer: KafkaConsumer[K,V] = null

  def onStop() {
    if (kafkaConsumer != null) {
      kafkaConsumer.synchronized {
        print("Stopping kafkaConsumer")
        kafkaConsumer.close()
        kafkaConsumer = null
      }
    }
  }

  def onStart() {
    logInfo("Starting Kafka Consumer Stream")
    
    //Make sure the Jaas Login config param is set
    val jaasLoginParam = System.getProperty(JaasUtils.JAVA_LOGIN_CONFIG_PARAM);
    if ( jaasLoginParam == null ){
      MessageHubConfig.createJaasConfiguration( 
          kafkaParams.get(MessageHubConfig.KAFKA_USER_NAME).get, 
          kafkaParams.get(MessageHubConfig.KAFKA_USER_PASSWORD).get
          )
    }
    
    val keyDeserializer = classTag[U].runtimeClass.getConstructor().newInstance().asInstanceOf[Deserializer[K]]
    val valueDeserializer = classTag[T].runtimeClass.getConstructor().newInstance().asInstanceOf[Deserializer[V]]
    
    //Create a new kafka consumer and subscribe to the relevant topics
    kafkaConsumer = new KafkaConsumer[K, V](kafkaParams)
    kafkaConsumer.subscribe( topics )
    
    val consumerPollDuration = (kafkaParams.get(MessageHubConfig.CONSUMER_POLL_DURATION_MS).get).toLong
    
    new Thread( new Runnable {
      def run(){
        try{
			    while( kafkaConsumer != null ){
            var it:Iterator[ConsumerRecord[K, V]] = null;
            
            if ( kafkaConsumer != null ){
              kafkaConsumer.synchronized{     
                //Poll for new events
                it = kafkaConsumer.poll(consumerPollDuration).iterator              
                while( it != null && it.hasNext() ){
                  //Get the record and store it
                  val record = it.next();
                  store( (record.key, record.value) )
                }            
                kafkaConsumer.commitSync
              }
            }            

            Thread.sleep( consumerPollDuration )
          }  
          println("Exiting Thread")
        }catch{
          case e:Throwable => {
            reportError( "Error in KafkaConsumer thread", e);
            e.printStackTrace()
          }
        }
	    }
    }).start
  }
}


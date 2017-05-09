package com.ibm.cds.spark.samples.config

import scala.collection.mutable.ListBuffer
import scala.reflect.ClassTag
import org.apache.kafka.clients.CommonClientConfigs
import org.apache.kafka.common.config.SslConfigs
import org.apache.kafka.common.security.JaasUtils
import scala.io.Source
import java.io.InputStream
import java.io.FileWriter
import java.io.File
import javax.net.ssl.SSLContext
import org.codehaus.jettison.json.JSONObject

class MessageHubConfig extends DemoConfig{  
  
  lazy val kafkaOptionKeys = ListBuffer[String]()
  
  override def initConfigKeys(){
    
    config = config ++ Map[String,String]( 
      registerConfigKey(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG),
      registerConfigKey(CommonClientConfigs.CLIENT_ID_CONFIG, "biginsights.examples.messagehub.consumer"),
      
      // You may want to change these values
      registerConfigKey("auto.offset.reset", "latest"),
      registerConfigKey("acks", "-1"),
      registerConfigKey("retries", "0"),
      registerConfigKey("batch.size", "16384"),
      registerConfigKey("linger.ms", "1"),
      registerConfigKey("buffer.memory", "33554432"),
      registerConfigKey("key.serializer", "org.apache.kafka.common.serialization.StringSerializer"),
      registerConfigKey("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer"),
      
      // used to control the poll frequency in com.ibm.cds.spark.samples.dstream.KafkaInputDStream
      registerConfigKey(MessageHubConfig.CONSUMER_POLL_DURATION_MS, "1000"),

      // You may want to change the password
      registerConfigKey(SslConfigs.SSL_TRUSTSTORE_PASSWORD_CONFIG, "changeit"),
      registerConfigKey(SslConfigs.SSL_PROTOCOL_CONFIG, "TLSv1.2"),
      registerConfigKey(SslConfigs.SSL_ENABLED_PROTOCOLS_CONFIG, "TLSv1.2"),
      registerConfigKey(SslConfigs.SSL_TRUSTSTORE_TYPE_CONFIG, "JKS"),
      registerConfigKey(SslConfigs.SSL_TRUSTSTORE_LOCATION_CONFIG, getDefaultSSLTrustStoreLocation),
      registerConfigKey(SslConfigs.SSL_ENDPOINT_IDENTIFICATION_ALGORITHM_CONFIG, "HTTPS"),
      registerConfigKey(CommonClientConfigs.SECURITY_PROTOCOL_CONFIG, "SASL_SSL" ),
      
      registerConfigKey(MessageHubConfig.KAFKA_USER_NAME),
      registerConfigKey(MessageHubConfig.KAFKA_USER_PASSWORD)
    )    
  }
  
  private def getDefaultSSLTrustStoreLocation():String={
    val javaHome = System.getProperty("java.home") + File.separator + "lib" + File.separator + "security" + File.separator + "cacerts"
    println("default location of ssl Trust store is: " + javaHome)
    javaHome
  }

  override private[config] def registerConfigKey( key: String, default: String = null ) : (String,String) = {
    kafkaOptionKeys += key
    super.registerConfigKey(key,default)
  }
  
  def createConfiguration(ignorePrefix:String=null) {
    //Create the jaas configuration
    MessageHubConfig.createJaasConfiguration(getConfig(MessageHubConfig.KAFKA_USER_NAME ), getConfig(MessageHubConfig.KAFKA_USER_PASSWORD) )
  }
  
  def copyKafkaOptionKeys(other:MessageHubConfig){
    kafkaOptionKeys.foreach { key => other.setConfig(key, getConfig(key) ) }
  }
  
  def setValueSerializer[U]()(implicit c: ClassTag[U]){
    setConfig("value.serializer", c.runtimeClass.getName);
  }
  
  def setValueDeserializer[U]()(implicit c: ClassTag[U]){
    setConfig("value.deserializer", c.runtimeClass.getName);
  }
}
  
object MessageHubConfig{
  final val KAFKA_USER_NAME = "kafka.user.name"
  final val KAFKA_USER_PASSWORD = "kafka.user.password"
  final val CONSUMER_POLL_DURATION_MS = "consumer.poll.duration.ms"
  
  private def fixPath(path: String):String = {
    path.replaceAll("\\ / : * ? \" < > |,", "_")
  }
  
  def createJaasConfiguration( userName: String, password: String){
    //Create the jaas configuration
      try{
        val confString = s"""|KafkaClient {
                             |    com.ibm.messagehub.login.MessageHubLoginModule required
                             |    serviceName="kafka"
                             |    username="${userName}"
                             |    password="${password}";
                             |};""".stripMargin
        
        val confDir= new File( System.getProperty("java.io.tmpdir") + File.separator + 
            fixPath( userName ) )
        confDir.mkdirs
        val confFile = new File( confDir, "jaas.conf");
        val fw = new FileWriter( confFile );
        fw.write( confString )
        fw.close
        
        //Set the jaas login config property
        println("Registering JaasConfiguration: " + confFile.getAbsolutePath)
        System.setProperty(JaasUtils.JAVA_LOGIN_CONFIG_PARAM, confFile.getAbsolutePath )
      }catch{
        case e:Throwable => {
          e.printStackTrace
          throw e
        }        
      }
  }
}

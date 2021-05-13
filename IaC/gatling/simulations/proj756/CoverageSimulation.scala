package proj756

import scala.concurrent.duration._

import io.gatling.core.Predef._
import io.gatling.http.Predef._

object Utility {
  /*
    Utility to get an Int from an environment variable.
    Return defInt if the environment var does not exist
    or cannot be converted to a string.
  */
  def envVarToInt(ev: String, defInt: Int): Int = {
    try {
      sys.env(ev).toInt
    } catch {
      case e: Exception => defInt
    }
  }

  /*
    Utility to get an environment variable.
    Return defStr if the environment var does not exist.
  */
  def envVar(ev: String, defStr: String): String = {
    sys.env.getOrElse(ev, defStr)
  }
}

  object CoverageSim {

    val feeder_1 = csv("landlord.csv").eager.random
    val feeder_2 = csv("property.csv").eager.random
    val feeder_3 = csv("tenant.csv").eager.random
    val feeder_4 = csv("property_list.csv").eager.random
    val feeder_5 = csv("city.csv").eager.random

    val app_simulation = repeat(times=1) {
      feed(feeder_1)
      .feed(feeder_2)
      .feed(feeder_3)
      .feed(feeder_4)
      .feed(feeder_5)
      //Create a landlord
      .exec(http("CreateLandlord")
      .post("/api/v1/landlord/")
      .body(StringBody("""{
                          "username": "${l_username}",
                          "password" : "${l_password}",
                          "fname" : "${l_fname}",
                          "lname" : "${l_lname}",
                          "email" : "${l_email}",
                          "contact" : "${l_contact}"
                       } """)).asJson)
      .pause(1)
      // Login to landlord
      .exec(http("LoginLandlord")
      .put("/api/v1/landlord/login")
      .body(StringBody("""{
                          "username": "${l_username}",
                          "password" : "${l_password}"
                       } """)).asJson)
      .pause(1)
      // Update landlord account
      .exec(http("UpdateLandlord")
      .put("/api/v1/landlord/${l_user_id}")
      .body(StringBody("""{
                          "password" : "${l_password}",
                          "fname" : "${l_fname}",
                          "lname" : "${l_lname}",
                          "email" : "truce@abc.com",
                          "contact" : "${l_contact}"
                       } """)).asJson)
      .pause(1)
      // Create landlord property
      .exec(http("CreateProperty")
      .post("/api/v1/landlord/property")
      .body(StringBody("""{
                          "street address" : "${street address}",
                          "city" : "${city}",
                          "pincode" : "${pincode}",
                          "availability" : "${availability}",
                          "beds" : "${beds}",
                          "baths" : "${baths}",
                          "rent" : "${rent}",
                          "facilities" : "${facilities}"
                       } """)).asJson
      .header("user_id", "${l_user_id}")
      .check(status is 200)
      .check(jsonPath("$.property_id").saveAs("prop_id_response")))
      .pause(1)
      //Create a tenant
      .exec(http("CreateTenant")
      .post("/api/v1/tenant/")
      .body(StringBody("""{
                          "username": "${t_username}",
                          "password" : "${t_password}",
                          "fname" : "${t_fname}",
                          "lname" : "${t_lname}",
                          "email" : "${t_email}",
                          "contact" : "${t_contact}"
                       } """)).asJson)
      .pause(1)
      // Login to tenant
      .exec(http("LoginTenant")
      .put("/api/v1/tenant/login")
      .body(StringBody("""{
                          "username": "${t_username}",
                          "password" : "${t_password}"
                       } """)).asJson)
      .pause(5)
      // Update tenant account
      .exec(http("UpdateTenant")
      .put("/api/v1/tenant/${t_user_id}")
      .body(StringBody("""{
                          "password" : "${t_password}",
                          "fname" : "${t_fname}",
                          "lname" : "${t_lname}",
                          "email" : "truce@abc.com",
                          "contact" : "${t_contact}"
                       } """)).asJson)
      // Search Properties
      .exec(http("SearchProperties")
      .get("/api/v1/property/list_prop/${city_id}"))
      .pause(1)
      // View property details
      .exec(http("ViewPropertyDetails")
      .get("/api/v1/property/${prop_id_response}"))
      .pause(5)
      // Tenant Property application
      .exec(http("TenantPropApplication")
      .put("/api/v1/tenant/apply/${t_user_id}")
      .body(StringBody("""{
                          "prop_id" : "${prop_id_response}"
                       } """)).asJson)
      .pause(1)
      // List landlord Properties
      .exec(http("ListLandlordProperty")
      .get("/api/v1/property/user_prop/${l_user_id}"))
      .pause(1)
      // Create tenant service request
      .exec(http("TenantCreateServiceRequest")
      .post("/api/v1/tenant/service_req")
      .body(StringBody("""{
                          "property_id" : "${prop_id_response}",
                          "query": "Problem in Bathroom"
                       } """)).asJson
      .header("user_id", "${t_user_id}")
      .check(status is 200)
      .check(jsonPath("$.query_id").saveAs("query_id_response")))
      .pause(15)
      // Update tenant service request
      .exec(http("TenantUpdateServiceRequest")
      .put("/api/v1/tenant/service_req_update/${query_id_response}")
      .body(StringBody("""{
                          "property_id" : "${prop_id_response}",
                          "query": "Toilet clogged"
                       } """)).asJson
      .header("user_id", "${t_user_id}"))
      .pause(1)
      // Landlord View service request
      .exec(http("ViewLandlordServiceRequest")
      .get("/api/v1/property/service_req")
      .body(StringBody("""{
                          "user_id" : "${l_user_id}"
                       } """)).asJson)
      .pause(15)
      // Landlord Resolves service request
      .exec(http("ResolveServiceRequest")
      .put("/api/v1/landlord/resolve_req/${query_id_response}")
      .body(StringBody("""{
                          "property_id" : "${prop_id_response}",
                          "tenant_id" : "${t_user_id}",
                          "resolution": "Fixed the bathroom door",
                          "resolved": true
                         } """)).asJson
      .header("user_id", "${l_user_id}"))
      .pause(15)
      // Delete property
      .exec(http("DeleteLandlordProperty")
      .delete("/api/v1/landlord/delprop/${prop_id_response}")
      .header("user_id", "${l_user_id}"))
      .pause(1)
      // Tenant logout
      .exec(http("LogoutTenant")
      .put("/api/v1/tenant/logoff")
      .header("jwt", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiVF9qYXp6eWIiLCJ0aW1lIjoxNjE3NDkzNTU1LjA0NDg4ODd9.uE-9Mu2I3BvmHhWRPa7uw09qrM_Qrue12H1h_RzBOBo"))
      .pause(1)
      // Landlord logout
      .exec(http("LogoutLandlord")
      .put("/api/v1/landlord/logoff")
      .header("jwt", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiVF9qYXp6eWIiLCJ0aW1lIjoxNjE3NDkzNTU1LjA0NDg4ODd9.uE-9Mu2I3BvmHhWRPa7uw09qrM_Qrue12H1h_RzBOBo"))
      .pause(1)
      // Delete landlord
      .exec(http("DeleteLandlordAccount")
      .delete("/api/v1/landlord/${l_user_id}"))
      // Delete tenant
      .exec(http("DeleteTenantAccount")
      .delete("/api/v1/tenant/${t_user_id}"))

        }
    }

object RLandlord {
val feeder = csv("landlord.csv").eager.circular
  val rlandlord = repeat(times=4, counterName="i") {
    feed(feeder)
    .exec(http("RLandlord ${i}")
      .get("/api/v1/landlord/L_rishabh"))
      .pause(1)
  }
}

object RLandlordforever {
  val feeder = csv("landlord.csv").eager.circular
    val rlandlordforever = forever("i") {
  feed(feeder)
    .exec(http("RLandlord ${i}")
      .get("/api/v1/landlord/L_rishabh"))
      .pause(1) }
  }


// Get Cluster IP from CLUSTER_IP environment variable or default to 127.0.0.1 (Minikube)
class ReadTablesSim extends Simulation {
  val httpProtocol = http
    .baseUrl("http://" + Utility.envVar("CLUSTER_IP", "127.0.0.1") + "/")
    .acceptHeader("application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    .authorizationHeader("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZGJmYmMxYzAtMDc4My00ZWQ3LTlkNzgtMDhhYTRhMGNkYTAyIiwidGltZSI6MTYwNzM2NTU0NC42NzIwNTIxfQ.zL4i58j62q8mGUo5a0SQ7MHfukBUel8yl8jGT5XmBPo")
    .acceptLanguageHeader("en-US,en;q=0.5")
    .acceptLanguageHeader("en-US,en;q=0.5")

}

class CoverageSim extends ReadTablesSim {
  val coverageScn = scenario("Perform coverage simulation")
    .exec(CoverageSim.app_simulation)

  setUp(
    coverageScn.inject(atOnceUsers(1))
  ).protocols(httpProtocol)

}

class ReadLandlordSim extends ReadTablesSim {
  val scnReadLandlord = scenario("ReadLandlord")
    .exec(RLandlord.rlandlord)
  setUp(
    scnReadLandlord.inject(constantConcurrentUsers(Utility.envVarToInt("USERS", 1)).during(10.seconds))
  ).protocols(httpProtocol)
  }

class ReadLandlordForeverSim extends ReadTablesSim {
  val scnReadLandlord = scenario("ReadLandlord")
    .exec(RLandlordforever.rlandlordforever)
  setUp(
    scnReadLandlord.inject(atOnceUsers(Utility.envVarToInt("USERS", 1)))
  ).protocols(httpProtocol)
  }
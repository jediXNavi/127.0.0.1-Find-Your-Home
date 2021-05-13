package proj756

import scala.concurrent.duration._
import scala.util.Random

import io.gatling.core.Predef._
import io.gatling.http.Predef._

object LandlordLoadTesting {

	//Helper functions
	def randomStringFromCharList(length: Int, chars: Seq[Char]): String = {
	    val sb = new StringBuilder
	    for (i <- 1 to length) {
	      val randomNum = util.Random.nextInt(chars.length)
	      sb.append(chars(randomNum))
	    }
	    sb.toString
	  }

	def randomAlphaNumericString(length: Int): String = {
	    val chars = ('A' to 'Z') ++ ('0' to '9')
	    randomStringFromCharList(length, chars)
	  }


	val random = new Random
	//Property values
	val street_list = Seq("Manor Street","Buchanan Street","Dominion Street","Haywood Avenue","Broadway Heights","Cameroon Avenue","Graveley Street")
	val city_names = Seq("Burnaby","Kitsilano","Surrey","Delta")
	val availability_types = Seq(true,false)
	val facilities_list = Seq("Jacuzzi","Wifi","Heating","Hydro","Parking","Gym","Music Room","Garden","Backyard")

	//Random generation
	val house_num = random.nextInt(1000)
	val street_address = house_num + " " + street_list(random.nextInt(street_list.length)) 
	val city = city_names(random.nextInt(city_names.length))
	val pincode = randomAlphaNumericString(6)
	val availability = availability_types(random.nextInt(availability_types.length))	
	val beds = random.nextInt(5)
	val baths = random.nextInt(3)
	val rent = random.nextInt(4000)


	val property_feeder = Iterator.continually(
		Map("street_address" -> (random.nextInt(1000) + " " + street_list(random.nextInt(street_list.length))),
	       "city" -> (city_names(random.nextInt(city_names.length))),
	       "pincode" -> (randomAlphaNumericString(6)),
	       "availability" -> (availability_types(random.nextInt(availability_types.length))),
	       "facility" -> (random.shuffle(facilities_list).take(1 + random.nextInt(4)).mkString("[", ",", "]")),
	       "beds" -> (random.nextInt(5)),
	       "baths" -> (random.nextInt(3)),
	       "rent" -> (random.nextInt(4000))
	   ))

  val user_feeder = csv("landlord.csv").eager.random



	val landlord_login = {
	  feed(user_feeder)
	  .exec(http("LoginLandlord")
      .put("/api/v1/landlord/login")
      .body(StringBody("""{
                          "username": "${l_username}",
                          "password" : "${l_password}"
                       } """)).asJson)
      .pause(1)
	}

	val create_property = {
	feed(property_feeder)
    .exec(http("CreateProperty")
  	.post("/api/v1/landlord/property")
  	.body(StringBody("""{
                      "street address" : "${street_address}",
                      "city" : "${city}",
                      "pincode" : "${pincode}",
                      "availability" : "${availability}",
                      "beds" : "${beds}",
                      "baths" : "${baths}",
                      "rent" : "${rent}",
                      "facilities" : "${facility}"
                   } """)).asJson
  	.header("user_id", "${l_user_id}")
  	.check(status is 200)
  	.check(jsonPath("$.property_id").saveAs("prop_id_response")))
  	.pause(1)
}
  
	val landlord_logout = {
	   exec(http("LogoutLandlord")
      .put("/api/v1/landlord/logoff")
      .header("jwt", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiVF9qYXp6eWIiLCJ0aW1lIjoxNjE3NDkzNTU1LjA0NDg4ODd9.uE-9Mu2I3BvmHhWRPa7uw09qrM_Qrue12H1h_RzBOBo"))
      .pause(1)
	}

  val listlandlordprop = {
       exec(http("ListLandlordProperty")
      .get("/api/v1/property/user_prop/${l_user_id}"))
      .pause(1)
  }
}

 object TenantLoadTesting {


  val random = new Random

  val user_feeder = csv("tenant.csv").eager.random
  val property_feeder = csv("property_list.csv").eager.random

  val query_list = Seq("Bathroom door not working","Lock broken","Toilet clogged","Electric problem","Water leakage","Broken Bulb","Garbage bin issue")

  val query_feeder = Iterator.continually(
      Map("query" -> (query_list(random.nextInt(query_list.length)))
          ))

  val tenant_login = {
  	  feed(user_feeder)
  	  .exec(http("LoginTenant")
      .put("/api/v1/tenant/login")
      .body(StringBody("""{
                          "username": "${t_username}",
                          "password" : "${t_password}"
                       } """)).asJson)
      .pause(1)
	}

  val create_service_req = {
  	   feed(query_feeder)
       .feed(property_feeder)
       .feed(user_feeder)
  	  .exec(http("TenantCreateServiceRequest")
      .post("/api/v1/tenant/service_req")
      .body(StringBody("""{
                          "property_id" : "${property_id}",
                          "query": "${query}"
                       } """)).asJson
      .header("user_id", "${t_user_id}"))
      .pause(1)

  }

  val logout_tenant = {
	   exec(http("LogoutTenant")
      .put("/api/v1/tenant/logoff")
      .header("jwt", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiVF9qYXp6eWIiLCJ0aW1lIjoxNjE3NDkzNTU1LjA0NDg4ODd9.uE-9Mu2I3BvmHhWRPa7uw09qrM_Qrue12H1h_RzBOBo"))
      .pause(1)
  }
}

// Get Cluster IP from CLUSTER_IP environment variable or default to 127.0.0.1 (Minikube)
class LandlordLoadTestSim extends ReadTablesSim {
	
  val propertyCreationScn = scenario("Landlord creates property")
	.forever(){
	 exec(LandlordLoadTesting.landlord_login, LandlordLoadTesting.create_property, LandlordLoadTesting.landlord_logout)
	}

  val listLandlordPropertyScn = scenario("Landlord logins and checks if new service requests")
    .forever(){
    exec(LandlordLoadTesting.landlord_login, LandlordLoadTesting.listlandlordprop)
  }

	setUp(
    propertyCreationScn.inject(constantConcurrentUsers(Utility.envVarToInt("USERS", 1)).during(20.seconds)),
    listLandlordPropertyScn.inject(constantConcurrentUsers(Utility.envVarToInt("USERS", 1)).during(20.seconds))
    ).protocols(httpProtocol)
}

class TenantLoadTestSim extends ReadTablesSim {
  
  val tenantServiceReqScn = scenario("Tenant creates service request")
  .forever(){
   exec(TenantLoadTesting.tenant_login, TenantLoadTesting.create_service_req, TenantLoadTesting.logout_tenant)
  }

  setUp(
    tenantServiceReqScn.inject(constantConcurrentUsers(Utility.envVarToInt("USERS", 1)).during(20.seconds))
    ).protocols(httpProtocol)
}

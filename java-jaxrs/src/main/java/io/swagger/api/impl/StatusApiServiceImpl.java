package io.swagger.api.impl;

import java.util.Random;

import javax.ws.rs.core.Response;
import javax.ws.rs.core.SecurityContext;

import io.swagger.api.StatusApi;
import io.swagger.model.Problem;

@javax.annotation.Generated(value = "io.swagger.codegen.languages.java.JavaResteasyEapServerCodegen", date = "2018-08-26T10:53:36.522+02:00[Europe/Rome]")

public class StatusApiServiceImpl implements StatusApi {

	public Response getStatus(SecurityContext securityContext) {
		// do some magic!

		Random rand = new Random();

		int  n = rand.nextInt(10);
		if (n < 6)
			return Response.ok(new Problem("ok", 200)).build();
		if (n < 7)
			return Response.status(429).entity(new Problem("Too Many Requests", 429)).build();

		return Response.status(503).entity(new Problem("Service Unavailable", 503)).build();

	}

}


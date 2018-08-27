package io.swagger.api.impl;

import io.swagger.api.*;
import io.swagger.model.*;


import io.swagger.model.Timestamps;


import java.util.List;

import java.io.InputStream;

import javax.ws.rs.core.Response;
import javax.ws.rs.core.SecurityContext;

import java.util.Date;



@javax.annotation.Generated(value = "io.swagger.codegen.languages.java.JavaResteasyEapServerCodegen", date = "2018-08-25T23:10:21.017Z[GMT]")

public class EchoApiServiceImpl implements EchoApi {
  
      public Response getEcho(SecurityContext securityContext) {
      // do some magic!
      Timestamps ts = new Timestamps();
      ts.setTimestamp(new Date());
      return Response.ok(ts).build();
  }
  
}


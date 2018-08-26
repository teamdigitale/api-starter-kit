package io.swagger.api;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

import io.swagger.api.impl.EchoApiServiceImpl;
import io.swagger.api.impl.StatusApiServiceImpl;
import io.swagger.model.Problem;
import io.swagger.model.Timestamps;

public class ServiceTest {

	@Test
	public void testEcho() {
		EchoApiServiceImpl service = new EchoApiServiceImpl();
		javax.ws.rs.core.Response res = service.getEcho(null);
		System.out.println(res);
		assertEquals(res.getStatus(), 200);
		assertTrue(res.getEntity() instanceof Timestamps);
	}

	@Test
	public void testStatus() {
		StatusApiServiceImpl service = new StatusApiServiceImpl();
		javax.ws.rs.core.Response res = service.getStatus(null);
		System.out.println(res);
		assertTrue(res.getEntity() instanceof Problem);
	}

}


FROM maven as builder
RUN mkdir /code -p
WORKDIR /code
ADD . /code/
RUN mvn package

FROM jboss/wildfly
COPY --from=0 /code/target/*.war /opt/jboss/wildfly/standalone/deployments

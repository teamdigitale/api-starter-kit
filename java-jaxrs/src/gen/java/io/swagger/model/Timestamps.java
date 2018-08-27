package io.swagger.model;

import java.util.Objects;
import java.util.ArrayList;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator;
import io.swagger.annotations.ApiModel;
import java.util.Date;


import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;



import javax.validation.constraints.*;





import io.swagger.annotations.*;

@ApiModel(description="Un Timestamp in RFC5424")
@javax.annotation.Generated(value = "io.swagger.codegen.languages.java.JavaResteasyEapServerCodegen", date = "2018-08-25T23:10:21.017Z[GMT]")
public class Timestamps   {

  
  private Date timestamp = null;

  
  /**
   
   
   
   **/
  
  @ApiModelProperty(value = "")
  @JsonProperty("timestamp")






  










  public String getTimestamp() {
    return new DateTime(timestamp).toString();
  }
  public void setTimestamp(Date timestamp) {
    this.timestamp = timestamp;
  }

  

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Timestamps timestamps = (Timestamps) o;
    return Objects.equals(timestamp, timestamps.timestamp);
  }

  @Override
  public int hashCode() {
    return Objects.hash(timestamp);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Timestamps {\n");
    
    sb.append("    timestamp: ").append(toIndentedString(timestamp)).append("\n");
    sb.append("}");
    return sb.toString();
  }

  /**
   * Convert the given object to string with each line indented by 4 spaces
   * (except the first line).
   */
  private String toIndentedString(Object o) {
    if (o == null) {
      return "null";
    }
    return o.toString().replace("\n", "\n    ");
  }
}





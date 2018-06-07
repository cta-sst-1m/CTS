package cta.ctsarraycontrolsystemsst.CTSArrayControlSystemImpl;

import alma.ACSErr.CompletionHolder;
import alma.acs.exceptions.AcsJException;
import cta.acs.opcua.da.UaDataSupport;
import org.apache.commons.lang3.ArrayUtils;

public class UaDataSupportIntegers extends UaDataSupport
{
  public UaDataSupportIntegers(String serverURI, String[] nodeIdRefs)
    throws IllegalArgumentException
  {
    super(serverURI, nodeIdRefs);
  }

  public int[] get(CompletionHolder completionHolder) throws AcsJException
  {
    Object value = super.get(completionHolder);
    if (value == null) {
      return null;
    }
    if ((value instanceof Integer)) {
    	int val = ((Integer)value).intValue();
      return new int[] { val };
    }
    if ((value instanceof Integer[])) {
        Integer[] values = (Integer[])value;
        int[] resValues = new int[values.length];
        for (int i = 0; i < values.length; i++) {
          Integer obj = values[i];
          if (obj != null) {
            resValues[i] = obj.intValue();
          }
        }
        return resValues;
    }
    if ((value instanceof Long[])) {
        Long[] values = (Long[])value;
        int[] resValues = new int[values.length];
        for (int i = 0; i < values.length; i++) {
          Long obj = values[i];
          if (obj != null) {
            resValues[i] = obj.intValue();
          }
        }
        return resValues;
    }
    if ((value instanceof Boolean[])) {
        Boolean[] values = (Boolean[])value;
        int[] resValues = new int[values.length];
        for (int i = 0; i < values.length; i++) {
          Boolean obj = values[i];
          if (obj != null) {
            resValues[i] = (obj) ? 1 : 0;
          }
        }
        return resValues;
    }
    if ((value instanceof Object[])) {
        Object[] values = (Object[])value;
        int[] resValues = new int[values.length];
        for (int i = 0; i < values.length; i++) {
          Object obj = values[i];
          if (obj != null) {
            if (!(obj instanceof Integer)) {
            	throw new IllegalArgumentException("Object[] unexpected data type: " + value.getClass());
          }
          resValues[i] = ((Integer)obj).intValue();
        }
      }
      return resValues;
    }    
    throw new IllegalArgumentException("final unexpected data type: " + value.getClass());
  }

  public void set(Object value, CompletionHolder completionHolder) throws AcsJException
  {
    if (value != null) {
      if ((value instanceof Integer[])) {
        super.set(value, completionHolder);
      }
      else if ((value instanceof int[])) {
        super.set(ArrayUtils.toObject((int[])value), completionHolder);
      }
      else if ((value instanceof Object[])) {
        Object[] objects = (Object[])value;
        Integer[] values = new Integer[objects.length];
        for (int i = 0; i < values.length; i++) {
          Object obj = objects[i];
          if (obj != null) {
            if (!(obj instanceof Integer)) {
              throw new IllegalArgumentException("unexpected data type: " + obj.getClass());
            }
            values[i] = ((Integer)obj);
          }
        }
      }
      throw new IllegalArgumentException("unexpected data type: " + value.getClass());
    }

    super.set(null, completionHolder);
  }
}

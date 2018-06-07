/*
 * Copyright (c) 2014, CTA collaboration. All rights reserved.
 * 
 * @author birsine (HU), mdavid (DESY)
 */
package cta.ctsarraycontrolsystemsst.CTSArrayControlSystemImpl;

import java.util.logging.Logger;

import org.omg.PortableServer.Servant;

import alma.ACS.ACSComponentOperations;
import alma.acs.component.ComponentLifecycle;
import alma.acs.container.ComponentHelper;
import cta.ctsarraycontrolsystemsst.CTSArrayControlSystemOperations;
import cta.ctsarraycontrolsystemsst.CTSArrayControlSystemPOATie;

/**
 * Component helper class. Generated for convenience, but can be modified by the
 * component developer.
 * 
 * @author birsine, HU
 * @author David Melkumyan, DESY
 */
public class CTSArrayControlSystemComponentHelper extends ComponentHelper {
	/**
	 * Constructor
	 * 
	 * @param containerLogger
	 *            logger used only by the parent class.
	 */
	public CTSArrayControlSystemComponentHelper(Logger containerLogger) {
		super(containerLogger);
	}

	/**
	 * @see alma.acs.container.ComponentHelper#_createComponentImpl()
	 */
	@Override
	protected ComponentLifecycle _createComponentImpl() {
		return new CTSArrayControlSystemImpl();
	}

	/**
	 * @see alma.acs.container.ComponentHelper#_getPOATieClass()
	 */
	@Override
	protected Class<? extends Servant> _getPOATieClass() {
		return CTSArrayControlSystemPOATie.class;
	}

	/**
	 * @see alma.acs.container.ComponentHelper#getOperationsInterface()
	 */
	@Override
	protected Class<? extends ACSComponentOperations> _getOperationsInterface() {
		return CTSArrayControlSystemOperations.class;
	}

}

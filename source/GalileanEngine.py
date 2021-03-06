import numpy as numpy
from astropy import units
import math
import Tools
from Formatter import formatter as fmt

from Engine import Engine
from Engine import DummyPlotter

__author__ = "Do Kester"
__year__ = 2017
__license__ = "GPL3"
__version__ = "0.9"
__maintainer__ = "Do"
__status__ = "Development"

#  *
#  * This file is part of the BayesicFitting package.
#  *
#  * BayesicFitting is free software: you can redistribute it and/or modify
#  * it under the terms of the GNU Lesser General Public License as
#  * published by the Free Software Foundation, either version 3 of
#  * the License, or ( at your option ) any later version.
#  *
#  * BayesicFitting is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY; without even the implied warranty of
#  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  * GNU Lesser General Public License for more details.
#  *
#  * The GPL3 license can be found at <http://www.gnu.org/licenses/>.
#  *
#  * A JAVA version of this code was part of the Herschel Common
#  * Science System (HCSS), also under GPL3.
#  *
#  *    2003 - 2014 Do Kester, SRON (Java code)
#  *    2017        Do Kester

class GalileanEngine( Engine ):
    """
    Move all parameters in forward steps, with optional mirroring on the edge.

    Move the parameters in a random direction for N iterations; mirror the direction
    on the gradient of the logLikelihood when the parameters enter the zone of logLlow.

    Attributes
    ----------
    walkers : SampleList
        walkers to be diffused
    errdis : ErrorDistribution
        error distribution to be used
    nstep : int (10)
        average number of steps to be taken
    size : float (0.5)
        average normalized stepsize
    maxtrials : int
        maximum number of trials for various operations
    rng : numpy.random.RandomState
        random number generator


    Author       Do Kester.

    """

    #  *********CONSTRUCTORS***************************************************
    def __init__( self, walkers, errdis, copy=None, seed=4213 ):
        """
        Default Constructor.

        Parameters
        ----------
        walkers : SampleList
            walkers to be diffused
        errdis : ErrorDistribution
            error distribution to be used
        copy : GalileanEngine
            to be copied
        seed : int
            for random number generator
        """
        super( GalileanEngine, self ).__init__( walkers, errdis, copy=copy, seed=seed  )
        self.nstep = 3
        self.size = 0.5

        self.plotter = DummyPlotter( )

    def copy( self ):
        """ Return copy of this.  """
        engine = GalileanEngine( self.walkers, self.errdis, copy=self )
        engine.nstep = self.nstep
        engine.size = self.size
        return engine

    def __str__( self ):
        """ Return the name of this engine.  """
        return str( "GalileanEngine" )

    #  *********EXECUTE***************************************************
    def execute( self, walker, lowLhood, fitIndex=None ):
        """
        Execute the engine by diffusing the parameters.

        Parameters
        ----------
        walker : Sample
            walker to diffuse
        lowLhood : float
            lower limit in logLikelihood
        fitIndex : array_like
            list of the/some parameters indices to be diffused

        Returns
        -------
        int : the number of successfull moves

        """
        model = walker.model
        Lhood = walker.logL
        parlist = walker.parlist
        fitIndex = walker.fitIndex

#        reportCall( )

        npout = 0
        inside = 0
        Ltry = 0

        self.plotter.start( )
        um = UnitMovements( model, parlist, fitIndex, self )

        ptry = parlist.copy()
#        print( ptry )
#        print( um.upar )
#        print( self.unit2Domain( model, um.upar ) )

        nstep = int( self.nstep * ( 1 + self.rng.rand() ) )
        maxtrial = self.maxtrials * nstep
        step = 0
        trial = 0

        while True:
            trial += 1
            um.setParameters( model, parlist )
            if inside == 0 :                            # safely inside lowLhood area
                ptry[fitIndex] = um.stepPars( 1.0 )

                self.plotter.move( parlist, ptry, 0 )
            elif inside == 1 :                          # first time outside -> mirror
                f = ( Lhood - lowLhood ) / ( Lhood - Ltry )     # lin interpolation to edge
                pedge = ptry.copy()
                pedge[fitIndex] = um.stepPars( f )                # ptry on edge
                dLdp = self.errdis.partialLogL( model, pedge, fitIndex )
                self.plotter.move( parlist, pedge, 1 )

                um.mirrorOnLowL( dLdp )
                ptry[fitIndex] = um.stepPars( 1 - f )

                self.plotter.move( pedge, ptry, 2 )
            else:                                       # mirroring failed; do reverse
                um.reverseVelocity( 1.0 )
                ptry[fitIndex] = um.stepPars( 1.0 )

                self.plotter.move( parlist, ptry, 3 )

#            print( ptry )
            Ltry = self.errdis.logLikelihood( model, ptry )
            if Ltry >= lowLhood:
                parlist = ptry.copy( )
                Lhood = Ltry
                self.reportSuccess( )
                npout = len( parlist )
                inside = 0
                step += 1
            else:
                inside += 1
                if inside == 1:
                    self.reportReject( )
                else:
                    self.reportFailed( )
            if not ( step < nstep and trial < maxtrial ):
                break

        self.setSample( walker, model, parlist, Lhood )

        if trial >= maxtrial:
            self.size = self.size * 0.9 + 0.00001

        self.plotter.stop()
        return npout

import matplotlib.pyplot as plt

class UnitMovements( object ):

    def __init__( self, model, parlist, fitIndex, engine ):
        self.model = model
        self.np = len( fitIndex )
        self.fitIndex = fitIndex
#        self.upar = engine.domain2Unit( model, parlist, kpar=fitIndex )
        self.engine = engine
        self.setParameters( model, parlist )
        self.upran = self.engine.unitRange[fitIndex]
#        print( "Range  ", fmt( self.upran ) )
        self.setVelocity( self.engine.size )

    def setParameters( self, model, parlist ):
        self.upar = self.engine.domain2Unit( model, parlist, kpar=self.fitIndex )

    def mirrorOnLowL( self, dLdp ):
        inprod = numpy.inner( dLdp, self.uvel )
        sumsq  = numpy.inner( dLdp, dLdp )
        self.uvel -= 2 * dLdp * inprod / sumsq

    def setVelocity( self, size ):
        if self.model.isDynamic():
            self.setVelocityDynamic( size )
        else:
            self.setVelocityStatic( size )

    def parlist2unit( self, kw ) :
        parlist = self.engine.walkers[kw].parlist
        return self.engine.domain2Unit( self.model, parlist, kpar=self.fitIndex )

    def setVelocityStatic( self, size ):
        # find two randomly chosen walkers
        nm = len( self.engine.walkers )
        k0 = self.engine.rng.randint( nm )
        while True:
            k1 = self.engine.rng.randint( nm )
            if k0 != k1 :
                break

        # subtract the parameter postions to get a velocity
        self.uvel = ( self.parlist2unit( k0 ) - self.parlist2unit( k1 ) ) * size

        # add a random contibution
        rv = self.uniform() * self.upran * size
        self.uvel = ( nm * self.uvel + self.np * rv ) / ( nm + self.np )

    def uniform( self ) :
        return self.engine.rng.rand( self.np ) - 0.5

    def setVelocityDynamic( self, size ):
        self.uvel = self.uniform() * size * self.uran

    def reverseVelocity( self, size ):
        upv = self.uvel
        self.setVelocity( 0.9 * size )
        self.uvel -= upv

    def stepPars( self, f ):
        uv = self.uvel
        pv = self.upar + uv * f
        pv, uv = numpy.where( pv <= 0, ( -pv, -uv ), ( pv, uv ) )
        self.upar, self.uvel = numpy.where( pv >= 1, ( 2 - pv, -uv ), ( pv, uv ) )
        return self.engine.unit2Domain( self.model, self.upar, kpar=self.fitIndex )


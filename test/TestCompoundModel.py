#run with: python3 -m unittest TestCompoundModel

import unittest
import numpy as numpy
from astropy import units
import math
import Tools

from Model import Model
from PolynomialModel import PolynomialModel
from GaussModel import GaussModel
from VoigtModel import VoigtModel


__author__ = "Do Kester"
__year__ = 2017
__license__ = "GPL3"
__version__ = "0.9"
__maintainer__ = "Do"
__status__ = "Development"

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
#  *    2016 Do Kester

class TestCompoundModel( unittest.TestCase ):
    """
    Test harness for Fitter class.

    Author:      Do Kester

    """

    def testOneModel( self ):
        print( "  Test one model" )
        m = GaussModel( )

        self.assertTrue( m.getNumberOfParameters( ) == 3 )
        self.assertTrue( m.npbase == 3 )

        par = numpy.asarray( [3,4,5], dtype=float )
        m.parameters = par

        numpy.testing.assert_array_equal( m.parameters, par )
        self.assertTrue( m.getNumberOfParameters( ) == 3 )
        self.assertTrue( m.npbase == 3 )
        numpy.testing.assert_array_equal( m.parameters, par )

        self.assertTrue( m.getNumberOfParameters( ) == 3 )
        self.assertTrue( m.npbase == 3 )
        par[1] = 10.0
        numpy.testing.assert_array_equal( m.parameters, par )

        fix = numpy.asarray( [0,1,2] )
        self.assertTrue( m.getNumberOfParameters( ) == 3 )
        self.assertTrue( m.npbase == 3 )

    def testTwoModel( self ):
        print( "  Test two models" )

        m = GaussModel( )
        p = PolynomialModel( 1 )

        m.addModel( p )

        print( m.parameters, p.parameters )


        self.assertTrue( m.getNumberOfParameters( ) == 5 )
        self.assertTrue( m.npbase == 3 )
        self.assertTrue( m._next.npbase == 2 )
        self.assertTrue( len( m.parameters ) == 5 )


        par = numpy.asarray( [1,-2,3,-1.2,0.2] )
        m.parameters = par
        print( m.parameters )
        numpy.testing.assert_array_equal( m.parameters, par )

    def testThreeModel( self ):
        print( "  Test three models" )
        m = GaussModel( )
        self.assertTrue( m.chainLength() == 1 )
        p = PolynomialModel( 1 )
        m.addModel( p )
        self.assertTrue( m.chainLength() == 2 )
        s = VoigtModel( )
        m.addModel( s )
        self.assertTrue( m.chainLength() == 3 )

        params = numpy.arange( 9, dtype=float )
        m.parameters = params

        self.assertTrue( m._next == p )
        self.assertTrue( m._next._next == s )
        self.assertTrue( p._next == s )
        self.assertTrue( s._head == m )
        self.assertTrue( p._head == m )
        self.assertTrue( m._head == m )
        self.assertTrue( m.getNumberOfParameters( ) == 9 )
        self.assertTrue( p.getNumberOfParameters( ) == 9 )
        self.assertTrue( s.getNumberOfParameters( ) == 9 )
        self.assertTrue( m.npbase == 3 )
        self.assertTrue( p.npbase == 2 )
        self.assertTrue( s.npbase == 4 )
        self.assertTrue( len( m.parameters ) == 9  )
        self.assertTrue( p.parameters is None  )
        self.assertTrue( s.parameters is None  )


        print( "Isolate second model into p1" )
        p1 = m.isolateModel( 1 )
        print( p1 )
        print( p1.parameters )
        self.assertTrue( isinstance( p1, PolynomialModel ) )

        self.assertTrue( p1._next == None )
        self.assertTrue( p1._head == p1 )
        self.assertTrue( p1.npbase == 2 )
        self.assertTrue( p1.getNumberOfParameters() == 2 )


        self.assertTrue( m._next == p )
        self.assertTrue( m._next._next == s )
        self.assertTrue( p._next == s )
        self.assertTrue( s._head == m )
        self.assertTrue( p._head == m )
        self.assertTrue( m._head == m )
        self.assertTrue( m.getNumberOfParameters( ) == 9 )
        self.assertTrue( p.getNumberOfParameters( ) == 9 )
        self.assertTrue( s.getNumberOfParameters( ) == 9 )
        self.assertTrue( m.npbase == 3 )
        self.assertTrue( p.npbase == 2 )
        self.assertTrue( s.npbase == 4 )

    def testThreeModelLimits( self ):
        print( "  Test three models: limits and domain <> unit" )

        m = GaussModel( )
        p = PolynomialModel( 1 )
        m.addModel( p )
        s = VoigtModel( )
        m.addModel( s )

        print( m.npchain )

        lo = numpy.zeros( 9 )
        hi = numpy.arange( 9 ) + 10.0
        m.setLimits( lo, hi )

        par = numpy.arange( 9, dtype=float )
        unp = m.domain2Unit( par )
        print( par )
        print( unp )
        print( m.unit2Domain( unp ) )
        print( m.partialDomain2Unit( par ) )

        numpy.testing.assert_array_almost_equal( m.unit2Domain( unp ), par, 8 )
        self.assertTrue( m.domain2Unit( par[2], 2 ) == unp[2] )
        self.assertTrue( m.domain2Unit( par[3], 3 ) == unp[3] )
        self.assertTrue( m.domain2Unit( par[6], 6 ) == unp[6] )

    def testTwoModelDerivatives( self ):
        print( "  Test two model derivatives" )
        m = GaussModel( )
        m.addModel( PolynomialModel(1) )
        p = numpy.asarray( [1,-2,3,-1.2,0.2] )
        x = numpy.asarray( [-1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0] )

        print( m )
        m.testPartial( x[3], p )

        part = m.partial( x, p )
        nump = m.numPartial( x, p )
        numpy.testing.assert_array_almost_equal( part, nump, 4 )

        mc = m.copy( )
        self.assertTrue( mc.getNumberOfParameters( ) == 5 )
        self.assertTrue( mc.getNumberOfFittedParameters( ) == 5 )

        mc.parameters = p
        m.parameters = p

        numpy.testing.assert_array_equal( m.result( x ), mc.result( x ) )

        m.addModel( GaussModel() )
        m.parameters =  numpy.asarray( [1,-2,3,1,-2,2,2,3], dtype=float )
        self.assertTrue( m.parameters[2] > 0 )
        self.assertTrue( m.parameters[7] > 0 )
        m.parameters = numpy.asarray( [1,-2,-3,1,-2,2,2,-3], dtype=float )
        m.result( x )
        self.assertTrue( m.parameters[2] > 0 )
        self.assertTrue( m.parameters[7] > 0 )
        m.parameters = numpy.asarray( [1,-2,0,1,-2,2,2,0], dtype=float )
        self.assertWarns( UserWarning, m.result, x )
        self.assertTrue( m.parameters[2] == m.tiny )
        self.assertTrue( m.parameters[7] == m.tiny )
        m.result( x )

    def testTwoModelSubtractDerivatives( self ):
        print( "  Test two model subtract derivatives" )
        m = GaussModel( )
        m.subtractModel( PolynomialModel(1) )
        p = numpy.asarray( [1,-2,3,-1.2,0.2] )
        x = numpy.asarray( [-1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0] )

        print( m )
        m.testPartial( x[3], p )

        part = m.partial( x, p )
        nump = m.numPartial( x, p )
        numpy.testing.assert_array_almost_equal( part, nump, 4 )

        mc = m.copy( )
        self.assertTrue( mc.getNumberOfParameters( ) == 5 )

        mc.parameters = p
        m.parameters = p

        numpy.testing.assert_array_equal( m.result( x ), mc.result( x ) )

    def testTwoModelDerivatives( self ):
        print( "  Test two model multiply derivatives" )
        m = GaussModel( )
        m.multiplyModel( PolynomialModel(1) )
        p = numpy.asarray( [1,-2,3,-1.2,0.2] )
        x = numpy.asarray( [-1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0] )

        print( m )
        m.testPartial( x[3], p )

        part = m.partial( x, p )
        nump = m.numPartial( x, p )
        numpy.testing.assert_array_almost_equal( part, nump, 4 )

        mc = m.copy( )
        self.assertTrue( mc.getNumberOfParameters( ) == 5 )

        mc.parameters = p
        m.parameters = p

        numpy.testing.assert_array_equal( m.result( x ), mc.result( x ) )

    def testTwoModelDivideDerivatives( self ):
        print( "  Test two model divide derivatives" )
        m = GaussModel( )
        m.divideModel( PolynomialModel(1) )
        p = numpy.asarray( [1,-2,3,-1.2,0.2] )
        x = numpy.asarray( [-1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0] )

        print( m )
        m.testPartial( x[3], p )

        part = m.partial( x, p )
        nump = m.numPartial( x, p )
        numpy.testing.assert_array_almost_equal( part, nump, 4 )

        mc = m.copy( )
        self.assertTrue( mc.getNumberOfParameters( ) == 5 )

        mc.parameters = p
        m.parameters = p

        numpy.testing.assert_array_equal( m.result( x ), mc.result( x ) )

    def suite( cls ):
        return unittest.TestCase.suite( CompoundModelTest.__class__ )


if __name__ == '__main__':
    unittest.main()


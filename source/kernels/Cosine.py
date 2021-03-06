import numpy as numpy
from astropy import units
import math
import Tools
from Kernel import Kernel

__author__ = "Do Kester"
__year__ = 2017
__license__ = "GPL3"
__version__ = "0.9"
__maintainer__ = "Do"
__status__ = "Development"

#  *
#  *    This file is part of the BayesicFitting package.
#  *
#  *    BayesicFitting is free software: you can redistribute it and/or modify
#  *    it under the terms of the GNU Lesser General Public License as
#  *    published by the Free Software Foundation, either version 3 of
#  *    the License, or ( at your option ) any later version.
#  *
#  *    BayesicFitting is distributed in the hope that it will be useful,
#  *    but WITHOUT ANY WARRANTY; without even the implied warranty of
#  *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  *    GNU Lesser General Public License for more details.
#  *
#  *    The GPL3 license can be found at <http://www.gnu.org/licenses/>.
#  *
#  * A JAVA version of this code was part of the Herschel Common
#  * Science System (HCSS), also under GPL3.
#  *
#  *    2013 - 2014 Do Kester, SRON (Java code)
#  *    2016 - 2017 Do Kester

class Cosine( Kernel ):
    """
    Cosine is a Kernel function between [-1,1]; it is 0 elsewhere.
    .. math::
        K( x ) = cos( 0.5*PI*x ) if |x| < 1 else  0


    """
    HALFPI = 0.5 * math.pi

    def __init__( self ) :
        super( Cosine, self ).__init__( integral=4/math.pi, fwhm=4.0/3.0 )

    def result( self, x ):
        return numpy.where( numpy.abs( x ) <= 1, numpy.cos( self.HALFPI * x ), 0.0 )

    def resultsq( self, xsq ):
        return self.result( numpy.sqrt( xsq ) )

    def partial( self, x ):
        return numpy.where( numpy.abs( x ) <= 1,
            -self.HALFPI * numpy.sin( self.HALFPI * x ), 0.0 )

    def isBound( self ):
        return True

    def name( self ):
        return str( "Cosine: cos( 0.5*PI*x ) if |x| < 1 else 0" )



# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 13:31:41 2016

@author: hxw186

Unit Test for Negative Binomial Regression

"""

import unittest
from NegBinRegression import negativeBinomialRegression


class NegBinTest(unittest.TestCase):
    
    def test_onlineDataset(self):
        """
        This test case uses the online dataset Medpar.
        The Medpar documentation: http://vincentarelbundock.github.io/Rdatasets/doc/COUNT/medpar.html
        The data path: http://vincentarelbundock.github.com/Rdatasets/csv/COUNT/medpar.csv
        
        There is a example in statsmodels in this link:
        http://statsmodels.sourceforge.net/devel/examples/generated/example_gmle.html
        """
        url = 'http://vincentarelbundock.github.com/Rdatasets/csv/COUNT/medpar.csv'
        import pandas as pd
        medpar = pd.read_csv(url)
        
        import patsy
        y, X = patsy.dmatrices('los~type2+type3+hmo+white', medpar)
        
        res, mod = negativeBinomialRegression(X, y)
        print res.pvalues       
        return res
        
        
if __name__ == '__main__':
    unittest.main()
"""
Hongjian
8/19/2016

Implement Negative Binomial Regression with python
from model to optimization.
"""


from statsmodels.discrete.discrete_model import CountModel, NegativeBinomialResults, \
    NegativeBinomialResultsWrapper
from scipy.special import gammaln, digamma, polygamma
import numpy as np


class NegBin(CountModel):
    """
    negative binomial regression
    """
    
    def __init__(self, endog, exog, **kwds):
        super(NegBin, self).__init__(endog, exog, offset=None,
            exposure=None, missing=None, **kwds)
        
        
    def loglike(self, params):
        alpha = params[-1]
        beta = params[:-1]
        print "=== params in loglike ===", params
        mu = np.exp(np.dot(self.exog, beta))
        print "=== mu in loglike ===", mu
        size = 1 / alpha
        prob = size / (size+mu)
        print "=== size in loglike ===", size
        const = gammaln(size+self.endog) - gammaln(self.endog+1) - gammaln(size)
        print "=== const in loglike ===", const
        ll = const + self.endog*np.log(1-prob) + size*np.log(prob)
        print "=== loglike ===", ll
        return np.sum(ll)
        
        
    def fit(self, start_params=None, method='newton', maxiter = 1000, full_output=1,
            disp=1, callback=None, cov_type='nonrobust', cov_kwds=None, use_t = None,
            **kwds):
        if start_params == None:
            start_params = np.ones(self.exog.shape[1])
            start_params = np.append(start_params, 0.1)
            print start_params
            if self.exog.mean() > 1:
                start_params[:-1] = np.ones(self.exog.shape[1]) * np.log(self.endog.mean())  / self.exog.mean()
            else:
                start_params[:-1] = np.ones(self.exog.shape[1]) * np.log(self.endog.mean())
            print "endog mean:", self.endog.mean(), "log endog mean:", np.log(self.endog.mean())
            print "exog mean", self.exog.mean()
        mlefit = super(NegBin, self).fit(start_params=start_params, maxiter=maxiter, method=method,
                callback=lambda x:x, **kwds)
            
        mlefit._results.params[-1] = np.exp(mlefit._results.params[-1])
        
        nbinfit = NegativeBinomialResults(self, mlefit._results)
        result = NegativeBinomialResultsWrapper(nbinfit)

        if cov_kwds is None:
            cov_kwds = {}  #TODO: make this unnecessary ?
        result._get_robustcov_results(cov_type=cov_type,
                                    use_self=True, use_t=use_t, **cov_kwds)
        return result
                

    def score(self, params, **kwds):
        """
        Gradient of log-likelihood evaluated at params
        """
        alpha = params[-1]
        beta = params[:-1]
        exog = self.exog
        y = self.endog[:,None]
        mu = np.exp(np.dot(self.exog, beta))[:,None]
        a1 = 1 / alpha
        
        dparams = exog*a1*(y-mu)/(a1+mu)
        dalpha = (digamma(a1) - digamma(y+a1) + np.log(1+alpha*mu) + \
                alpha* (y-mu)/(1+alpha*mu)).sum() / alpha**2
        
        res = np.r_[dparams.sum(0), dalpha]
        return res
        
    
    def hessian(self, params):
        """
        Hessian of NB2 model.
        """
        if False: # lnalpha came in during fit
            alpha = np.exp(params[-1])
        else:
            alpha = params[-1]
        a1 = 1/alpha
        beta = params[:-1]

        exog = self.exog
        y = self.endog[:,None]
        mu = np.exp(np.dot(self.exog, beta))[:,None]

        # for dl/dparams dparams
        dim = exog.shape[1]
        hess_arr = np.empty((dim+1,dim+1))
        const_arr = a1*mu*(a1+y)/(mu+a1)**2
        for i in range(dim):
            for j in range(dim):
                if j > i:
                    continue
                hess_arr[i,j] = np.sum(-exog[:,i,None] * exog[:,j,None] *
                                       const_arr, axis=0)
        tri_idx = np.triu_indices(dim, k=1)
        hess_arr[tri_idx] = hess_arr.T[tri_idx]

        # for dl/dparams dalpha
        da1 = -alpha**-2
        dldpda = np.sum(mu*exog*(y-mu)*da1/(mu+a1)**2 , axis=0)
        hess_arr[-1,:-1] = dldpda
        hess_arr[:-1,-1] = dldpda

        # for dl/dalpha dalpha
        #NOTE: polygamma(1,x) is the trigamma function
        da2 = 2*alpha**-3
        dalpha = da1 * (digamma(a1+y) - digamma(a1) +
                    np.log(a1) - np.log(a1+mu) - (a1+y)/(a1+mu) + 1)
        dada = (da2 * dalpha/da1 + da1**2 * (polygamma(1, a1+y) -
                    polygamma(1, a1) + 1/a1 - 1/(a1 + mu) +
                    (y - mu)/(mu + a1)**2)).sum()
        hess_arr[-1,-1] = dada

        return hess_arr
                
    
    def predict(self, params, exog=None, *args, **kwargs):
        """
        predict the acutal endogenous count from exog
        """
        beta = params[:-1]
        return np.exp(exog.dot(beta))
  


    
def negativeBinomialRegression(features, Y):
    """
    learn the NB regression
    """
    mod = NegBin(Y, features)
    res = mod.fit(disp=False)
    if not res.mle_retvals['converged']:
        print "NBreg not converged."
    return res, mod
    
    
    
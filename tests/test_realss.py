from itertools import product
import numpy as np
import scipy.linalg
from sysmor.realss import _residual, _jacobian


def test_residual(p = 3, m = 2, M = 1000, r_c = 2, r_r = 3):
	np.random.seed(0)
	z = 0.1+1j*np.linspace(-1,1, M)
	Y = np.random.randn(M, p, m)
	# complex conjugate poles
	alpha = -np.random.rand(r_c)
	beta = -np.random.rand(r_c)
	B = np.random.randn(r_c*2, m)
	C = np.random.randn(p, r_c*2)
	# real poles
	gamma = -np.random.rand(r_r)
	b = np.random.randn(r_r, m)
	c = np.random.randn(p, r_r)

	res_true = np.zeros((M, p, m), dtype = np.complex)
	A = np.zeros((2,2), dtype = np.complex)
	for i in range(M):
		res_true[i] = Y[i]
		for k in range(r_c):
			A[0,0] = alpha[k] - z[i]
			A[1,1] = alpha[k] - z[i]
			A[0,1] = beta[k]
			A[1,0] = -beta[k]
			res_true[i] -= C[:,k*2:(k+1)*2] @ scipy.linalg.solve(A, B[k*2:(k+1)*2])

		for k in range(r_r):
			res_true[i] -= (c[:,k:k+1] @ b[k:k+1,:])/(gamma[k] - z[i])
	
	res = _residual(z, Y, alpha, beta, B, C, gamma, b, c)
	assert np.all(np.isclose(res, res_true))

def test_jacobian(p = 3, m = 2, M = 100, r_c = 2, r_r = 3):
	np.random.seed(0)
	z = 0.1+1j*np.linspace(-1,1, M)
	Y = np.random.randn(M, p, m)
	# complex conjugate poles
	alpha = -np.random.rand(r_c)
	beta = -np.random.rand(r_c)
	B = np.random.randn(r_c*2, m)
	C = np.random.randn(p, r_c*2)
	# real poles
	gamma = -np.random.rand(r_r)
	b = np.random.randn(r_r, m)
	c = np.random.randn(p, r_r)


	# Check Jalpha
	h = 1e-6
	Jalpha, Jbeta, JB, JC, Jgamma, Jb, Jc = _jacobian(z, Y, alpha, beta, B, C, gamma, b, c)

	for k in range(r_c):
		ek = np.eye(r_c)[k]
		Jest = _residual(z, Y, alpha + h*ek, beta, B, C, gamma, b, c) 
		Jest -= _residual(z, Y, alpha - h*ek, beta, B, C, gamma, b, c) 
		Jest /= 2*h
		assert np.all(np.isclose(Jalpha[...,k], Jest))

	for k in range(r_c):
		ek = np.eye(r_c)[k]
		Jest = _residual(z, Y, alpha, beta+h*ek, B, C, gamma, b, c) 
		Jest -= _residual(z, Y, alpha, beta-h*ek, B, C, gamma, b, c) 
		Jest /= 2*h
		assert np.all(np.isclose(Jbeta[...,k], Jest))
	
	for idx in np.ndindex(2*r_c, m):
		eB = np.zeros_like(B)
		eB[idx] = 1
		Jest = _residual(z, Y, alpha, beta, B + h*eB, C, gamma, b, c) 
		Jest -= _residual(z, Y, alpha, beta, B - h*eB, C, gamma, b, c) 
		Jest /= 2*h
		assert np.all(np.isclose(JB[...,idx[0], idx[1]], Jest))
	
	for idx in np.ndindex(p, 2*r_c):
		eC = np.zeros_like(C)
		eC[idx] = 1
		Jest = _residual(z, Y, alpha, beta, B, C + h*eC, gamma, b, c) 
		Jest -= _residual(z, Y, alpha, beta, B, C - h*eC, gamma, b, c) 
		Jest /= 2*h
		assert np.all(np.isclose(JC[...,idx[0], idx[1]], Jest))

	for k in range(r_r):
		ek = np.eye(r_r)[k]
		Jest = _residual(z, Y, alpha, beta, B, C, gamma+h*ek, b, c) 
		Jest -= _residual(z, Y, alpha, beta, B, C, gamma-h*ek, b, c) 
		Jest /= 2*h
		assert np.all(np.isclose(Jgamma[...,k], Jest))

	for k, j in product(range(r_r), range(m)):
		eb = np.zeros_like(b)
		eb[k,j] = 1.
		Jest = _residual(z, Y, alpha, beta, B, C, gamma, b+h*eb, c) 
		Jest -= _residual(z, Y, alpha, beta, B, C, gamma, b-h*eb, c) 
		Jest /= 2*h
		assert np.all(np.isclose(Jb[...,k,j], Jest))
	
	for k, j in product(range(r_r), range(p)):
		ec = np.zeros_like(c)
		ec[j,k] = 1.
		Jest = _residual(z, Y, alpha, beta, B, C, gamma, b, c+h*ec) 
		Jest -= _residual(z, Y, alpha, beta, B, C, gamma, b, c-h*ec) 
		Jest /= 2*h
		assert np.all(np.isclose(Jc[...,j,k], Jest))

if __name__ == '__main__':
	#test_residual()
	test_jacobian()
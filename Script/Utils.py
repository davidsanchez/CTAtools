import os,sys,numpy


def LiMa(non, noff, alpha):
	excess = non - noff*alpha;

	if (alpha == 0):
			return sqrt(non)

	if excess>0 :
		n1 = non;
		n2 = noff;
		sign = 1.0;
		a = alpha;
	else :
		n2 = non;
		n1 = noff;
		sign = -1.0;
		a = 1.0/alpha;

	if(n2 == 0): 
		return sign * numpy.sqrt(2 * n1 * numpy.log((1+a)/a));
	if(n1 == 0):
		return sign * numpy.sqrt(2 * n2 * numpy.log(1+a));

	# the standard Li & Ma formula:
	nt = n1+n2;
	pa = 1 + a;

	t1 = n1*numpy.log((pa/a)*(n1/nt));
	t2 = n2*numpy.log(pa*(n2/nt));
	sig = numpy.sqrt(2)*numpy.sqrt(numpy.abs(t1+t2));

	return sign*sig;
// hi! this source code is not intended to be reverse engineered. thanks

/* ================================================================
 * probability-distributions by Matt Asher (me[at]mattasher.com)
 * Originally created for StatisticsBlog.com
 *
 * first created at : Sat Oct 10 2015
 *
 * ================================================================
 * Copyright 2015 Matt Asher
 *
 * Licensed under the MIT License
 * You may not use this file except in compliance with the License.
 *
 * ================================================================ */

// Shortcuts
var exp = Math.exp;
var ln = Math.log;
var PI = Math.PI;
var pow = Math.pow;

var PD = {

    /**
     * This is the core function for generating entropy
     *
     * @param len number of bytes of entropy to create
     * @returns {number} A pseduo random number between 0 and 1
     *
     */
    prng: function(len) {
        return Math.random()
    },




    /**
     *
     * @param n The number of random variates to create. Must be a positive integer.
     * @param alpha First shape parameter
     * @param beta Second shape parameter
     * @param loc Location or Non-centrality parameter
     */
    rbeta: function(n, alpha, beta, loc) {
        // Uses relationship with gamma to calculate

        // Validations
        n = this._v(n, "n");
        alpha = this._v(alpha, "nn", 1);
        beta = this._v(beta, "nn", 1);
        loc =  this._v(loc, "r", 0);

        var toReturn = [];

        for(var i=0; i<n; i++) {
            var g1 = this.rgamma(1, alpha, 1)[0];
            var g2 = this.rgamma(1, beta, 1)[0];


            toReturn[i] = loc + g1/(g1+g2);
        }
        return toReturn

    },


    /**
     *
     * @param n Number of variates to return.
     * @param size Number of Bernoulli trials to be summed up. Defaults to 1
     * @param p Probability of a "success". Defaults to 0.5
     * @returns {Array} Random variates array
     */
    rbinom: function(n, size, p) {
        n = this._v(n, "n");
        size = this._v(size, "nni", 1);
        p = this._v(p, "p", 0.5);

        var toReturn = [];

        for(var i=0; i<n; i++) {
            var result = 0;
            for(var j=0; j<size; j++) {
                if(this.prng() < p) {
                    result++
                }
            }
            toReturn[i] = result;
        }
        return toReturn
    },


    /**
     *
     * @param n The number of variates to create
     * @param df Degrees of freedom for the distribution
     * @param ncp Non-centrality parameter
     * @returns {Array} Random variates array
     */
    rchisq: function(n, df, ncp) {
        n = this._v(n, "n");
        df = this._v(df, "nn");
        ncp = this._v(ncp, "r", 0);

        var toReturn = [];
        for(var i=0; i<n; i++) {
            // Start at ncp
            var x = ncp;
            for(var j=0; j<df; j++) {
                x = x + Math.pow(this.rnorm(1)[0],2);
            }
            toReturn[i] = x;
        }
        return toReturn
    },

    /**
     *
     * @param n The number of random variates to create. Must be a positive integer.
     * @param rate The rate parameter. Must be a positive number
     */
    rexp: function(n, rate) {
        n = this._v(n, "n");
        rate = this._v(rate, "pos", 1);

        var toReturn = [];

        for(var i=0; i<n; i++) {

            toReturn[i] =  -ln(this.prng())/rate;
        }

        return toReturn
    },



    /**
     *
     * @param n The number of random variates to create. Must be a positive integer
     * @param alpha
     * @param rate
     * @returns {Array} Random variates array
     */
    rgamma: function(n, alpha, rate) {
        // Adapted from https://github.com/mvarshney/simjs-source/ & scipy
        n = this._v(n, "n");
        alpha = this._v(alpha, "nn");
        rate = this._v(rate, "pos", 1);

        var LOG4 = ln(4.0);
        var SG_MAGICCONST = 1.0 + ln(4.5);
        var beta = 1/rate;

        var toReturn = [];
        for(var i = 0; i<n; i++) {

            /* Based on Python 2.6 source code of random.py.
             */

            if (alpha > 1.0) {
                var ainv = Math.sqrt(2.0 * alpha - 1.0);
                var bbb = alpha - LOG4;
                var ccc = alpha + ainv;

                while (true) {
                    var u1 = this.prng();
                    if ((u1 < 1e-7) || (u > 0.9999999)) {
                        continue;
                    }
                    var u2 = 1.0 - this.prng();
                    var v = ln(u1 / (1.0 - u1)) / ainv;
                    var x = alpha * exp(v);
                    var z = u1 * u1 * u2;
                    var r = bbb + ccc * v - x;
                    if ((r + SG_MAGICCONST - 4.5 * z >= 0.0) || (r >= ln(z))) {
                        var result = x * beta;
                        break;
                    }
                }
            } else if (alpha == 1.0) {
                var u = this.prng();
                while (u <= 1e-7) {
                    u = this.prng();
                }
                var result = - ln(u) * beta;
            } else {
                while (true) {
                    var u = this.prng();
                    var b = (Math.E + alpha) / Math.E;
                    var p = b * u;
                    if (p <= 1.0) {
                        var x = Math.pow(p, 1.0 / alpha);
                    } else {
                        var x = - ln((b - p) / alpha);
                    }
                    var u1 = this.prng();
                    if (p > 1.0) {
                        if (u1 <= Math.pow(x, (alpha - 1.0))) {
                            break;
                        }
                    } else if (u1 <= exp(-x)) {
                        break;
                    }
                }
                var result =  x * beta;
            }

            toReturn[i] = result;
        }

        return toReturn;

    },


    /**
     *
     * @param n The number of random variates to create. Must be a positive integer.
     * @param size Number of hits required
     * @param p Hit probability
     * @param mu Optional way to specify hit probability
     * @returns {Array} Random variates array
     */
    rnbinom: function(n, size, p, mu) {
        n = this._v(n, "n");
        if(size === undefined) size=1;
        if(Math.round(size) != size) throw new Error("Size must be a whole number");
        if(size < 1) throw new Error("Size must be one or greater");
        if(p !== undefined && mu !== undefined) throw new Error("You must specify probability or mean, not both");
        if(mu !== undefined) p = size/(size+mu);
        p = this._v(p, "p");


        var toReturn = [];

        for(var i=0; i<n; i++) {

            // Core distribution
            var result = 0;
            var leftToFind = size;
            while(leftToFind > 0) {
                result++;
                if(this.prng() < p) leftToFind--;
            }

            toReturn[i] = result - 1;
        }

        return toReturn

    },


    /**
     *
     * @param n The number of random variates to create. Must be a positive integer.
     * @param mean Mean of the distribution
     * @param sd Standard Deviation of the distribution
     * @returns {Array} Random variates array
     */
    rnorm: function(n, mean, sd) {
        // Adapted from http://blog.yjl.im/2010/09/simulating-normal-random-variable-using.html

        n = this._v(n, "n");
        mean = this._v(mean, "r", 0);
        sd = this._v(sd, "nn", 1);

        var toReturn = [];

        for(var i=0; i<n; i++) {
            var V1, V2, S, X;

            do {
                var U1 = this.prng();
                var U2 = this.prng();
                V1 = (2 * U1) - 1;
                V2 = (2 * U2) - 1;
                S = (V1 * V1) + (V2 * V2);
            } while (S > 1);

            X = Math.sqrt(-2 * ln(S) / S) * V1;
            X = mean + sd * X;
            toReturn.push(X);
        }

        return toReturn
    },



    /**
     *
     * @param n The number of random variates to create. Must be a positive integer.
     * @param lambda Mean/Variance of the distribution
     * @returns {Array} Random variates array
     */
    rpois: function(n, lambda) {
        n = this._v(n, "n");
        lambda = this._v(lambda, "pos");

        var toReturn = [];

        for(var i=0; i<n; i++) {

            // Adapted from http://wiki.q-researchsoftware.com/wiki/How_to_Generate_Random_Numbers:_Poisson_Distribution
            if (lambda < 30) {

                var L = exp(-lambda);
                var p = 1;
                var k = 0;
                do {
                    k++;
                    p *= this.prng();
                } while (p > L);
                toReturn.push(k - 1);

            } else {

                // Roll our own
                // Fix total number of samples
                var samples = 10000;
                var p = lambda/samples;
                var k = 0;
                for(var j=0; j<samples; j++) {
                    if(this.prng() < p) {
                        k++
                    }
                }
                toReturn[i] = k;
            }
        }

        return toReturn
    },

    /**
     *
     * @param n  Number of variates to return
     * @param min Lower bound
     * @param max Upper bound
     * @returns {Array} Random variates array
     */
    runif: function(n, min, max) {
        n = this._v(n, "n");
        min = this._v(min, "r", 0);
        max = this._v(max, "r", 1);
        if(min > max) throw new Error("Minimum value cannot be greater than maximum value");
        var toReturn = [];

        for(var i=0; i<n; i++) {
            var raw = this.prng();
            var scaled = min + raw*(max-min);
            toReturn.push(scaled)
        }
        return toReturn
    },


    // HELPERS

    /**
     *
     * @param ratios Array of non-negative numbers to be turned into CDF
     * @param len length of the collection
     * @returns {Array}
     * @private
     */
    _getCumulativeProbs: function(ratios, len) {
        if(len === undefined) throw new Error("An error occurred: len was not sent to _getCumulativeProbs");
        if(ratios.length !== len) throw new Error("Probabilities for sample must be same length as the array to sample from");

        var toReturn = [];

        if(ratios !== undefined) {
            ratios = this._v(ratios, "a");
            if(ratios.length !== len) throw new Error("Probabilities array must be the same length as the array you are sampling from");

            var sum = 0;
            ratios.map(function(ratio) {
                ratio = this._v(ratio, "nn"); // Note validating as ANY non-negative number
                sum+= ratio;
                toReturn.push(sum);
            }.bind(this));

            // Divide by total to normalize
            for(var k=0; k<toReturn.length; k++) { toReturn[k] = toReturn[k]/sum }
            return toReturn
        }
    },

    _sampleOneIndex: function(cumulativeProbs) {

        var toTake = this.prng();

        // Find out where this lands in weights
        var cur = 0;
        while(toTake > cumulativeProbs[cur]) cur++;

        return cur;
    },

    _factorial: function(n) {
        var toReturn=1;
        for (var i = 2; i <= n; i++)
            toReturn = toReturn * i;

        return toReturn;
    },

    // Return default if undefined, otherwise validate
    // Return a COPY of the validated parameter
    _v: function(param, type, defaultParam) {
        if(param == null && defaultParam != null)
            return defaultParam;

        switch(type) {

            // Array of 1 item or more
            case "a":
                if(!Array.isArray(param) || !param.length) throw new Error("Expected an array of length 1 or greater");
                return param.slice(0);

            // Integer
            case "int":
                if(param !== Number(param)) throw new Error("A required parameter is missing or not a number");
                if(param !== Math.round(param)) throw new Error("Parameter must be a whole number");
                if(param === Infinity) throw new Error("Sent 'infinity' as a parameter");
                return param;

            // Natural number
            case "n":
                if(param === undefined) throw new Error("You must specify how many values you want");
                if(param !== Number(param)) throw new Error("The number of values must be numeric");
                if(param !== Math.round(param)) throw new Error("The number of values must be a whole number");
                if(param < 1) throw new Error("The number of values must be a whole number of 1 or greater");
                if(param === Infinity) throw new Error("The number of values cannot be infinite ;-)");
                return param;

            // Valid probability
            case "p":
                if(Number(param) !== param) throw new Error("Probability value is missing or not a number");
                if(param > 1) throw new Error("Probability values cannot be greater than 1");
                if(param < 0) throw new Error("Probability values cannot be less than 0");
                return param;

            // Positive numbers
            case "pos":
                if(Number(param) !== param) throw new Error("A required parameter is missing or not a number");
                if(param <= 0) throw new Error("Parameter must be greater than 0");
                if(param === Infinity) throw new Error("Sent 'infinity' as a parameter");
                return param;

            // Look for numbers (reals)
            case "r":
                if(Number(param) !== param) throw new Error("A required parameter is missing or not a number");
                if(param === Infinity) throw new Error("Sent 'infinity' as a parameter");
                return param;

            // Non negative real number
            case "nn":
                if(param !== Number(param)) throw new Error("A required parameter is missing or not a number");
                if(param < 0) throw new Error("Parameter cannot be less than 0");
                if(param === Infinity) throw new Error("Sent 'infinity' as a parameter");
                return param;

            // Non negative whole number (integer)
            case "nni":
                if(param !== Number(param)) throw new Error("A required parameter is missing or not a number");
                if(param !== Math.round(param)) throw new Error("Parameter must be a whole number");
                if(param < 0) throw new Error("Parameter cannot be less than zero");
                if(param === Infinity) throw new Error("Sent 'infinity' as a parameter");
                return param;

            // Non-empty string
            case "str":
                if(param !== String(param)) throw new Error("A required parameter is missing or not a string");
                if(param.length === 0) throw new Error("Parameter must be at least one character long");
                return param;


        }
    },
};

function getRow() {
    var dresscode_1 = PD.runif(1,4,7)
    var dresscode_2 = PD.runif(1,2,4)
    var giant_growth_1 = PD.rexp(1,2)
    var giant_growth_2 = PD.rexp(1,6)
    var product_testing = PD.rbeta(1,4,1)
    var xbox = PD.rchisq(1,1)
    var xbox2 = PD.rchisq(1,3)
    var sole_men = PD.rpois(1,4)
    var sole_men2 = PD.rpois(1,8)
    var sole_men3 = PD.rpois(1,1)
    var conventional = PD.rnorm(1,4,Math.sqrt(3))
    var conventional2 = PD.rnorm(1,5,Math.sqrt(6))

    return [product_testing, conventional, dresscode_1, conventional2, dresscode_2, giant_growth_1, conventional, conventional2, xbox, sole_men, dresscode_2, product_testing, dresscode_1, sole_men2, giant_growth_2, xbox2, sole_men3]
}

function getData(count) {
    var res = []
    for (var i = 0; i < count; i++) {
        res.push(getRow().map(x => x[0].toFixed(3)).join("\t"))
    }
    return res
}

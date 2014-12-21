#! /usr/bin/env python
#
# Author: Damian Eads
# Date: April 17, 2008
#
# Copyright (C) 2008 Damian Eads
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#
# 3. The name of the author may not be used to endorse or promote
#    products derived from this software without specific prior
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import division, print_function, absolute_import

import numpy as np
from numpy.testing import (TestCase, run_module_suite, dec, assert_raises,
                           assert_allclose, assert_equal, assert_)

from scipy.lib.six import xrange

import scipy.cluster.hierarchy
from scipy.cluster.hierarchy import (
    linkage, from_mlab_linkage, to_mlab_linkage, num_obs_linkage, inconsistent,
    cophenet, fclusterdata, fcluster, is_isomorphic, single, leaders,
    correspond, is_monotonic, maxdists, maxinconsts, maxRstat,
    is_valid_linkage, is_valid_im, to_tree, leaves_list, dendrogram,
    set_link_color_palette)
from scipy.spatial.distance import pdist

import hierarchy_test_data


# Matplotlib is not a scipy dependency but is optionally used in dendrogram, so
# check if it's available
try:
    import matplotlib
    # and set the backend to be Agg (no gui)
    matplotlib.use('Agg')
    # before importing pyplot
    import matplotlib.pyplot as plt
    have_matplotlib = True
except:
    have_matplotlib = False


class TestLinkage(object):
    def test_linkage_empty_distance_matrix(self):
        # Tests linkage(Y) where Y is a 0x4 linkage matrix. Exception expected.
        y = np.zeros((0,))
        assert_raises(ValueError, linkage, y)

    def test_linkage_tdist(self):
        for method in ['single', 'complete', 'average', 'weighted', u'single']:
            yield self.check_linkage_tdist, method

    def check_linkage_tdist(self, method):
        # Tests linkage(Y, method) on the tdist data set.
        Z = linkage(hierarchy_test_data.ytdist, method)
        expectedZ = getattr(hierarchy_test_data, 'linkage_ytdist_' + method)
        assert_allclose(Z, expectedZ, atol=1e-10)

    def test_linkage_X(self):
        for method in ['centroid', 'median', 'ward']:
            yield self.check_linkage_q, method

    def check_linkage_q(self, method):
        # Tests linkage(Y, method) on the Q data set.
        Z = linkage(hierarchy_test_data.X, method)
        expectedZ = getattr(hierarchy_test_data, 'linkage_X_' + method)
        assert_allclose(Z, expectedZ, atol=1e-06)


class TestInconsistent(object):
    def test_inconsistent_tdist(self):
        for depth in hierarchy_test_data.inconsistent_ytdist:
            yield self.check_inconsistent_tdist, depth

    def check_inconsistent_tdist(self, depth):
        Z = hierarchy_test_data.linkage_ytdist_single
        assert_allclose(inconsistent(Z, depth),
                        hierarchy_test_data.inconsistent_ytdist[depth])


class TestCopheneticDistance(object):
    def test_linkage_cophenet_tdist_Z(self):
        # Tests cophenet(Z) on tdist data set.
        expectedM = np.array([268, 295, 255, 255, 295, 295, 268, 268, 295, 295,
                              295, 138, 219, 295, 295])
        Z = hierarchy_test_data.linkage_ytdist_single
        M = cophenet(Z)
        assert_allclose(M, expectedM, atol=1e-10)

    def test_linkage_cophenet_tdist_Z_Y(self):
        # Tests cophenet(Z, Y) on tdist data set.
        Z = hierarchy_test_data.linkage_ytdist_single
        (c, M) = cophenet(Z, hierarchy_test_data.ytdist)
        expectedM = np.array([268, 295, 255, 255, 295, 295, 268, 268, 295, 295,
                              295, 138, 219, 295, 295])
        expectedc = 0.639931296433393415057366837573
        assert_allclose(c, expectedc, atol=1e-10)
        assert_allclose(M, expectedM, atol=1e-10)


class TestMLabLinkageConversion(object):
    def test_mlab_linkage_conversion_empty(self):
        # Tests from/to_mlab_linkage on empty linkage array.
        X = np.asarray([])
        assert_equal(from_mlab_linkage([]), X)
        assert_equal(to_mlab_linkage([]), X)

    def test_mlab_linkage_conversion_single_row(self):
        # Tests from/to_mlab_linkage on linkage array with single row.
        Z = np.asarray([[0., 1., 3., 2.]])
        Zm = [[1, 2, 3]]
        assert_equal(from_mlab_linkage(Zm), Z)
        assert_equal(to_mlab_linkage(Z), Zm)

    def test_mlab_linkage_conversion_multiple_rows(self):
        # Tests from/to_mlab_linkage on linkage array with multiple rows.
        Zm = np.asarray([[3, 6, 138], [4, 5, 219],
                         [1, 8, 255], [2, 9, 268], [7, 10, 295]])
        Z = np.array([[2., 5., 138., 2.],
                      [3., 4., 219., 2.],
                      [0., 7., 255., 3.],
                      [1., 8., 268., 4.],
                      [6., 9., 295., 6.]],
                      dtype=np.double)
        assert_equal(from_mlab_linkage(Zm), Z)
        assert_equal(to_mlab_linkage(Z), Zm)


class TestFcluster(object):
    def test_fclusterdata(self):
        for t in hierarchy_test_data.fcluster_inconsistent:
            yield self.check_fclusterdata, t, 'inconsistent'
        for t in hierarchy_test_data.fcluster_distance:
            yield self.check_fclusterdata, t, 'distance'
        for t in hierarchy_test_data.fcluster_maxclust:
            yield self.check_fclusterdata, t, 'maxclust'

    def check_fclusterdata(self, t, criterion):
        # Tests fclusterdata(X, criterion=criterion, t=t) on a random 3-cluster data set.
        expectedT = getattr(hierarchy_test_data, 'fcluster_' + criterion)[t]
        X = hierarchy_test_data.Q_X
        T = fclusterdata(X, criterion=criterion, t=t)
        assert_(is_isomorphic(T, expectedT))

    def test_fcluster(self):
        for t in hierarchy_test_data.fcluster_inconsistent:
            yield self.check_fcluster, t, 'inconsistent'
        for t in hierarchy_test_data.fcluster_distance:
            yield self.check_fcluster, t, 'distance'
        for t in hierarchy_test_data.fcluster_maxclust:
            yield self.check_fcluster, t, 'maxclust'

    def check_fcluster(self, t, criterion):
        # Tests fcluster(Z, criterion=criterion, t=t) on a random 3-cluster data set.
        expectedT = getattr(hierarchy_test_data, 'fcluster_' + criterion)[t]
        Z = single(hierarchy_test_data.Q_X)
        T = fcluster(Z, criterion=criterion, t=t)
        assert_(is_isomorphic(T, expectedT))

    def test_fcluster_monocrit(self):
        for t in hierarchy_test_data.fcluster_distance:
            yield self.check_fcluster_monocrit, t
        for t in hierarchy_test_data.fcluster_maxclust:
            yield self.check_fcluster_maxclust_monocrit, t

    def check_fcluster_monocrit(self, t):
        expectedT = hierarchy_test_data.fcluster_distance[t]
        Z = single(hierarchy_test_data.Q_X)
        T = fcluster(Z, t, criterion='monocrit', monocrit=maxdists(Z))
        assert_(is_isomorphic(T, expectedT))

    def check_fcluster_maxclust_monocrit(self, t):
        expectedT = hierarchy_test_data.fcluster_maxclust[t]
        Z = single(hierarchy_test_data.Q_X)
        T = fcluster(Z, t, criterion='maxclust_monocrit', monocrit=maxdists(Z))
        assert_(is_isomorphic(T, expectedT))


class TestLeaders(object):
    def test_leaders_single(self):
        # Tests leaders using a flat clustering generated by single linkage.
        X = hierarchy_test_data.Q_X
        Y = pdist(X)
        Z = linkage(Y)
        T = fcluster(Z, criterion='maxclust', t=3)
        Lright = (np.array([53, 55, 56]), np.array([2, 3, 1]))
        L = leaders(Z, T)
        assert_equal(L, Lright)


class TestIsIsomorphic(object):
    def test_is_isomorphic_1(self):
        # Tests is_isomorphic on test case #1 (one flat cluster, different labellings)
        a = [1, 1, 1]
        b = [2, 2, 2]
        assert_(is_isomorphic(a, b))
        assert_(is_isomorphic(b, a))

    def test_is_isomorphic_2(self):
        # Tests is_isomorphic on test case #2 (two flat clusters, different labelings)
        a = [1, 7, 1]
        b = [2, 3, 2]
        assert_(is_isomorphic(a, b))
        assert_(is_isomorphic(b, a))

    def test_is_isomorphic_3(self):
        # Tests is_isomorphic on test case #3 (no flat clusters)
        a = []
        b = []
        assert_(is_isomorphic(a, b))

    def test_is_isomorphic_4A(self):
        # Tests is_isomorphic on test case #4A (3 flat clusters, different labelings, isomorphic)
        a = [1, 2, 3]
        b = [1, 3, 2]
        assert_(is_isomorphic(a, b))
        assert_(is_isomorphic(b, a))

    def test_is_isomorphic_4B(self):
        # Tests is_isomorphic on test case #4B (3 flat clusters, different labelings, nonisomorphic)
        a = [1, 2, 3, 3]
        b = [1, 3, 2, 3]
        assert_(is_isomorphic(a, b) == False)
        assert_(is_isomorphic(b, a) == False)

    def test_is_isomorphic_4C(self):
        # Tests is_isomorphic on test case #4C (3 flat clusters, different labelings, isomorphic)
        a = [7, 2, 3]
        b = [6, 3, 2]
        assert_(is_isomorphic(a, b))
        assert_(is_isomorphic(b, a))

    def test_is_isomorphic_5(self):
        # Tests is_isomorphic on test case #5 (1000 observations, 2/3/5 random
        # clusters, random permutation of the labeling).
        for nc in [2, 3, 5]:
            yield self.help_is_isomorphic_randperm, 1000, nc

    def test_is_isomorphic_6(self):
        # Tests is_isomorphic on test case #5A (1000 observations, 2/3/5 random
        # clusters, random permutation of the labeling, slightly
        # nonisomorphic.)
        for nc in [2, 3, 5]:
            yield self.help_is_isomorphic_randperm, 1000, nc, True, 5

    def help_is_isomorphic_randperm(self, nobs, nclusters, noniso=False, nerrors=0):
        for k in range(3):
            a = np.int_(np.random.rand(nobs) * nclusters)
            b = np.zeros(a.size, dtype=np.int_)
            P = np.random.permutation(nclusters)
            for i in xrange(0, a.shape[0]):
                b[i] = P[a[i]]
            if noniso:
                Q = np.random.permutation(nobs)
                b[Q[0:nerrors]] += 1
                b[Q[0:nerrors]] %= nclusters
            assert_(is_isomorphic(a, b) == (not noniso))
            assert_(is_isomorphic(b, a) == (not noniso))


class TestIsValidLinkage(object):
    def test_is_valid_linkage_various_size(self):
        for nrow, ncol, valid in [(2, 5, False), (2, 3, False),
                                  (1, 4, True), (2, 4, True)]:
            yield self.check_is_valid_linkage_various_size, nrow, ncol, valid

    def check_is_valid_linkage_various_size(self, nrow, ncol, valid):
        # Tests is_valid_linkage(Z) with linkage matrics of various sizes
        Z = np.asarray([[0, 1, 3.0, 2, 5],
                        [3, 2, 4.0, 3, 3]], dtype=np.double)
        Z = Z[:nrow, :ncol]
        assert_(is_valid_linkage(Z) == valid)
        if not valid:
            assert_raises(ValueError, is_valid_linkage, Z, throw=True)

    def test_is_valid_linkage_int_type(self):
        # Tests is_valid_linkage(Z) with integer type.
        Z = np.asarray([[0, 1, 3.0, 2],
                        [3, 2, 4.0, 3]], dtype=np.int)
        assert_(is_valid_linkage(Z) == False)
        assert_raises(TypeError, is_valid_linkage, Z, throw=True)

    def test_is_valid_linkage_empty(self):
        # Tests is_valid_linkage(Z) with empty linkage.
        Z = np.zeros((0, 4), dtype=np.double)
        assert_(is_valid_linkage(Z) == False)
        assert_raises(ValueError, is_valid_linkage, Z, throw=True)

    def test_is_valid_linkage_4_and_up(self):
        # Tests is_valid_linkage(Z) on linkage on observation sets between
        # sizes 4 and 15 (step size 3).
        for i in xrange(4, 15, 3):
            y = np.random.rand(i*(i-1)//2)
            Z = linkage(y)
            assert_(is_valid_linkage(Z) == True)

    def test_is_valid_linkage_4_and_up_neg_index_left(self):
        # Tests is_valid_linkage(Z) on linkage on observation sets between
        # sizes 4 and 15 (step size 3) with negative indices (left).
        for i in xrange(4, 15, 3):
            y = np.random.rand(i*(i-1)//2)
            Z = linkage(y)
            Z[i//2,0] = -2
            assert_(is_valid_linkage(Z) == False)
            assert_raises(ValueError, is_valid_linkage, Z, throw=True)

    def test_is_valid_linkage_4_and_up_neg_index_right(self):
        # Tests is_valid_linkage(Z) on linkage on observation sets between
        # sizes 4 and 15 (step size 3) with negative indices (right).
        for i in xrange(4, 15, 3):
            y = np.random.rand(i*(i-1)//2)
            Z = linkage(y)
            Z[i//2,1] = -2
            assert_(is_valid_linkage(Z) == False)
            assert_raises(ValueError, is_valid_linkage, Z, throw=True)

    def test_is_valid_linkage_4_and_up_neg_dist(self):
        # Tests is_valid_linkage(Z) on linkage on observation sets between
        # sizes 4 and 15 (step size 3) with negative distances.
        for i in xrange(4, 15, 3):
            y = np.random.rand(i*(i-1)//2)
            Z = linkage(y)
            Z[i//2,2] = -0.5
            assert_(is_valid_linkage(Z) == False)
            assert_raises(ValueError, is_valid_linkage, Z, throw=True)

    def test_is_valid_linkage_4_and_up_neg_counts(self):
        # Tests is_valid_linkage(Z) on linkage on observation sets between
        # sizes 4 and 15 (step size 3) with negative counts.
        for i in xrange(4, 15, 3):
            y = np.random.rand(i*(i-1)//2)
            Z = linkage(y)
            Z[i//2,3] = -2
            assert_(is_valid_linkage(Z) == False)
            assert_raises(ValueError, is_valid_linkage, Z, throw=True)


class TestIsValidInconsistent(object):
    def test_is_valid_im_int_type(self):
        # Tests is_valid_im(R) with integer type.
        R = np.asarray([[0, 1, 3.0, 2],
                        [3, 2, 4.0, 3]], dtype=np.int)
        assert_(is_valid_im(R) == False)
        assert_raises(TypeError, is_valid_im, R, throw=True)

    def test_is_valid_im_various_size(self):
        for nrow, ncol, valid in [(2, 5, False), (2, 3, False),
                                  (1, 4, True), (2, 4, True)]:
            yield self.check_is_valid_im_various_size, nrow, ncol, valid

    def check_is_valid_im_various_size(self, nrow, ncol, valid):
        # Tests is_valid_im(R) with linkage matrics of various sizes
        R = np.asarray([[0, 1, 3.0, 2, 5],
                        [3, 2, 4.0, 3, 3]], dtype=np.double)
        R = R[:nrow, :ncol]
        assert_(is_valid_im(R) == valid)
        if not valid:
            assert_raises(ValueError, is_valid_im, R, throw=True)

    def test_is_valid_im_empty(self):
        # Tests is_valid_im(R) with empty inconsistency matrix.
        R = np.zeros((0, 4), dtype=np.double)
        assert_(is_valid_im(R) == False)
        assert_raises(ValueError, is_valid_im, R, throw=True)

    def test_is_valid_im_4_and_up(self):
        # Tests is_valid_im(R) on im on observation sets between sizes 4 and 15
        # (step size 3).
        for i in xrange(4, 15, 3):
            y = np.random.rand(i*(i-1)//2)
            Z = linkage(y)
            R = inconsistent(Z)
            assert_(is_valid_im(R) == True)

    def test_is_valid_im_4_and_up_neg_index_left(self):
        # Tests is_valid_im(R) on im on observation sets between sizes 4 and 15
        # (step size 3) with negative link height means.
        for i in xrange(4, 15, 3):
            y = np.random.rand(i*(i-1)//2)
            Z = linkage(y)
            R = inconsistent(Z)
            R[i//2,0] = -2.0
            assert_(is_valid_im(R) == False)
            assert_raises(ValueError, is_valid_im, R, throw=True)

    def test_is_valid_im_4_and_up_neg_index_right(self):
        # Tests is_valid_im(R) on im on observation sets between sizes 4 and 15
        # (step size 3) with negative link height standard deviations.
        for i in xrange(4, 15, 3):
            y = np.random.rand(i*(i-1)//2)
            Z = linkage(y)
            R = inconsistent(Z)
            R[i//2,1] = -2.0
            assert_(is_valid_im(R) == False)
            assert_raises(ValueError, is_valid_im, R, throw=True)

    def test_is_valid_im_4_and_up_neg_dist(self):
        # Tests is_valid_im(R) on im on observation sets between sizes 4 and 15
        # (step size 3) with negative link counts.
        for i in xrange(4, 15, 3):
            y = np.random.rand(i*(i-1)//2)
            Z = linkage(y)
            R = inconsistent(Z)
            R[i//2,2] = -0.5
            assert_(is_valid_im(R) == False)
            assert_raises(ValueError, is_valid_im, R, throw=True)


class TestNumObsLinkage(TestCase):
    def test_num_obs_linkage_empty(self):
        # Tests num_obs_linkage(Z) with empty linkage.
        Z = np.zeros((0, 4), dtype=np.double)
        self.assertRaises(ValueError, num_obs_linkage, Z)

    def test_num_obs_linkage_1x4(self):
        # Tests num_obs_linkage(Z) on linkage over 2 observations.
        Z = np.asarray([[0, 1, 3.0, 2]], dtype=np.double)
        self.assertTrue(num_obs_linkage(Z) == 2)

    def test_num_obs_linkage_2x4(self):
        # Tests num_obs_linkage(Z) on linkage over 3 observations.
        Z = np.asarray([[0, 1, 3.0, 2],
                        [3, 2, 4.0, 3]], dtype=np.double)
        self.assertTrue(num_obs_linkage(Z) == 3)

    def test_num_obs_linkage_4_and_up(self):
        # Tests num_obs_linkage(Z) on linkage on observation sets between sizes
        # 4 and 15 (step size 3).
        for i in xrange(4, 15, 3):
            y = np.random.rand(i*(i-1)//2)
            Z = linkage(y)
            self.assertTrue(num_obs_linkage(Z) == i)


class TestLeavesList(object):
    def test_leaves_list_1x4(self):
        # Tests leaves_list(Z) on a 1x4 linkage.
        Z = np.asarray([[0, 1, 3.0, 2]], dtype=np.double)
        to_tree(Z)
        assert_equal(leaves_list(Z), [0, 1])

    def test_leaves_list_2x4(self):
        # Tests leaves_list(Z) on a 2x4 linkage.
        Z = np.asarray([[0, 1, 3.0, 2],
                        [3, 2, 4.0, 3]], dtype=np.double)
        to_tree(Z)
        assert_equal(leaves_list(Z), [0, 1, 2])

    def test_leaves_list_Q(self):
        for method in ['single', 'complete', 'average', 'weighted', 'centroid',
                       'median', 'ward']:
            yield self.check_leaves_list_Q, method

    def check_leaves_list_Q(self, method):
        # Tests leaves_list(Z) on the Q data set
        X = hierarchy_test_data.Q_X
        Z = linkage(X, method)
        node = to_tree(Z)
        assert_equal(node.pre_order(), leaves_list(Z))

    def test_Q_subtree_pre_order(self):
        # Tests that pre_order() works when called on sub-trees.
        X = hierarchy_test_data.Q_X
        Z = linkage(X, 'single')
        node = to_tree(Z)
        assert_equal(node.pre_order(), (node.get_left().pre_order()
                                        + node.get_right().pre_order()))


class TestCorrespond(TestCase):
    def test_correspond_empty(self):
        # Tests correspond(Z, y) with empty linkage and condensed distance matrix.
        y = np.zeros((0,))
        Z = np.zeros((0,4))
        self.assertRaises(ValueError, correspond, Z, y)

    def test_correspond_2_and_up(self):
        # Tests correspond(Z, y) on linkage and CDMs over observation sets of
        # different sizes.
        for i in xrange(2, 4):
            y = np.random.rand(i*(i-1)//2)
            Z = linkage(y)
            self.assertTrue(correspond(Z, y))
        for i in xrange(4, 15, 3):
            y = np.random.rand(i*(i-1)//2)
            Z = linkage(y)
            self.assertTrue(correspond(Z, y))

    def test_correspond_4_and_up(self):
        # Tests correspond(Z, y) on linkage and CDMs over observation sets of
        # different sizes. Correspondance should be false.
        for (i, j) in (list(zip(list(range(2, 4)), list(range(3, 5)))) +
                       list(zip(list(range(3, 5)), list(range(2, 4))))):
            y = np.random.rand(i*(i-1)//2)
            y2 = np.random.rand(j*(j-1)//2)
            Z = linkage(y)
            Z2 = linkage(y2)
            self.assertTrue(correspond(Z, y2) == False)
            self.assertTrue(correspond(Z2, y) == False)

    def test_correspond_4_and_up_2(self):
        # Tests correspond(Z, y) on linkage and CDMs over observation sets of
        # different sizes. Correspondance should be false.
        for (i, j) in (list(zip(list(range(2, 7)), list(range(16, 21)))) +
                       list(zip(list(range(2, 7)), list(range(16, 21))))):
            y = np.random.rand(i*(i-1)//2)
            y2 = np.random.rand(j*(j-1)//2)
            Z = linkage(y)
            Z2 = linkage(y2)
            self.assertTrue(correspond(Z, y2) == False)
            self.assertTrue(correspond(Z2, y) == False)

    def test_num_obs_linkage_multi_matrix(self):
        # Tests num_obs_linkage with observation matrices of multiple sizes.
        for n in xrange(2, 10):
            X = np.random.rand(n, 4)
            Y = pdist(X)
            Z = linkage(Y)
            self.assertTrue(num_obs_linkage(Z) == n)


class TestIsMonotonic(TestCase):
    def test_is_monotonic_empty(self):
        # Tests is_monotonic(Z) on an empty linkage.
        Z = np.zeros((0, 4))
        self.assertRaises(ValueError, is_monotonic, Z)

    def test_is_monotonic_1x4(self):
        # Tests is_monotonic(Z) on 1x4 linkage. Expecting True.
        Z = np.asarray([[0, 1, 0.3, 2]], dtype=np.double)
        self.assertTrue(is_monotonic(Z) == True)

    def test_is_monotonic_2x4_T(self):
        # Tests is_monotonic(Z) on 2x4 linkage. Expecting True.
        Z = np.asarray([[0, 1, 0.3, 2],
                        [2, 3, 0.4, 3]], dtype=np.double)
        self.assertTrue(is_monotonic(Z) == True)

    def test_is_monotonic_2x4_F(self):
        # Tests is_monotonic(Z) on 2x4 linkage. Expecting False.
        Z = np.asarray([[0, 1, 0.4, 2],
                        [2, 3, 0.3, 3]], dtype=np.double)
        self.assertTrue(is_monotonic(Z) == False)

    def test_is_monotonic_3x4_T(self):
        # Tests is_monotonic(Z) on 3x4 linkage. Expecting True.
        Z = np.asarray([[0, 1, 0.3, 2],
                        [2, 3, 0.4, 2],
                        [4, 5, 0.6, 4]], dtype=np.double)
        self.assertTrue(is_monotonic(Z) == True)

    def test_is_monotonic_3x4_F1(self):
        # Tests is_monotonic(Z) on 3x4 linkage (case 1). Expecting False.
        Z = np.asarray([[0, 1, 0.3, 2],
                        [2, 3, 0.2, 2],
                        [4, 5, 0.6, 4]], dtype=np.double)
        self.assertTrue(is_monotonic(Z) == False)

    def test_is_monotonic_3x4_F2(self):
        # Tests is_monotonic(Z) on 3x4 linkage (case 2). Expecting False.
        Z = np.asarray([[0, 1, 0.8, 2],
                        [2, 3, 0.4, 2],
                        [4, 5, 0.6, 4]], dtype=np.double)
        self.assertTrue(is_monotonic(Z) == False)

    def test_is_monotonic_3x4_F3(self):
        # Tests is_monotonic(Z) on 3x4 linkage (case 3). Expecting False
        Z = np.asarray([[0, 1, 0.3, 2],
                        [2, 3, 0.4, 2],
                        [4, 5, 0.2, 4]], dtype=np.double)
        self.assertTrue(is_monotonic(Z) == False)

    def test_is_monotonic_tdist_linkage1(self):
        # Tests is_monotonic(Z) on clustering generated by single linkage on
        # tdist data set. Expecting True.
        Z = linkage(hierarchy_test_data.ytdist, 'single')
        self.assertTrue(is_monotonic(Z) == True)

    def test_is_monotonic_tdist_linkage2(self):
        # Tests is_monotonic(Z) on clustering generated by single linkage on
        # tdist data set. Perturbing. Expecting False.
        Z = linkage(hierarchy_test_data.ytdist, 'single')
        Z[2,2] = 0.0
        self.assertTrue(is_monotonic(Z) == False)

    def test_is_monotonic_Q_linkage(self):
        # Tests is_monotonic(Z) on clustering generated by single linkage on
        # Q data set. Expecting True.
        X = hierarchy_test_data.Q_X
        Z = linkage(X, 'single')
        self.assertTrue(is_monotonic(Z) == True)


class TestMaxDists(object):
    def test_maxdists_empty_linkage(self):
        # Tests maxdists(Z) on empty linkage. Expecting exception.
        Z = np.zeros((0, 4), dtype=np.double)
        assert_raises(ValueError, maxdists, Z)

    def test_maxdists_one_cluster_linkage(self):
        # Tests maxdists(Z) on linkage with one cluster.
        Z = np.asarray([[0, 1, 0.3, 4]], dtype=np.double)
        MD = maxdists(Z)
        expectedMD = calculate_maximum_distances(Z)
        assert_allclose(MD, expectedMD, atol=1e-15)

    def test_maxdists_Q_linkage(self):
        for method in ['single', 'complete', 'ward', 'centroid', 'median']:
            yield self.check_maxdists_Q_linkage, method

    def check_maxdists_Q_linkage(self, method):
        # Tests maxdists(Z) on the Q data set
        X = hierarchy_test_data.Q_X
        Z = linkage(X, method)
        MD = maxdists(Z)
        expectedMD = calculate_maximum_distances(Z)
        assert_allclose(MD, expectedMD, atol=1e-15)


class TestMaxInconsts(object):
    def test_maxinconsts_empty_linkage(self):
        # Tests maxinconsts(Z, R) on empty linkage. Expecting exception.
        Z = np.zeros((0, 4), dtype=np.double)
        R = np.zeros((0, 4), dtype=np.double)
        assert_raises(ValueError, maxinconsts, Z, R)

    def test_maxinconsts_difrow_linkage(self):
        # Tests maxinconsts(Z, R) on linkage and inconsistency matrices with
        # different numbers of clusters. Expecting exception.
        Z = np.asarray([[0, 1, 0.3, 4]], dtype=np.double)
        R = np.random.rand(2, 4)
        assert_raises(ValueError, maxinconsts, Z, R)

    def test_maxinconsts_one_cluster_linkage(self):
        # Tests maxinconsts(Z, R) on linkage with one cluster.
        Z = np.asarray([[0, 1, 0.3, 4]], dtype=np.double)
        R = np.asarray([[0, 0, 0, 0.3]], dtype=np.double)
        MD = maxinconsts(Z, R)
        expectedMD = calculate_maximum_inconsistencies(Z, R)
        assert_allclose(MD, expectedMD, atol=1e-15)

    def test_maxinconsts_Q_linkage(self):
        for method in ['single', 'complete', 'ward', 'centroid', 'median']:
            yield self.check_maxinconsts_Q_linkage, method

    def check_maxinconsts_Q_linkage(self, method):
        # Tests maxinconsts(Z, R) on the Q data set
        X = hierarchy_test_data.Q_X
        Z = linkage(X, method)
        R = inconsistent(Z)
        MD = maxinconsts(Z, R)
        expectedMD = calculate_maximum_inconsistencies(Z, R)
        assert_allclose(MD, expectedMD, atol=1e-15)


class TestMaxRStat(object):
    def test_maxRstat_invalid_index(self):
        for i in [3.3, -1, 4]:
            yield self.check_maxRstat_invalid_index, i

    def check_maxRstat_invalid_index(self, i):
        # Tests maxRstat(Z, R, i). Expecting exception.
        Z = np.asarray([[0, 1, 0.3, 4]], dtype=np.double)
        R = np.asarray([[0, 0, 0, 0.3]], dtype=np.double)
        if isinstance(i, int):
            assert_raises(ValueError, maxRstat, Z, R, i)
        else:
            assert_raises(TypeError, maxRstat, Z, R, i)

    def test_maxRstat_empty_linkage(self):
        for i in range(4):
            yield self.check_maxRstat_empty_linkage, i

    def check_maxRstat_empty_linkage(self, i):
        # Tests maxRstat(Z, R, i) on empty linkage. Expecting exception.
        Z = np.zeros((0, 4), dtype=np.double)
        R = np.zeros((0, 4), dtype=np.double)
        assert_raises(ValueError, maxRstat, Z, R, i)

    def test_maxRstat_difrow_linkage(self):
        for i in range(4):
            yield self.check_maxRstat_difrow_linkage, i

    def check_maxRstat_difrow_linkage(self, i):
        # Tests maxRstat(Z, R, i) on linkage and inconsistency matrices with
        # different numbers of clusters. Expecting exception.
        Z = np.asarray([[0, 1, 0.3, 4]], dtype=np.double)
        R = np.random.rand(2, 4)
        assert_raises(ValueError, maxRstat, Z, R, i)

    def test_maxRstat_one_cluster_linkage(self):
        for i in range(4):
            yield self.check_maxRstat_one_cluster_linkage, i

    def check_maxRstat_one_cluster_linkage(self, i):
        # Tests maxRstat(Z, R, i) on linkage with one cluster.
        Z = np.asarray([[0, 1, 0.3, 4]], dtype=np.double)
        R = np.asarray([[0, 0, 0, 0.3]], dtype=np.double)
        MD = maxRstat(Z, R, 1)
        expectedMD = calculate_maximum_inconsistencies(Z, R, 1)
        assert_allclose(MD, expectedMD, atol=1e-15)

    def test_maxRstat_Q_linkage(self):
        for method in ['single', 'complete', 'ward', 'centroid', 'median']:
            for i in range(4):
                yield self.check_maxRstat_Q_linkage, method, i

    def check_maxRstat_Q_linkage(self, method, i):
        # Tests maxRstat(Z, R, i) on the Q data set
        X = hierarchy_test_data.Q_X
        Z = linkage(X, method)
        R = inconsistent(Z)
        MD = maxRstat(Z, R, 1)
        expectedMD = calculate_maximum_inconsistencies(Z, R, 1)
        assert_allclose(MD, expectedMD, atol=1e-15)


class TestDendrogram(object):
    def test_dendrogram_single_linkage_tdist(self):
        # Tests dendrogram calculation on single linkage of the tdist data set.
        Z = linkage(hierarchy_test_data.ytdist, 'single')
        R = dendrogram(Z, no_plot=True)
        leaves = R["leaves"]
        assert_equal(leaves, [2, 5, 1, 0, 3, 4])

    def test_valid_orientation(self):
        Z = linkage(hierarchy_test_data.ytdist, 'single')
        assert_raises(ValueError, dendrogram, Z, orientation="foo")

    @dec.skipif(not have_matplotlib)
    def test_dendrogram_plot(self):
        for orientation in ['top', 'bottom', 'left', 'right']:
            yield self.check_dendrogram_plot, orientation

    def check_dendrogram_plot(self, orientation):
        # Tests dendrogram plotting.
        Z = linkage(hierarchy_test_data.ytdist, 'single')
        expected = {'color_list': ['g', 'b', 'b', 'b', 'b'],
                    'dcoord': [[0.0, 138.0, 138.0, 0.0],
                               [0.0, 219.0, 219.0, 0.0],
                               [0.0, 255.0, 255.0, 219.0],
                               [0.0, 268.0, 268.0, 255.0],
                               [138.0, 295.0, 295.0, 268.0]],
                    'icoord': [[5.0, 5.0, 15.0, 15.0],
                               [45.0, 45.0, 55.0, 55.0],
                               [35.0, 35.0, 50.0, 50.0],
                               [25.0, 25.0, 42.5, 42.5],
                               [10.0, 10.0, 33.75, 33.75]],
                    'ivl': ['2', '5', '1', '0', '3', '4'],
                    'leaves': [2, 5, 1, 0, 3, 4]}

        fig = plt.figure()
        ax = fig.add_subplot(111)

        # test that dendrogram accepts ax keyword
        R1 = dendrogram(Z, ax=ax, orientation=orientation)
        plt.close()
        assert_equal(R1, expected)

        # test plotting to gca (will import pylab)
        R2 = dendrogram(Z, orientation=orientation)
        plt.close()
        assert_equal(R2, expected)

    @dec.skipif(not have_matplotlib)
    def test_dendrogram_truncate_mode(self):
        Z = linkage(hierarchy_test_data.ytdist, 'single')

        R = dendrogram(Z, 2, 'lastp', show_contracted=True)
        plt.close()
        assert_equal(R, {'color_list': ['b'],
                         'dcoord': [[0.0, 295.0, 295.0, 0.0]],
                         'icoord': [[5.0, 5.0, 15.0, 15.0]],
                         'ivl': ['(2)', '(4)'],
                         'leaves': [6, 9]})

        R = dendrogram(Z, 2, 'mtica', show_contracted=True)
        plt.close()
        assert_equal(R, {'color_list': ['g', 'b', 'b', 'b'],
                         'dcoord': [[0.0, 138.0, 138.0, 0.0],
                                    [0.0, 255.0, 255.0, 0.0],
                                    [0.0, 268.0, 268.0, 255.0],
                                    [138.0, 295.0, 295.0, 268.0]],
                         'icoord': [[5.0, 5.0, 15.0, 15.0],
                                    [35.0, 35.0, 45.0, 45.0],
                                    [25.0, 25.0, 40.0, 40.0],
                                    [10.0, 10.0, 32.5, 32.5]],
                         'ivl': ['2', '5', '1', '0', '(2)'],
                         'leaves': [2, 5, 1, 0, 7]})

    def test_dendrogram_colors(self):
        # Tests dendrogram plots with alternate colors
        Z = linkage(hierarchy_test_data.ytdist, 'single')

        set_link_color_palette(['c', 'm', 'y', 'k'])
        R = dendrogram(Z, no_plot=True,
                       above_threshold_color='g', color_threshold=250)
        set_link_color_palette(['g', 'r', 'c', 'm', 'y', 'k'])

        color_list = R['color_list']
        assert_equal(color_list, ['c', 'm', 'g', 'g', 'g'])


def calculate_maximum_distances(Z):
    # Used for testing correctness of maxdists.
    n = Z.shape[0] + 1
    B = np.zeros((n-1,))
    q = np.zeros((3,))
    for i in xrange(0, n - 1):
        q[:] = 0.0
        left = Z[i, 0]
        right = Z[i, 1]
        if left >= n:
            q[0] = B[int(left) - n]
        if right >= n:
            q[1] = B[int(right) - n]
        q[2] = Z[i, 2]
        B[i] = q.max()
    return B


def calculate_maximum_inconsistencies(Z, R, k=3):
    # Used for testing correctness of maxinconsts.
    n = Z.shape[0] + 1
    B = np.zeros((n-1,))
    q = np.zeros((3,))
    for i in xrange(0, n - 1):
        q[:] = 0.0
        left = Z[i, 0]
        right = Z[i, 1]
        if left >= n:
            q[0] = B[int(left) - n]
        if right >= n:
            q[1] = B[int(right) - n]
        q[2] = R[i, k]
        B[i] = q.max()
    return B


def test_euclidean_linkage_value_error():
    for method in scipy.cluster.hierarchy._cpy_euclid_methods:
        assert_raises(ValueError,
                linkage, [[1, 1], [1, 1]], method=method, metric='cityblock')


def test_2x2_linkage():
    Z1 = linkage([1], method='single', metric='euclidean')
    Z2 = linkage([[0, 1], [0, 0]], method='single', metric='euclidean')
    assert_allclose(Z1, Z2)


if __name__ == "__main__":
    run_module_suite()

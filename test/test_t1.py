# This code is part of Qiskit.
#
# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
"""
Test T1 experiment
"""

from qiskit.test import QiskitTestCase
from qiskit_experiments import ExperimentData
from qiskit_experiments.composite import ParallelExperiment
from qiskit_experiments.characterization import T1, T1Analysis
from qiskit_experiments.test.t1_backend import T1Backend


class TestT1(QiskitTestCase):
    """
    Test measurement of T1
    """

    def test_t1_end2end(self):
        """
        Test T1 experiment using a simulator.
        """

        dt_factor = 2e-7

        t1 = 25e-6
        backend = T1Backend(
            [t1 / dt_factor],
            initial_prob1=[0.02],
            readout0to1=[0.02],
            readout1to0=[0.02],
            dt_factor=dt_factor,
        )

        delays = list(
            range(
                int(1e-6 / dt_factor),
                int(40e-6 / dt_factor),
                int(3e-6 / dt_factor),
            )
        )

        exp = T1(0, delays, unit="dt")
        exp.set_analysis_options(amplitude_guess=1, t1_guess=t1 / dt_factor, offset_guess=0)
        res = exp.run(backend, shots=10000).analysis_result(0)

        self.assertEqual(res["quality"], "computer_good")
        self.assertAlmostEqual(res["value"], t1, delta=3)

    def test_t1_parallel(self):
        """
        Test parallel experiments of T1 using a simulator.
        """

        t1 = [25, 15]
        delays = list(range(1, 40, 3))

        exp0 = T1(0, delays)
        exp2 = T1(2, delays)
        par_exp = ParallelExperiment([exp0, exp2])
        res = par_exp.run(T1Backend([t1[0], None, t1[1]]))

        for i in range(2):
            sub_res = res.component_experiment_data(i).analysis_result(0)
            self.assertEqual(sub_res["quality"], "computer_good")
            self.assertAlmostEqual(sub_res["value"], t1[i], delta=3)

    def test_t1_parallel_different_analysis_options(self):
        """
        Test parallel experiments of T1 using a simulator, for the case where
        the sub-experiments have different analysis options
        """

        t1 = 25
        delays = list(range(1, 40, 3))

        exp0 = T1(0, delays)
        exp0.set_analysis_options(t1_bounds=[10, 30])
        exp1 = T1(1, delays)
        exp1.set_analysis_options(t1_bounds=[100, 200])

        par_exp = ParallelExperiment([exp0, exp1])
        res = par_exp.run(T1Backend([t1, t1]))

        sub_res = []
        for i in range(2):
            sub_res.append(res.component_experiment_data(i).analysis_result(0))

        self.assertEqual(sub_res[0]["quality"], "computer_good")
        self.assertAlmostEqual(sub_res[0]["value"], t1, delta=3)
        self.assertFalse(sub_res[1]["success"])

    def test_t1_analysis(self):
        """
        Test T1Analysis
        """

        data = ExperimentData(None)
        numbers = [750, 1800, 2750, 3550, 4250, 4850, 5450, 5900, 6400, 6800, 7000, 7350, 7700]

        for i, count0 in enumerate(numbers):
            data._data.append(
                {
                    "counts": {"0": count0, "1": 10000 - count0},
                    "metadata": {
                        "xval": 3 * i + 1,
                        "experiment_type": "T1",
                        "qubit": 0,
                        "unit": "ns",
                        "dt_factor_in_sec": None,
                    },
                }
            )

        res = T1Analysis()._run_analysis(data)[0]
        self.assertEqual(res[0]["quality"], "computer_good")
        self.assertAlmostEqual(res[0]["value"], 25e-9, delta=3)

    def test_t1_metadata(self):
        """
        Test the circuits metadata
        """

        delays = list(range(1, 40, 3))
        exp = T1(0, delays, unit="ms")
        circs = exp.circuits()

        self.assertEqual(len(circs), len(delays))

        for delay, circ in zip(delays, circs):
            self.assertEqual(
                circ.metadata,
                {
                    "experiment_type": "T1",
                    "qubit": 0,
                    "xval": delay,
                    "unit": "ms",
                },
            )

    def test_t1_low_quality(self):
        """
        A test where the fit's quality will be low
        """

        data = ExperimentData(None)

        for i in range(10):
            data._data.append(
                {
                    "counts": {"0": 10, "1": 10},
                    "metadata": {
                        "xval": i,
                        "experiment_type": "T1",
                        "qubit": 0,
                        "unit": "ns",
                        "dt_factor_in_sec": None,
                    },
                }
            )

        res = T1Analysis()._run_analysis(data)[0]
        self.assertEqual(res[0]["quality"], "computer_bad")

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
===============================================================================================
Stark Experiments (:mod:`qiskit_experiments.library.stark`)
===============================================================================================

.. currentmodule:: qiskit_experiments.library.stark

Experiments
===========
.. autosummary::
    :toctree: ../stubs/
    :template: autosummary/experiment.rst

    StarkRamseyXY
    StarkRamseyFast
    StarkP1Spectroscopy


Analysis
========
.. autosummary::
    :toctree: ../stubs/
    :template: autosummary/analysis.rst

    StarkRamseyFastAnalysis
    StarkP1SpectroscopyAnalysis

"""

from .p1_spectroscopy import StarkP1Spectroscopy
from .p1_spectroscopy_analysis import StarkP1SpectroscopyAnalysis
from .ramsey_xy import StarkRamseyXY
from .ramsey_fast import StarkRamseyFast
from .ramsey_fast_analysis import StarkRamseyFastAnalysis

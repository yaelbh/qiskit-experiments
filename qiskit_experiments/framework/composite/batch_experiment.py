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
Batch Experiment class.
"""

from typing import List, Optional
from collections import OrderedDict

from qiskit import QuantumCircuit
from qiskit.providers.backend import Backend
from qiskit_experiments.exceptions import QiskitError
from .composite_experiment import CompositeExperiment, BaseExperiment


class BatchExperiment(CompositeExperiment):
    """Combine multiple experiments into a batch experiment.

    Batch experiments combine individual experiments on any subset of qubits
    into a single composite experiment which appends all the circuits from
    each component experiment into a single batch of circuits to be executed
    as one experiment job.

    Analysis of batch experiments is performed using the
    :class:`~qiskit_experiments.framework.CompositeAnalysis` class which handles
    sorting the composite experiment circuit data into individual child
    :class:`ExperimentData` containers for each component experiment which are
    then analyzed using the corresponding analysis class for that component
    experiment.

    See :class:`~qiskit_experiments.framework.CompositeAnalysis`
    documentation for additional information.
    """

    def __init__(self, experiments: List[BaseExperiment], backend: Optional[Backend] = None):
        """Initialize a batch experiment.

        Args:
            experiments: a list of experiments.
            backend: Optional, the backend to run the experiment on.
        """

        # Generate qubit map
        self._qubit_map = OrderedDict()
        logical_qubit = 0
        for expr in experiments:
            for physical_qubit in expr.physical_qubits:
                if physical_qubit not in self._qubit_map:
                    self._qubit_map[physical_qubit] = logical_qubit
                    logical_qubit += 1
        qubits = tuple(self._qubit_map.keys())
        super().__init__(experiments, qubits, backend=backend)

    def circuits(self):
        batch_circuits = []

        # Generate data for combination
        for index, sub_exp in enumerate(self._experiments):
            for sub_circ in sub_exp._transpiled_circuits():
                circuit = QuantumCircuit(
                    self.num_qubits, sub_circ.num_clbits, name="batch_" + sub_circ.name
                )
                circuit.metadata = {
                    "experiment_type": self._type,
                    "composite_metadata": [sub_circ.metadata],
                    "composite_index": [index],
                }
                for inst, qargs, cargs in sub_circ.data:
                    try:
                        mapped_qargs = [
                            circuit.qubits[self._qubit_map[sub_circ.find_bit(i).index]]
                            for i in qargs
                        ]
                    except KeyError as ex:
                        # Instruction is outside physical qubits for the component
                        # experiment.
                        # This could legitimately happen if the subcircuit was
                        # explicitly scheduled during transpilation which would
                        # insert delays on all auxillary device qubits.
                        # We skip delay instructions to allow for this.
                        if inst.name == "delay":
                            continue
                        raise QiskitError(
                            "Invalid physical qubits for component experiment"
                        ) from ex
                    mapped_cargs = [circuit.clbits[sub_circ.find_bit(i).index] for i in cargs]
                    circuit._append(inst, mapped_qargs, mapped_cargs)
                batch_circuits.append(circuit)

        return batch_circuits

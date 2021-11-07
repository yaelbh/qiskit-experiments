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

"""Class to test composite experiments."""

from typing import Optional, List, Dict, Type, Any, Union, Tuple
import json
import copy
import uuid

from test.fake_backend import FakeBackend
from test.fake_experiment import FakeExperiment

from qiskit.circuit import QuantumCircuit
from qiskit.result import Result
from qiskit.test import QiskitTestCase
from qiskit.test.mock import FakeMelbourne

from qiskit_experiments.framework import (
    ParallelExperiment,
    Options,
    ExperimentData,
    BatchExperiment,
)
from qiskit_experiments.database_service import DatabaseServiceV1
from qiskit_experiments.database_service.device_component import DeviceComponent
from qiskit_experiments.test.utils import FakeJob

# pylint: disable=missing-raises-doc


class TestComposite(QiskitTestCase):
    """
    Test composite experiment behavior.
    """

    def test_parallel_options(self):
        """
        Test parallel experiments overriding sub-experiment run and transpile options.
        """
        # These options will all be overridden
        exp0 = FakeExperiment([0])
        exp0.set_transpile_options(optimization_level=1)
        exp2 = FakeExperiment([2])
        exp2.set_experiment_options(dummyoption="test")
        exp2.set_run_options(shots=2000)
        exp2.set_transpile_options(optimization_level=1)
        exp2.set_analysis_options(dummyoption="test")

        par_exp = ParallelExperiment([exp0, exp2])

        with self.assertWarnsRegex(
            Warning,
            "Sub-experiment run and transpile options"
            " are overridden by composite experiment options.",
        ):
            self.assertEqual(par_exp.experiment_options, Options())
            self.assertEqual(par_exp.run_options, Options(meas_level=2))
            self.assertEqual(par_exp.transpile_options, Options(optimization_level=0))
            self.assertEqual(par_exp.analysis_options, Options())

            par_exp.run(FakeBackend())


class DummyService(DatabaseServiceV1):
    """
    Extremely simple database for testing
    """

    def __init__(self):
        self.database = {}

    def create_experiment(
        self,
        experiment_type: str,
        backend_name: str,
        metadata: Optional[Dict] = None,
        experiment_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        job_ids: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None,
        json_encoder: Type[json.JSONEncoder] = json.JSONEncoder,
        **kwargs: Any,
    ) -> str:
        """Create a new experiment in the database.

        Args:
            experiment_type: Experiment type.
            backend_name: Name of the backend the experiment ran on.
            metadata: Experiment metadata.
            experiment_id: Experiment ID. It must be in the ``uuid4`` format.
                One will be generated if not supplied.
            parent_id: The experiment ID of the parent experiment.
                The parent experiment must exist, must be on the same backend as the child,
                and an experiment cannot be its own parent.
            job_ids: IDs of experiment jobs.
            tags: Tags to be associated with the experiment.
            notes: Freeform notes about the experiment.
            json_encoder: Custom JSON encoder to use to encode the experiment.
            kwargs: Additional keywords supported by the service provider.

        Returns:
            Experiment ID.
        """

        self.database[experiment_id] = {
            "experiment_type": experiment_type,
            "parent_id": parent_id,
            "backend_name": backend_name,
            "metadata": metadata,
            "job_ids": job_ids,
            "tags": tags,
            "notes": notes,
            "share_level": kwargs.get("share_level", None),
            "figure_names": kwargs.get("figure_names", None),
        }
        return experiment_id

    def update_experiment(
        self,
        experiment_id: str,
        metadata: Optional[Dict] = None,
        job_ids: Optional[List[str]] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Update an existing experiment.

        Args:
            experiment_id: Experiment ID.
            metadata: Experiment metadata.
            job_ids: IDs of experiment jobs.
            notes: Freeform notes about the experiment.
            tags: Tags to be associated with the experiment.
            kwargs: Additional keywords supported by the service provider.
        """
        raise Exception("not implemented")

    def experiment(
        self, experiment_id: str, json_decoder: Type[json.JSONDecoder] = json.JSONDecoder
    ) -> Dict:
        """Retrieve a previously stored experiment.

        Args:
            experiment_id: Experiment ID.
            json_decoder: Custom JSON decoder to use to decode the retrieved experiment.

        Returns:
            A dictionary containing the retrieved experiment data.
        """

        db_entry = copy.deepcopy(self.database[experiment_id])
        backend_name = db_entry.pop("backend_name")
        backend = FakeMelbourne()
        if backend_name == backend.name():
            db_entry["backend"] = backend
        db_entry["experiment_id"] = experiment_id

        return db_entry

    def experiments(
        self,
        limit: Optional[int] = 10,
        json_decoder: Type[json.JSONDecoder] = json.JSONDecoder,
        device_components: Optional[Union[str, DeviceComponent]] = None,
        experiment_type: Optional[str] = None,
        backend_name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        parent_id: Optional[str] = None,
        tags_operator: Optional[str] = "OR",
        **filters: Any,
    ) -> List[Dict]:
        raise Exception("not implemented")

    def delete_experiment(self, experiment_id: str) -> None:
        raise Exception("not implemented")

    def create_analysis_result(
        self,
        experiment_id: str,
        result_data: Dict,
        result_type: str,
        device_components: Optional[Union[str, DeviceComponent]] = None,
        tags: Optional[List[str]] = None,
        quality: Optional[str] = None,
        verified: bool = False,
        result_id: Optional[str] = None,
        json_encoder: Type[json.JSONEncoder] = json.JSONEncoder,
        **kwargs: Any,
    ) -> str:
        raise Exception("not implemented")

    def update_analysis_result(
        self,
        result_id: str,
        result_data: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        quality: Optional[str] = None,
        verified: bool = None,
        **kwargs: Any,
    ) -> None:
        raise Exception("not implemented")

    def analysis_result(
        self, result_id: str, json_decoder: Type[json.JSONDecoder] = json.JSONDecoder
    ) -> Dict:
        raise Exception("not implemented")

    def analysis_results(
        self,
        limit: Optional[int] = 10,
        json_decoder: Type[json.JSONDecoder] = json.JSONDecoder,
        device_components: Optional[Union[str, DeviceComponent]] = None,
        experiment_id: Optional[str] = None,
        result_type: Optional[str] = None,
        backend_name: Optional[str] = None,
        quality: Optional[str] = None,
        verified: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        tags_operator: Optional[str] = "OR",
        **filters: Any,
    ) -> List[Dict]:
        raise Exception("not implemented")

    def delete_analysis_result(self, result_id: str) -> None:
        raise Exception("not implemented")

    def create_figure(
        self, experiment_id: str, figure: Union[str, bytes], figure_name: Optional[str]
    ) -> Tuple[str, int]:
        raise Exception("not implemented")

    def update_figure(
        self, experiment_id: str, figure: Union[str, bytes], figure_name: str
    ) -> Tuple[str, int]:
        raise Exception("not implemented")

    def figure(
        self, experiment_id: str, figure_name: str, file_name: Optional[str] = None
    ) -> Union[int, bytes]:
        raise Exception("not implemented")

    def delete_figure(
        self,
        experiment_id: str,
        figure_name: str,
    ) -> None:
        raise Exception("not implemented")

    @property
    def preferences(self) -> Dict:
        raise Exception("not implemented")


class TestCompositeExperimentData(QiskitTestCase):
    """
    Test operations on objects of composite ExperimentData
    """

    def setUp(self):
        super().setUp()

        self.backend = FakeMelbourne()
        self.share_level = "hey"

        exp1 = FakeExperiment([0, 2])
        exp2 = FakeExperiment([1, 3])
        par_exp = ParallelExperiment([exp1, exp2])
        exp3 = FakeExperiment([0, 1, 2, 3])
        batch_exp = BatchExperiment([par_exp, exp3])

        self.rootdata = ExperimentData(batch_exp, backend=self.backend)

        self.rootdata.share_level = self.share_level

    def check_attributes(self, expdata):
        """
        Recursively traverse the tree to verify attributes
        """
        self.assertEqual(expdata.backend, self.backend)
        self.assertEqual(expdata.share_level, self.share_level)

        components = expdata.child_data()
        comp_ids = expdata.metadata.get("child_ids", [])
        for childdata, comp_id in zip(components, comp_ids):
            self.check_attributes(childdata)
            self.assertEqual(childdata.parent_id, expdata.experiment_id)
            self.assertEqual(childdata.experiment_id, comp_id)

    def check_if_equal(self, expdata1, expdata2, is_a_copy):
        """
        Recursively traverse the tree and check equality of expdata1 and expdata2
        """
        self.assertEqual(expdata1.backend.name(), expdata2.backend.name())
        self.assertEqual(expdata1.tags, expdata2.tags)
        self.assertEqual(expdata1.experiment_type, expdata2.experiment_type)
        self.assertEqual(expdata1.share_level, expdata2.share_level)

        metadata1 = copy.copy(expdata1.metadata)
        metadata2 = copy.copy(expdata2.metadata)
        if is_a_copy:
            comp_ids1 = metadata1.pop("child_ids", [])
            comp_ids2 = metadata2.pop("child_ids", [])
            for id1 in comp_ids1:
                self.assertNotIn(id1, comp_ids2)
            for id2 in comp_ids2:
                self.assertNotIn(id2, comp_ids1)
            if expdata1.parent_id is None:
                self.assertEqual(expdata2.parent_id, None)
            else:
                self.assertNotEqual(expdata1.parent_id, expdata2.parent_id)
        else:
            self.assertEqual(expdata1.parent_id, expdata2.parent_id)
        self.assertDictEqual(metadata1, metadata2, msg="metadata not equal")

        if isinstance(expdata1, ExperimentData):
            for childdata1, childdata2 in zip(expdata1.child_data(), expdata2.child_data()):
                self.check_if_equal(childdata1, childdata2, is_a_copy)

    def test_composite_experiment_data_attributes(self):
        """
        Verify correct attributes of parents and children
        """
        self.check_attributes(self.rootdata)
        self.assertEqual(self.rootdata.parent_id, None)

    def test_composite_save_load(self):
        """
        Verify that saving and loading restores the original composite experiment data object
        """

        self.rootdata.service = DummyService()
        self.rootdata.save()
        loaded_data = ExperimentData.load(self.rootdata.experiment_id, self.rootdata.service)
        self.check_if_equal(loaded_data, self.rootdata, is_a_copy=False)

    def test_composite_save_metadata(self):
        """
        Verify that saving metadata and loading restores the original composite experiment data object
        """
        self.rootdata.service = DummyService()
        self.rootdata.save_metadata()
        loaded_data = ExperimentData.load(self.rootdata.experiment_id, self.rootdata.service)

        self.check_if_equal(loaded_data, self.rootdata, is_a_copy=False)

    def test_composite_copy(self):
        """
        Test composite ExperimentData.copy
        """
        new_instance = self.rootdata.copy()
        self.check_if_equal(new_instance, self.rootdata, is_a_copy=True)
        self.check_attributes(new_instance)

    def test_analysis_replace_results_true(self):
        """
        Test replace results when analyzing composite experiment data
        """
        exp1 = FakeExperiment([0, 2])
        exp2 = FakeExperiment([1, 3])
        par_exp = ParallelExperiment([exp1, exp2])
        data1 = par_exp.run(FakeBackend()).block_for_results()

        # Additional data not part of composite experiment
        exp3 = FakeExperiment([0, 1])
        extra_data = exp3.run(FakeBackend())
        data1.add_child_data(extra_data)

        # Replace results
        data2 = par_exp.run_analysis(data1, replace_results=True)
        self.assertEqual(data1, data2)
        self.assertEqual(len(data1.child_data()), len(data2.child_data()))
        for sub1, sub2 in zip(data1.child_data(), data2.child_data()):
            self.assertEqual(sub1, sub2)

    def test_analysis_replace_results_false(self):
        """
        Test replace_results of composite experiment data
        """
        exp1 = FakeExperiment([0, 2])
        exp2 = FakeExperiment([1, 3])
        par_exp = BatchExperiment([exp1, exp2])
        data1 = par_exp.run(FakeBackend()).block_for_results()

        # Additional data not part of composite experiment
        exp3 = FakeExperiment([0, 1])
        extra_data = exp3.run(FakeBackend())
        data1.add_child_data(extra_data)

        # Replace results
        data2 = par_exp.run_analysis(data1, replace_results=False)
        self.assertNotEqual(data1.experiment_id, data2.experiment_id)
        self.assertEqual(len(data1.child_data()), len(data2.child_data()))
        for sub1, sub2 in zip(data1.child_data(), data2.child_data()):
            self.assertNotEqual(sub1.experiment_id, sub2.experiment_id)

    def test_parallel_subexp_data(self):
        """
        Verify that sub-experiment data of a parallel experiment is
        correctly marginalized
        """

        class Backend(FakeBackend):
            def run(self, run_input, **options):
                counts = [
                    {
                        "0000": 1,
                        "0010": 6,
                        "0011": 3,
                        "0100": 4,
                        "0101": 2,
                        "0110": 1,
                        "0111": 3,
                        "1000": 5,
                        "1001": 3,
                        "1010": 4,
                        "1100": 4,
                        "1101": 3,
                        "1110": 8,
                        "1111": 5,
                    },
                    {
                        "0001": 3,
                        "0010": 4,
                        "0011": 5,
                        "0100": 2,
                        "0101": 1,
                        "0111": 7,
                        "1000": 3,
                        "1001": 2,
                        "1010": 1,
                        "1011": 1,
                        "1100": 7,
                        "1101": 8,
                        "1110": 2,
                    },
                    {
                        "0000": 1,
                        "0001": 1,
                        "0010": 8,
                        "0011": 7,
                        "0100": 2,
                        "0101": 2,
                        "0110": 2,
                        "0111": 1,
                        "1000": 6,
                        "1010": 4,
                        "1011": 4,
                        "1100": 5,
                        "1101": 2,
                        "1110": 2,
                        "1111": 5,
                    },
                    {
                        "0000": 4,
                        "0001": 5,
                        "0101": 4,
                        "0110": 8,
                        "0111": 2,
                        "1001": 6,
                        "1010": 8,
                        "1011": 8,
                        "1101": 1,
                        "1110": 3,
                        "1111": 3,
                    },
                    {
                        "0000": 3,
                        "0001": 6,
                        "0010": 7,
                        "0011": 1,
                        "0100": 1,
                        "0101": 5,
                        "0110": 4,
                        "1000": 2,
                        "1001": 4,
                        "1011": 3,
                        "1100": 6,
                        "1111": 1,
                    },
                ]

                results = []
                for circ, cnt in zip(run_input, counts):
                    results.append(
                        {
                            "shots": -1,
                            "success": True,
                            "header": {"metadata": circ.metadata},
                            "data": {"counts": cnt},
                        }
                    )

                res = {
                    "backend_name": "backend",
                    "backend_version": "0",
                    "qobj_id": uuid.uuid4().hex,
                    "job_id": uuid.uuid4().hex,
                    "success": True,
                    "results": results,
                }
                return FakeJob(backend=self, result=Result.from_dict(res))

        class Experiment(FakeExperiment):
            def circuits(self):
                circs = []
                for i in range(5):
                    circ = QuantumCircuit(2, 2)
                    circ.metadata = {}
                    circs.append(circ)
                return circs

        exp1 = Experiment([0, 2])
        exp2 = Experiment([1, 3])
        par_exp = ParallelExperiment([exp1, exp2])
        expdata = par_exp.run(Backend()).block_for_results()

        expected_counts = [
            [
                {"00": 14, "10": 19, "11": 11, "01": 8},
                {"01": 14, "10": 7, "11": 13, "00": 12},
                {"00": 14, "01": 5, "10": 16, "11": 17},
                {"00": 4, "01": 16, "10": 19, "11": 13},
                {"00": 12, "01": 15, "10": 11, "11": 5},
            ],
            [
                {"00": 10, "01": 10, "10": 12, "11": 20},
                {"00": 12, "01": 10, "10": 7, "11": 17},
                {"00": 17, "01": 7, "10": 14, "11": 14},
                {"00": 9, "01": 14, "10": 22, "11": 7},
                {"00": 17, "01": 10, "10": 9, "11": 7},
            ],
        ]

        for child, counts in zip(expdata.child_data(), expected_counts):
            for child_counts, cnt in zip(child.data(), counts):
                self.assertDictEqual(child_counts["counts"], cnt)

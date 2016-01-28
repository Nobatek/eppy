# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""
Tests for features in eppy.runner related to running EnergyPlus from Eppy.
"""





from glob import glob
from subprocess import CalledProcessError
import multiprocessing
import os
import re
import shutil

from eppy.runner.run_functions import EPLUS_WEATHER
from eppy.runner.run_functions import VERSION
from eppy.runner.run_functions import multirunner
from eppy.runner.run_functions import run
from eppy.runner.run_functions import runIDFs
from eppy.runner.runner import IDF5


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
IDD_FILES = os.path.join(THIS_DIR, os.pardir, 'resources/iddfiles')
IDF_FILES = os.path.join(THIS_DIR, os.pardir, 'resources/idffiles')

TEST_IDF = "V{}/smallfile.idf".format(VERSION[:3].replace('-', '_'))
TEST_EPW = 'USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw'
TEST_IDD = "Energy+V{}.idd".format(VERSION.replace('-', '_'))
TEST_OLD_IDD = 'Energy+V8_1_0.idd'


def has_severe_errors(results='run_outputs'):
    """Check for severe errors in the eplusout.end file.
    """
    end_filename = glob('{}/*.end'.format(results))[0]
    with open(os.path.join(end_filename), 'r') as end_file:
        end_txt = end_file.read()
    num_severe = int(re.findall(r' (\d*) Severe Error', end_txt)[0])
    return num_severe > 0


class TestMultiprocessing(object):

    """Tests for running multiple EnergyPlus jobs simultaneously.
    """

    def setup(self):
        """Clear out any results from previous tests.
        """
        os.chdir(THIS_DIR)
        shutil.rmtree("multirun_outputs", ignore_errors=True)
        self.expected_files = [
            'eplusout.audit', 'eplusout.bnd', 'eplusout.eio',
            'eplusout.end', 'eplusout.err', 'eplusout.eso',
            'eplusout.mdd', 'eplusout.mtd', 'eplusout.rdd',
            'eplusout.shd', 'eplustbl.htm', 'sqlite.err']

    def teardown(self):
        """Remove the multiprocessing results folders.
        """
        for results_dir in glob('results_*'):
            shutil.rmtree(results_dir)
        shutil.rmtree("test_results", ignore_errors=True)
        shutil.rmtree("run_outputs", ignore_errors=True)

    def test_sequential_run(self):
        """
        Test that we can run a sequence of runs using the signature:
            run([idf_path, epw], kwargs)
        Fails if expected output files are not in the expected output
        directories.

        """
        fname1 = os.path.join(IDF_FILES, TEST_IDF)
        runs = []
        for i in range(2):
            kwargs = {'output_directory': 'results_%s' % i}
            runs.append([[fname1, TEST_EPW], kwargs])
        for r in runs:
            run(*r[0], **r[1])
        for results_dir in glob('results_*'):
            assert not has_severe_errors(results_dir)
            files = os.listdir(results_dir)
            assert set(files) == set(self.expected_files)

    def test_multiprocess_run(self):
        """
        Test that we can run a list of runs in parallel using the signature:
            run([idf_path, epw], kwargs)
        Fails if expected output files are not in the expected output
        directories.

        """
        fname1 = os.path.join(IDF_FILES, TEST_IDF)
        runs = []
        for i in range(2):
            kwargs = {'output_directory': 'results_%s' % i}
            runs.append([[fname1, TEST_EPW], kwargs])
        pool = multiprocessing.Pool(2)
        pool.map(multirunner, runs)
        pool.close()

    def test_multiprocess_run_IDF5(self):
        """
        Test that we can run a sequence of runs using the signature:
            runIDFs([[IDF5, kwargs],...], num_CPUs)
        Fails if expected output files are not in the expected output
        directories.

        """
        iddfile = os.path.join(IDD_FILES, TEST_IDD)
        fname1 = os.path.join(IDF_FILES, TEST_IDF)
        IDF5.setiddname(open(iddfile, 'r'), testing=True)
        runs = []
        for i in range(4):
            runs.append([IDF5(open(fname1, 'r'), TEST_EPW),
                         {'output_directory': 'results_%i' % i}])
        num_CPUs = 2
        runIDFs(runs, num_CPUs)

        num_CPUs = -1
        runIDFs(runs, num_CPUs)


class TestRunFunction(object):

    """Tests for simple running of EnergyPlus from Eppy.
    """

    def setup(self):
        """Tidy up just in case anything is left from previous test runs.
        """
        os.chdir(THIS_DIR)
        shutil.rmtree("test_results", ignore_errors=True)
        shutil.rmtree("run_outputs", ignore_errors=True)

    def teardown(self):
        """Tidy up after tests.
        """
        os.chdir(THIS_DIR)
        shutil.rmtree("test_results", ignore_errors=True)
        shutil.rmtree("run_outputs", ignore_errors=True)

    def test_run_relative_paths(self):
        """
        Test that running works with a relative path.
        Fails if no results are produced.

        """
        relative_path = os.path.join("../resources/idffiles", TEST_IDF)
        run(relative_path, TEST_EPW, output_directory="test_results")
        assert len(os.listdir('test_results')) > 0
        for f in os.listdir('test_results'):
            assert os.path.isfile(os.path.join('test_results', f))

    def test_run_abs_paths(self):
        """
        Test that running works with absolute paths.
        Fails if no results are produced.

        """
        fname1 = os.path.join(IDF_FILES, TEST_IDF)
        epw = os.path.join(
            EPLUS_WEATHER, TEST_EPW)
        run(fname1, epw, output_directory="test_results")
        assert len(os.listdir('test_results')) > 0
        for f in os.listdir('test_results'):
            assert os.path.isfile(os.path.join('test_results', f))

    def test_run_weather_name_only(self):
        """
        Test that running works with the name of a weather file that is
        in the Weather subdirectory of the EnergyPlus install directory.
        Fails if no results are produced.

        """
        fname1 = os.path.join(IDF_FILES, TEST_IDF)
        run(fname1, TEST_EPW, output_directory="test_results")
        assert len(os.listdir('test_results')) > 0
        for f in os.listdir('test_results'):
            assert os.path.isfile(os.path.join('test_results', f))

    def test_run_missing_file_raises_error(self, capfd):
        """
        Test that a missing file produces the expected warning to std
        out.
        Fails if error message is not as expected.

        """
        fname1 = os.path.join(IDF_FILES, "XXXXXXX_fake_file.idf")
        try:
            run(fname1, TEST_EPW, output_directory="test_results")
            assert False  # missed the error
        except CalledProcessError:
            out, _err = capfd.readouterr()
            assert "ERROR: Could not find input data file:" in out


class TestIDFRunner(object):

    """Tests for running EnergyPlus from an IDF5 object.
    """

    def setup(self):
        """Tidy up anything left from previous runs. Get an IDF object to run.
        """
        outdir = os.path.join(THIS_DIR, 'run_outputs')
        if os.path.isdir(outdir):
            shutil.rmtree(outdir)
        iddfile = os.path.join(IDD_FILES, TEST_IDD)
        fname1 = os.path.join(IDF_FILES, TEST_IDF)
        IDF5.setiddname(open(iddfile, 'r'), testing=True)
        self.idf = IDF5(open(fname1, 'r'), TEST_EPW)

        self.expected_files = [
            'eplusout.audit', 'eplusout.bnd', 'eplusout.eio',
            'eplusout.end', 'eplusout.err', 'eplusout.eso',
            'eplusout.mdd', 'eplusout.mtd', 'eplusout.rdd',
            'eplusout.shd', 'eplustbl.htm', 'sqlite.err', ]
#            u'eplusout.iperr']
        self.expected_files_suffix_C = [
            'eplus.audit', 'eplus.mdd', 'eplus.err',
            'eplusSqlite.err', 'eplus.eio', 'eplusTable.htm', 'eplus.shd',
            'eplus.mtd', 'eplus.bnd', 'eplus.eso', 'eplus.rdd',
            'eplus.end']
        self.expected_files_suffix_D = [
            'eplus.audit', 'eplus.mdd', 'eplus-sqlite.err',
            'eplus-table.htm', 'eplus.err', 'eplus.eio', 'eplus.bnd',
            'eplus.shd', 'eplus.mtd', 'eplus.end', 'eplus.eso',
            'eplus.rdd']

    def teardown(self):
        """Destroy temp dir, reset working directory, destroy outputs.
        """
        os.chdir(THIS_DIR)
        shutil.rmtree('run_outputs', ignore_errors=True)
        shutil.rmtree('other_run_outputs', ignore_errors=True)
        shutil.rmtree("test_results", ignore_errors=True)

    def num_rows_in_csv(self, results='./run_outputs'):
        """Check readvars outputs the expected number of rows.
        """
        with open(os.path.join(results, 'eplusout.csv'), 'r') as csv_file:
            return len(csv_file.readlines())

    def test_run(self):
        """
        End to end test of idf.run function.
        Fails on severe errors or unexpected/missing output files.

        """
        self.idf.run()
        assert not has_severe_errors()
        files = os.listdir('run_outputs')
        assert set(files) == set(self.expected_files)

    def test_run_readvars(self):
        """
        End to end test of idf.run function with readvars set True.
        Fails on severe errors or unexpected/missing output files.

        """
        self.idf.run(readvars=True)
        assert not has_severe_errors()
        files = os.listdir('run_outputs')
        self.expected_files.extend(['eplusout.rvaudit', 'eplusout.csv'])
        assert set(files) == set(self.expected_files)

    def test_run_annual(self):
        """
        End to end test of idf.run function with annual set True.
        Fails on incorrect size of CSV output, severe errors or
        unexpected/missing output files.

        """
        self.idf.idfobjects['RUNPERIOD'][0].End_Month = 1
        self.idf.run(annual=True, readvars=True)
        assert not has_severe_errors()
        files = os.listdir('run_outputs')
        self.expected_files.extend(['eplusout.rvaudit', 'eplusout.csv'])
        assert set(files) == set(self.expected_files)
        assert self.num_rows_in_csv() == 35041  # 24 * 365 * 4 + 1 header row

    def test_run_output_directory(self):
        """
        End to end test of idf.run function with a specific output dir set.
        Fails on severe errors or unexpected/missing output files.

        """
        self.idf.run(output_directory='other_run_outputs')
        assert not has_severe_errors('other_run_outputs')
        files = os.listdir('other_run_outputs')
        self.expected_files.extend([])
        assert set(files) == set(self.expected_files)

    def test_run_design_day(self):
        """
        End to end test of idf.run function with design_day flag set True.
        Fails on incorrect size of CSV output, severe errors or
        unexpected/missing output files.

        """
        self.idf.run(design_day=True, readvars=True)
        assert not has_severe_errors()
        files = os.listdir('run_outputs')
        self.expected_files.extend(['eplusout.rvaudit', 'eplusout.csv'])
        assert set(files) == set(self.expected_files)
        assert self.num_rows_in_csv() == 193  # 24 * 8 + 1 header row

    def test_run_epmacro(self):
        """
        End to end test of idf.run function with epmacro flag set True.
        Fails on severe errors or unexpected/missing output files.

        """
        self.idf.run(epmacro=True)
        assert not has_severe_errors()
        files = os.listdir('run_outputs')
        self.expected_files.extend(['eplusout.epmdet', 'eplusout.epmidf'])
        assert set(files) == set(self.expected_files)

    def test_run_expandobjects(self):
        """
        End to end test of idf.run function with expandobjects flag set to
        True.
        Fails on severe errors or unexpected/missing output files.

        """
        self.idf.newidfobject(
            'HVACTEMPLATE:THERMOSTAT',
            Name="TestThermostat",
            Cooling_Setpoint_Schedule_Name="",
            Heating_Setpoint_Schedule_Name="",
            Constant_Cooling_Setpoint=25,
            Constant_Heating_Setpoint=21,
        )
        self.idf.run(expandobjects=True)
        assert not has_severe_errors()
        files = os.listdir('run_outputs')
        self.expected_files.extend(['eplusout.expidf'])
        assert set(files) == set(self.expected_files)

    def test_run_output_prefix(self):
        """
        End to end test of idf.run function with output prefix set.
        Fails on severe errors or unexpected/missing output files.

        """
        self.idf.run(output_prefix='test')
        assert not has_severe_errors()
        files = os.listdir('run_outputs')
        prefixed_files = [f.replace('eplus', 'test')
                          for f in self.expected_files]
        assert set(files) == set(prefixed_files)

    def test_run_output_suffix_L(self):
        """
        End to end test of idf.run function with output suffix set.
        Fails on severe errors or unexpected/missing output files.

        """
        self.idf.run(output_suffix='L')
        assert not has_severe_errors()
        files = os.listdir('run_outputs')
        assert set(files) == set(self.expected_files)

    def test_run_output_suffix_C(self):
        """
        End to end test of idf.run function with output suffix set.
        Fails on severe errors or unexpected/missing output files.

        """
        self.idf.run(output_suffix='C')
        assert not has_severe_errors()
        files = os.listdir('run_outputs')
        assert set(files) == set(self.expected_files_suffix_C)

    def test_run_output_suffix_D(self):
        """
        End to end test of idf.run function with output suffix set.
        Fails on severe errors or unexpected/missing output files.

        """
        self.idf.run(output_suffix='D')
        assert not has_severe_errors()
        files = os.listdir('run_outputs')
        assert set(files) == set(self.expected_files_suffix_D)

    def test_run_IDD(self):
        """
        End to end test of idf.run function with a different IDD set.
        We use an old IDD here since it throws an error we can see. Real uses
        of this option would include using an IDD with extra fields added
        extensible fields to allow larger objects.
        Fails if the expected IDD version is not listed in the error file.

        """
        other_idd = os.path.join(IDD_FILES, TEST_OLD_IDD)
        self.idf.run(idd=other_idd)
        with open('run_outputs/eplusout.err', 'r') as errors:
            assert "IDD_Version 8.1.0.009" in errors.readline()

    def test_version(self, capfd):
        """
        End to end test of idf.run function with the version flag set True.
        Fails if the expected EnergyPlus version number is not returned.

        """
        self.idf.run(version=True)
        out, _err = capfd.readouterr()

        expected_version = VERSION.replace('-', '.')
        version_string = "EnergyPlus, Version {}".format(expected_version)

        assert out.strip().startswith(version_string)

    def test_help(self, capfd):
        """
        Test of calling the `help` built-in function on an IDF5 object.
        Fails if the expected help output is not returned.

        """
        help(self.idf.run)
        out, _err = capfd.readouterr()
        expected = "Help on method run in module eppy.runner.runner:"

        assert out.strip().startswith(expected)

    def test_verbose(self, capfd):
        """
        End to end test of idf.run function with the version flag set True.
        Fails on severe errors or unexpected/missing output files.
        Fails if no output received from EnergyPlus.

        """
        self.idf.run(verbose='v')
        assert not has_severe_errors()
        files = os.listdir('run_outputs')
        self.expected_files.extend([])
        assert set(files) == set(self.expected_files)
        out, _err = capfd.readouterr()
        assert len(out) > 0

    def test_quiet(self, capfd):
        """
        End to end test of idf.run function with the version flag set True.
        Fails on severe errors or unexpected/missing output files.
        Fails if output received from EnergyPlus.

        """
        self.idf.run(verbose='q')
        assert not has_severe_errors()
        files = os.listdir('run_outputs')
        self.expected_files.extend([])
        assert set(files) == set(self.expected_files)
        out, _err = capfd.readouterr()
        assert len(out) == 0

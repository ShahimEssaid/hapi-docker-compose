import logging
import pathlib
import shutil
import subprocess
from os import environ
from subprocess import Popen
from typing import List, Optional


class HapiSetup:
    def __init__(self,
                 setup_path: pathlib.Path,
                 build_docker_image: bool,
                 build_hapi: bool,
                 stdout: bool,
                 stderr: bool,
                 restart_exit_code: int,
                 attach: bool = False,
                 debug: bool = False
                 ):
        self._setup_path = setup_path
        self._build_docker_image = build_docker_image
        self._build_hapi = build_hapi
        self._stdout = stdout
        self._stderr = stderr
        self._restart_exit_code = restart_exit_code
        self._popen: Optional[Popen] = None
        self._attach: bool = attach
        self._debug = debug

    # =========================
    # Setup high level commands
    # =========================

    def start(self):
        if self._build_hapi:
            self.hapi_build_build()
        self.hapi_up_exit_code_restart()

    def stop(self):
        logging.info("Stopping HAPI setup")
        return self.compose(['stop'])

    def down(self):
        logging.info("Downing HAPI setup")
        return self.compose(['down'])

    def reset(self, **kwargs):
        self.down()
        if kwargs['pg']:
            self.postgresql_reset()
        if kwargs['es']:
            self.elasticsearch_reset()
        if kwargs['hapi_target']:
            shutil.rmtree(self._setup_path / 'service' / 'hapi' / 'mounts' / 'workdir' / 'target', ignore_errors=True)
        if kwargs['hapi_logs']:
            shutil.rmtree(self._setup_path / 'service' / 'hapi' / 'mounts' / 'workdir' / 'logs', ignore_errors=True)
        if kwargs['hapi_loaders']:
            for p in (self._setup_path / 'service' / 'hapi' / 'mounts' / 'workdir' / 'loaders').glob("**/*loaded.txt"):
                p.unlink()
            for p in (self._setup_path / 'service' / 'hapi' / 'mounts' / 'workdir' / 'loaders').glob("**/*loading.txt"):
                p.unlink()
            for p in (self._setup_path / 'service' / 'hapi' / 'mounts' / 'workdir' / 'loaders').glob("**/*response.txt"):
                p.unlink()
        # if kwargs['hapi_build']:
        #     shutil.rmtree(self._setup_path / 'hapi' / 'logs', ignore_errors=True)

    # =========================
    # Postgresql commands
    # =========================

    def postgresql_up(self):
        args = []
        args.extend(['up'])
        self._up_args(args)
        args.append('postgresql')
        return self.compose(args)

    def postgresql_stop(self):
        args = []
        args.extend(['stop', 'postgresql'])
        return self.compose(args)

    def postgresql_rm(self):
        args = []
        args.extend(['rm', '-f', 'postgresql'])
        return self.compose(args)

    def postgresql_reset(self):
        shutil.rmtree(self._setup_path / environ['HS_PG_SERVICE_DIR'] / 'mounts' / 'data')

    # =========================
    # Elasticsearch commands
    # =========================

    def elasticsearch_up(self):
        args = []
        args.extend(['up'])
        self._up_args(args)
        args.append('elasticsearch')
        return self.compose(args)

    def elasticsearch_stop(self):
        args = []
        args.extend(['stop', 'elasticsearch'])
        return self.compose(args)

    def elasticsearch_rm(self):
        args = []
        args.extend(['rm', '-f', 'elasticsearch'])
        return self.compose(args)

    def elasticsearch_reset(self):
        shutil.rmtree(self._setup_path / environ['HS_ESREST_SERVICE_DIR'] / 'mounts' / 'data')

    # =========================
    # Kibana commands
    # =========================

    def kibana_up(self):
        args = []
        args.extend(['up'])
        self._up_args(args)
        args.append('kibana')
        return self.compose(args)

    def kibana_stop(self):
        args = []
        args.extend(['stop', 'kibana'])
        return self.compose(args)

    def kibana_rm(self):
        args = []
        args.extend(['rm', '-f', 'kibana'])
        return self.compose(args)

    # =========================
    # HAPI build commands
    # =========================

    def hapi_build_build(self) -> Optional[Popen]:
        args = ['run', '--rm']
        if self._build_docker_image:
            args.append('--build')
        args.append('hapi-build')
        return self.compose(args)

    # =========================
    # HAPI commands
    # =========================

    def hapi_up_exit_code_restart(self):
        logging.info('Starting HAPI')
        while True:
            self.hapi_build_build()
            logging.info('Finished building HAPI')
            self._popen = self.hapi_up_exit_code()
            if self._popen.returncode != self._restart_exit_code:
                break

    def hapi_up_exit_code(self) -> Popen:
        return self.compose(['up', '--exit-code-from', 'hapi'])

    # =========================
    # HAPI load commands
    # =========================

    def hapi_load(self, loaders_dir):
        logging.info(f"Loading HAPI from: {loaders_dir}")
        args = ['exec', 'hapi', 'hapisetup-hapi-load', loaders_dir]
        return self.compose(args)

    # =========================
    # Jansugraph
    # =========================

    def janusgraph_up(self):
        logging.info(f'Janusgraph up.')
        args = []
        args.extend(['up'])
        self._up_args(args)
        args.append('janusgraph')
        return self.compose(args)

    def janusgraph_stop(self):
        args = []
        args.extend(['stop', 'janusgraph'])
        return self.compose(args)

    def janusgraph_config(self):
        args = []
        args.extend(['stop', 'janusgraph'])
        return self.compose(args)

    def janusgraph_rm(self):
        args = []
        args.extend(['rm', '-f', 'janusgraph'])
        return self.compose(args)

    # =========================
    # Cassandra
    # =========================

    def cassandra_up(self):
        logging.info(f'Cassandra up.')
        args = []
        args.extend(['up'])
        self._up_args(args)
        args.append('cassandra')
        return self.compose(args)

    def cassandra_stop(self):
        args = []
        args.extend(['stop', 'cassandra'])
        return self.compose(args)

    def cassandra_rm(self):
        args = []
        args.extend(['rm', '-f', 'cassandra'])
        return self.compose(args)

    # =========================
    # Compose
    # =========================

    def compose(self, args: List[str]) -> Popen:
        compose = ['docker', 'compose']

        for profile in environ['HS_PROFILES'].split(','):
            compose.extend(['--profile', profile])
        compose.extend(args)

        kwargs = {
            'stdout': subprocess.DEVNULL,
            'stderr': subprocess.DEVNULL
        }
        if self._stdout:
            kwargs['stdout'] = None
        if self._stderr:
            kwargs['stderr'] = None

        if self._debug:
            logging.debug(f'Running docker compose with args: {compose} and Popen options: {kwargs}')
        popen = Popen(compose, env=environ, **kwargs)
        popen.wait()
        return popen

    def _up_args(self, args):
        if self._build_docker_image:
            args.append('--build')
        if not self._attach:
            args.append('--detach')

    def _remove_container(self, container: str):
        shutil.rmtree(self._setup_path / 'service' / container, ignore_errors=True)

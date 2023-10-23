# defaults

(service.path / 'config' / 'envs' / 'local.env').touch(exist_ok=True)
(service.path / 'service' / 'mounts' / 'hapi' / 'load_zips').mkdir(exist_ok=True, parents=True)
(service.path / 'service' / 'mounts' / 'hapi' / 'load_unzips').mkdir(exist_ok=True, parents=True)
(service.path / 'service' / 'mounts' / 'hapibuild').mkdir(exist_ok=True, parents=True)

# reset globs
service.add_reset_glob(f'service/mounts/hapi/target')
service.add_reset_glob(f'service/mounts/hapi/ROOT.war*')
service.add_reset_glob(f'service/mounts/hapi/logs')
service.add_reset_glob(f'service/mounts/hapi/load_unzips/**/*load*.txt')
# service.add_reset_glob(f'service/mounts/hapibuild')
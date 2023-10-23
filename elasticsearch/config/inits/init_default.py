# defaults

(service.path / 'config' / 'envs' / 'local.env').touch(exist_ok=True)
(service.path / 'service' / 'mounts' / 'data').mkdir(exist_ok=True, parents=True)
service.add_reset_glob(f'service/mounts/data/nodes')

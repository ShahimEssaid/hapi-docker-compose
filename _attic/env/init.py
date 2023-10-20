import glob
# Allow a  "project" to set HS_PROFILES and other variables as needed and be committed.
init_project_path = Path('env/project.py')
init_project_path.touch()
exec(open(init_project_path).read())

# Allow local configuration to set/override HS_PROFILES
init_local_path = Path('env/local.py')
init_local_path.touch()
exec(open(init_local_path).read())

# Load defaults for the service
os.environ['HS_SERVICES'] = os.environ.get('HS_SERVICES', ',postgres,')
for service in [p.strip() for p in os.environ['HS_SERVICES'].split(',')]:
    if not service:
        continue
    cli_environment_path = Path(service) / 'config' / 'cli-environment-defaults.py'
    print(f'Loading service CLIP environment from: {cli_environment_path}')
    exec(open(cli_environment_path).read())

# Need to have these files in place to avoid errors from the compose file referencing them.
for config_dir in glob.glob('*/config/'):
    (Path(config_dir) / 'local.env').touch()

# If HS_PROFILES not set by this point, we set the default.
os.environ['HS_PROFILES'] = os.environ.get('HS_PROFILES', 'env-default,hs-default,hs-project,hs-local')
if os.environ['HS_PROFILES_PREFIX']:
    os.environ['HS_PROFILES'] = os.environ['HS_PROFILES_PREFIX'] + ',' + os.environ['HS_PROFILES']
if os.environ['HS_PROFILES_SUFFIX']:
    os.environ['HS_PROFILES'] = os.environ['HS_PROFILES'] + ',' + os.environ['HS_PROFILES_SUFFIX']

# Override with value from HS_PROFILES_CMDLINE which is set if --profiles command line option is used
# This is to help scripts set the profiles they want for that run of the script and overriding the above configuration.
os.environ['HS_PROFILES'] = os.environ.get('HS_PROFILES_CMDLINE', os.environ['HS_PROFILES'])

# Load the profiles
for env in [p.strip() for p in os.environ['HS_PROFILES'].split(',')]:
    if not env:
        continue
    if env.startswith('env-'):
        env_path = Path(f'env/{env[4:]}.py').absolute()
        print(f'Attempting to load environment file: {env_path}')
        exec(open(env_path).read())



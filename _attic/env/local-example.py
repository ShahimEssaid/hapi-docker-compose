from os import environ

# Overwrite profiles from env-init.py if needed.
# If you want to use HAPI with Elasticsearch and Kibana, uncomment the following line and adjust as needed.
# environ['HS_PROFILES'] = 'env-defaults,hs-defaults,hs-postgresql,hs-elasticsearch,hs-kibana,hs-local'

# The following allows for shifting the ports by an offset.  This is the default offset
#environ['HS_PORT_OFFSET'] = environ.get('HS_PORT_OFFSET', '10000')

# Set the following to your actual environment.
#environ['HS_HAPI_HOST'] = '127.0.0.1'
#environ['HS_HAPI_HOST_PUBLIC'] = '127.0.0.1'
#environ['HS_HAPI_PORT'] = '18080'
#environ['HS_HAPI_PORT_PUBLIC'] = '18080'

# Uncomment and set your desired repo and build command like this:
#environ['HS_HAPI_BUILD_GIT_REPO'] = 'https://github.com/hapifhir/hapi-fhir-jpaserver-starter.git'
#environ['HS_HAPI_BUILD_GIT_REF'] = 'refs/tags/v6.4.0'
#environ['HS_HAPI_BUILD_CMD'] = 'mvn -U -Pboot -DskipTests clean package'
#environ['HS_HAPI_BUILD_ALWAYS'] = 'false'

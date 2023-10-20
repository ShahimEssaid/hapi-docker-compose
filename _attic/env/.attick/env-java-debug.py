from os import environ

# This is to enable JVM debugging when needed.
environ['HS_HAPI_JAVA_OPTIONS'] = \
    environ['HS_HAPI_JAVA_OPTIONS'] + \
    f' -agentlib:jdwp=\"transport=dt_socket,server=y,suspend=y,address=*:8081\"'

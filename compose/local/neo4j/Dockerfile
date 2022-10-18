# For arm64 hosts like M1 Macs we need to be able to configure a different base image.
ARG NEO4J_IMAGE=neo4j:4.1
FROM ${NEO4J_IMAGE}

# The URLs in the plugins file in the base neo4j image are outdated and need to be updated.
# See https://github.com/neo4j/graph-data-science/issues/227
COPY ./compose/local/neo4j/neo4jlabs-plugins.json /neo4jlabs-plugins.json
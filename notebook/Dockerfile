# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Pick your favorite docker-stacks image
FROM jupyter/all-spark-notebook

USER root

# Add permanent apt-get installs and other root commands here
# e.g., RUN apt-get install npm nodejs

USER $NB_UID

# Switch back to jovyan to avoid accidental container runs as root
# Add permanent pip/conda installs, data files, other user libs here
# e.g., RUN pip install jupyter_dashboards


RUN pip install --pre gql[aiohttp]

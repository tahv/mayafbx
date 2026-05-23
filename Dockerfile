ARG MAYA_VERSION=latest
FROM tahv/mayapy:$MAYA_VERSION
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN ln -s /lib/x86_64-linux-gnu/libreadline.so.8 /lib/x86_64-linux-gnu/libreadline.so.7
ENV UV_PYTHON=/usr/autodesk/maya/bin/mayapy
# https://github.com/ofek/hatch-vcs/issues/108
ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0
WORKDIR /app
COPY . .
RUN uv export --group dev --no-hashes | uv pip install --system -r -
ENV FORCE_COLOR=1
CMD ["mayapy", "-ic", "import maya.standalone; maya.standalone.initialize(); from maya import cmds; cmds.loadPlugin('fbxmaya')"]

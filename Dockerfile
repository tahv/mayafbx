ARG MAYA_VERSION=2024
FROM mottosso/maya:$MAYA_VERSION

WORKDIR /app

RUN mayapy -m pip install pytest coverage

COPY . .

RUN mayapy -m pip install --editable .

CMD ["mayapy", "-ic", "import maya.standalone; maya.standalone.initialize(); from maya import cmds; cmds.loadPlugin('fbxmaya')"]

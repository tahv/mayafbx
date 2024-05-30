ARG MAYA_VERSION=latest

FROM tahv/mayapy:$MAYA_VERSION

WORKDIR /app

RUN mayapy -m pip install --upgrade pip && mayapy -m pip install pytest coverage

COPY . .

RUN mayapy -m pip install --editable .

CMD ["mayapy", "-ic", "import maya.standalone; maya.standalone.initialize(); from maya import cmds; cmds.loadPlugin('fbxmaya')"]

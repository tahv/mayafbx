ARG MAYA_VERSION=2024
FROM mottosso/maya:$MAYA_VERSION

# RUN python -m pip install pytest coverage

COPY . .

CMD ["mayapy", "-ic", "import maya.standalone; maya.standalone.initialize(); from maya import cmds; cmds.loadPlugin('fbxmaya')"]

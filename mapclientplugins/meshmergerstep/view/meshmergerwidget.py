'''
Created on Sep 10, 2017

@author: Richard Christie
'''
from PySide import QtGui, QtCore
from functools import partial
from opencmiss.zinc.field import Field
from opencmiss.zinc.sceneviewer import Sceneviewer
from opencmiss.zinc.selection import Selectionevent

from mapclientplugins.meshmergerstep.view.ui_meshmergerwidget import Ui_MeshMergerWidget
from mapclientplugins.meshmergerstep.utils import zinc as zincutils

class MeshMergerWidget(QtGui.QWidget):
    '''
    classdocs
    '''

    def __init__(self, model, parent=None):
        '''
        Constructor
        '''
        super(MeshMergerWidget, self).__init__(parent)
        self._ui = Ui_MeshMergerWidget()
        self._ui.setupUi(self)
        self._model = model
        context = model.getContext()
        self._ui.master_sceneviewerWidget.setContext(context)
        scenefiltermodule = context.getScenefiltermodule()
        self._scenefilterNodes = scenefiltermodule.createScenefilterFieldDomainType(Field.DOMAIN_TYPE_NODES)
        self._ui.master_sceneviewerWidget.graphicsInitialized.connect(self._graphicsInitializedMaster)
        self._ui.slave_sceneviewerWidget.setContext(model.getContext())
        self._ui.slave_sceneviewerWidget.graphicsInitialized.connect(self._graphicsInitializedSlave)
        self._model.registerSceneChangeCallback(self._sceneChanged)
        self._doneCallback = None
        self._refreshOptions()
        self._makeConnections()
        self._masterSelectionnotifier = None
        self._slaveSelectionnotifier = None
        self._setupSelectionCallbacks()

    def _graphicsInitializedMaster(self):
        '''
        Callback for when SceneviewerWidget is initialised
        Set custom scene from model
        '''
        sceneviewer = self._ui.master_sceneviewerWidget.getSceneviewer()
        if sceneviewer is not None:
            scene = self._model.getMasterScene()
            self._ui.master_sceneviewerWidget.setScene(scene)
            self._ui.master_sceneviewerWidget.setSelectionfilter(self._scenefilterNodes)
            self._ui.master_sceneviewerWidget.setSelectModeNode()
            sceneviewer.setLookatParametersNonSkew([2.0, -2.0, 1.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0])
            sceneviewer.setTransparencyMode(sceneviewer.TRANSPARENCY_MODE_SLOW)
            self._viewAll()

    def _graphicsInitializedSlave(self):
        '''
        Callback for when SceneviewerWidget is initialised
        Set custom scene from model
        '''
        sceneviewer = self._ui.slave_sceneviewerWidget.getSceneviewer()
        if sceneviewer is not None:
            scene = self._model.getSlaveScene()
            self._ui.slave_sceneviewerWidget.setScene(scene)
            self._ui.slave_sceneviewerWidget.setSelectionfilter(self._scenefilterNodes)
            self._ui.slave_sceneviewerWidget.setSelectModeNode()
            sceneviewer.setLookatParametersNonSkew([2.0, -2.0, 1.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0])
            sceneviewer.setTransparencyMode(sceneviewer.TRANSPARENCY_MODE_SLOW)
            self._viewAll()

    def _selectionCallbackMaster(self, event):
        change = event.getChangeFlags()
        if change & Selectionevent.CHANGE_FLAG_ADD:
            masterNode = zincutils.getSelectedNode(self._model.getMasterScene())
            if masterNode is not None:
                self._ui.mergeNodesEntry_lineEdit.setText(str(masterNode.getIdentifier()) + '=')
                self._mergeNodesEntryChanged()

    def _selectionCallbackSlave(self, event):
        change = event.getChangeFlags()
        if change & Selectionevent.CHANGE_FLAG_ADD:
            masterNode = zincutils.getSelectedNode(self._model.getMasterScene())
            slaveNode = zincutils.getSelectedNode(self._model.getSlaveScene())
            if (masterNode is not None) and (slaveNode is not None):
                self._ui.mergeNodesEntry_lineEdit.setText(str(masterNode.getIdentifier()) + '=' + str(slaveNode.getIdentifier()))
                self._mergeNodesEntryChanged()

    def _setupSelectionCallbacks(self):
        self._masterSelectionnotifier = self._model.getMasterScene().createSelectionnotifier()
        self._masterSelectionnotifier.setCallback(self._selectionCallbackMaster)
        if self._slaveSelectionnotifier is None:
            self._slaveSelectionnotifier = self._model.getSlaveScene().createSelectionnotifier()
            self._slaveSelectionnotifier.setCallback(self._selectionCallbackSlave)

    def _sceneChanged(self):
        sceneviewer = self._ui.master_sceneviewerWidget.getSceneviewer()
        if sceneviewer is not None:
            scene = self._model.getMasterScene()
            self._ui.master_sceneviewerWidget.setScene(scene)
        sceneviewer = self._ui.slave_sceneviewerWidget.getSceneviewer()
        if sceneviewer is not None:
            scene = self._model.getSlaveScene()
            self._ui.slave_sceneviewerWidget.setScene(scene)
        self._setupSelectionCallbacks()

    def _makeConnections(self):
        self._ui.done_button.clicked.connect(self._doneButtonClicked)
        self._ui.viewAll_button.clicked.connect(self._viewAll)
        self._ui.mergeNodesEntry_lineEdit.returnPressed.connect(self._mergeNodesEntryChanged)
        self._ui.mergeNodesDelete_pushButton.clicked.connect(self._meshNodesDeleteClicked)
        self._ui.previewAlign_checkBox.clicked.connect(self._previewAlignClicked)
        self._ui.previewFit_checkBox.clicked.connect(self._previewFitClicked)
        self._ui.displayAxes_checkBox.clicked.connect(self._displayAxesClicked)
        self._ui.displayElementNumbers_checkBox.clicked.connect(self._displayElementNumbersClicked)
        self._ui.displayLines_checkBox.clicked.connect(self._displayLinesClicked)
        self._ui.displayNodeDerivatives_checkBox.clicked.connect(self._displayNodeDerivativesClicked)
        self._ui.displayNodeNumbers_checkBox.clicked.connect(self._displayNodeNumbersClicked)
        self._ui.displaySurfaces_checkBox.clicked.connect(self._displaySurfacesClicked)
        self._ui.displaySurfacesExterior_checkBox.clicked.connect(self._displaySurfacesExteriorClicked)
        self._ui.displaySurfacesTranslucent_checkBox.clicked.connect(self._displaySurfacesTranslucentClicked)
        self._ui.displaySurfacesWireframe_checkBox.clicked.connect(self._displaySurfacesWireframeClicked)
        self._ui.displayXiAxes_checkBox.clicked.connect(self._displayXiAxesClicked)

    def getModel(self):
        return self._model

    def registerDoneExecution(self, doneCallback):
        self._doneCallback = doneCallback

    def _doneButtonClicked(self):
        self._model.done()
        self._model = None
        self._doneCallback()

    def _refreshOptions(self):
        self._ui.identifier_label.setText('Identifier:  ' + self._model.getIdentifier())
        self._ui.mergeNodes_plainTextEdit.setPlainText(self._model.getMergeNodesText())
        self._ui.previewAlign_checkBox.setChecked(self._model.isPreviewAlign())
        self._ui.previewFit_checkBox.setChecked(self._model.isPreviewFit())
        self._ui.displayAxes_checkBox.setChecked(self._model.isDisplayAxes())
        self._ui.displayElementNumbers_checkBox.setChecked(self._model.isDisplayElementNumbers())
        self._ui.displayLines_checkBox.setChecked(self._model.isDisplayLines())
        self._ui.displayNodeDerivatives_checkBox.setChecked(self._model.isDisplayNodeDerivatives())
        self._ui.displayNodeNumbers_checkBox.setChecked(self._model.isDisplayNodeNumbers())
        self._ui.displaySurfaces_checkBox.setChecked(self._model.isDisplaySurfaces())
        self._ui.displaySurfacesExterior_checkBox.setChecked(self._model.isDisplaySurfacesExterior())
        self._ui.displaySurfacesTranslucent_checkBox.setChecked(self._model.isDisplaySurfacesTranslucent())
        self._ui.displaySurfacesWireframe_checkBox.setChecked(self._model.isDisplaySurfacesWireframe())
        self._ui.displayXiAxes_checkBox.setChecked(self._model.isDisplayXiAxes())

    def _mergeNodesEntryChanged(self):
        nodeIdsText = self._ui.mergeNodesEntry_lineEdit.text().split('=',maxsplit=1)
        try:
            masterNodeId = int(nodeIdsText[0])
        except:
            masterNodeId = -1
        if self._model.checkMasterNodeId(masterNodeId):
            slaveNodeId = -1
            if len(nodeIdsText) == 2:
                try:
                    slaveNodeId = int(nodeIdsText[1])
                except:
                    pass
            if slaveNodeId >= 0:
                if self._model.mergeNodes(masterNodeId, slaveNodeId):
                    self._ui.mergeNodes_plainTextEdit.setPlainText(self._model.getMergeNodesText())
            else:
                newText = str(masterNodeId) + '='
                slaveNodeId = self._model.findMergeSlaveNodeId(masterNodeId)
                if slaveNodeId >= 0:
                    newText += str(slaveNodeId)
                self._ui.mergeNodesEntry_lineEdit.setText(newText)
                return
        self._ui.mergeNodesEntry_lineEdit.setText('')

    def _meshNodesDeleteClicked(self):
        try:
            text = self._ui.mergeNodesEntry_lineEdit.text()
            nodeIds = text.split('=')
            masterNodeId = int(nodeIds[0])
            if self._model.deleteMergeNode(masterNodeId):
                self._ui.mergeNodes_plainTextEdit.setPlainText(self._model.getMergeNodesText())
        except:
            pass
        self._ui.mergeNodesEntry_lineEdit.setText('')

    def _previewAlignClicked(self):
        self._model.setPreviewAlign(self._ui.previewAlign_checkBox.isChecked())

    def _previewFitClicked(self):
        self._model.setPreviewFit(self._ui.previewFit_checkBox.isChecked())

    def _displayAxesClicked(self):
        self._model.setDisplayAxes(self._ui.displayAxes_checkBox.isChecked())

    def _displayAxesClicked(self):
        self._model.setDisplayAxes(self._ui.displayAxes_checkBox.isChecked())

    def _displayElementNumbersClicked(self):
        self._model.setDisplayElementNumbers(self._ui.displayElementNumbers_checkBox.isChecked())

    def _displayLinesClicked(self):
        self._model.setDisplayLines(self._ui.displayLines_checkBox.isChecked())

    def _displayNodeDerivativesClicked(self):
        self._model.setDisplayNodeDerivatives(self._ui.displayNodeDerivatives_checkBox.isChecked())

    def _displayNodeNumbersClicked(self):
        self._model.setDisplayNodeNumbers(self._ui.displayNodeNumbers_checkBox.isChecked())

    def _displaySurfacesClicked(self):
        self._model.setDisplaySurfaces(self._ui.displaySurfaces_checkBox.isChecked())

    def _displaySurfacesExteriorClicked(self):
        self._model.setDisplaySurfacesExterior(self._ui.displaySurfacesExterior_checkBox.isChecked())

    def _displaySurfacesTranslucentClicked(self):
        self._model.setDisplaySurfacesTranslucent(self._ui.displaySurfacesTranslucent_checkBox.isChecked())

    def _displaySurfacesWireframeClicked(self):
        self._model.setDisplaySurfacesWireframe(self._ui.displaySurfacesWireframe_checkBox.isChecked())

    def _displayXiAxesClicked(self):
        self._model.setDisplayXiAxes(self._ui.displayXiAxes_checkBox.isChecked())

    def _viewAll(self):
        '''
        Ask sceneviewer to show all of scene.
        '''
        if self._ui.master_sceneviewerWidget.getSceneviewer() is not None:
            self._ui.master_sceneviewerWidget.viewAll()
        if self._ui.slave_sceneviewerWidget.getSceneviewer() is not None:
            self._ui.slave_sceneviewerWidget.viewAll()

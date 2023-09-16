<template>
  <q-page class="">
    <q-toolbar class="bg-transparent text-primary">
      <q-toolbar-title>
        VM List
      </q-toolbar-title>
      <q-btn @click="onRefresh" flat icon="refresh" label="Refresh" />
    </q-toolbar>

    <div v-for="HostInfo in hosts" class="q-pt-md q-px-md">
      <q-table :title="'HOST: ' + HostInfo.host" :rows="HostInfo.vms" :columns="columns" :pagination.sync="pagination" 
        :rows-per-page-options="RowsPerPageOptions" 
        style="height: 400px" virtual-scroll 
        row-key="NAME">
        <template v-slot:body="props">
          <!-- <q-tr :props="props" @click="onRowClick(props.row)"> -->
          <q-tr :props="props">
            <q-td key="name" :props="props">
              {{ props.row.NAME }}
            </q-td>
            <q-td key="datastore" :props="props">
              {{ props.row.DATASTORE }}
            </q-td>
            <q-td key="loader" :props="props">
              {{ props.row.LOADER }}
            </q-td>
            <q-td key="cpu" :props="props">
              {{ props.row.CPU }}
            </q-td>
            <q-td key="memory" :props="props">
              {{ props.row.MEMORY }}
            </q-td>
            <q-td key="vnc" :props="props">
              {{ props.row.VNC }}
            </q-td>
            <q-td key="auto" :props="props">
              <q-btn flat :label="props.row.AUTO" :class="getAutoColor(props.row.AUTO)"/>
            </q-td>
            <q-td key="state" :props="props">
              <q-btn @click="showStateDialog(HostInfo.host, props.row)" flat>
                <span :class="getStateColor(props.row.STATE)">{{ props.row.STATE }}</span>
              </q-btn>
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </div>
    <pre>
      {{debug}}
    </pre>
    <q-dialog v-model="isShowStateDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">Change VM State</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-banner rounded class="bg-blue text-white q-mb-md">
            State change may take a few seconds to reflect. Refresh the page to see the change reflected.
          </q-banner>
          <div class="row">
            <div class="col-4">Host</div>
            <div class="col-8">{{ SelectedHost }}</div>
            <div class="col-4">VM Name</div>
            <div class="col-8">{{ SelectedVmName.toUpperCase() }}</div>
            <div class="col-4">Current State</div>
            <div class="col-8">{{ SelectedVmState }}</div>
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-btn @click="sendVmCmd('start')" :disable="isDisableStart()" label="Start" v-close-popup class="full-width" color="green" flat/>
          <q-btn @click="sendVmCmd('stop', 5)" :disable="isDisableStop()" label="Stop" v-close-popup class="full-width" color="orange" flat/>
          <q-btn @click="sendVmCmd('unlock')" label="Unlock" v-close-popup class="full-width" color="blue" flat/>
          <q-btn @click="sendVmCmd('destroy')" label="Destroy" v-close-popup class="full-width" color="red" flat/>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="black" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import axios from 'axios'
import { ref } from 'vue'

const API_BASE_URL = 'http://192.168.88.7:8000'
// const debug = 'resp.data'
const isShowStateDialog = ref(null)
isShowStateDialog.value = false
const SelectedVmState = ref(null)
const SelectedVmName = ref(null)
const SelectedHost = ref(null)
let debug = ''

const hosts = ref([])
hosts.value = await getVmInfo()

const columns = ref([])
columns.value = [
  { name: 'name', field: 'NAME', label: 'Name', sortable: true, },
  { name: 'datastore', field: 'DATASTORE', label: 'Data Store', align: 'center' },
  { name: 'loader', field: 'LOADER', label: 'Loader', align: 'center', sortable: true, },
  { name: 'cpu', field: 'CPU', label: 'CPU', align: 'center', sortable: true, },
  { name: 'memory', field: 'MEMORY', label: 'Memory', align: 'center', sortable: true, },
  { name: 'vnc', field: 'VNC', label: 'VNC', sortable: true, },
  { name: 'auto', field: 'AUTO', label: 'Auto', align: 'center' },
  { name: 'state', field: 'STATE', label: 'State', align: 'center', sortable: true, },
]
const pagination = {
  rowsPerPage: 50,
}
const RowsPerPageOptions = [
  10,
  20,
  50,
  0,
]

function isDisableStop() {
  const isAllow = SelectedVmState.value.toLowerCase().startsWith('stop')
  return isAllow
}

function isDisableStart() {
  const isAllow = SelectedVmState.value.toLowerCase().startsWith('running')
  return isAllow
}

async function sendVmCmd(cmd, RefreshDelaySec = 3) {
  try {
    const resp = await axios.get(API_BASE_URL + `/api/bhyve/vm/${cmd}?host=${SelectedHost.value}&vm=${SelectedVmName.value}`)
    console.log(`response: ${resp.data}`)
    if (resp.data.code === 0) {
      console.log(`Delayed refresh: ${RefreshDelaySec}`)
      setTimeout(() => {
        onRefresh()
      }, RefreshDelaySec * 1000)
    }
  } catch (err) {
    console.error(err)
  }
}


function showStateDialog(host, VmInfo) {
  isShowStateDialog.value = true
  SelectedHost.value = host
  SelectedVmState.value = VmInfo.STATE.toUpperCase()
  SelectedVmName.value = VmInfo.NAME
}

function getAutoColor(AutoText) {
  if (AutoText.startsWith('Yes')) {
    return 'text-green'
  }
  return 'text-black'
}

function getStateColor(StateText) {
  if (StateText.startsWith('Running')) {
    return 'text-green'
  }
  if (StateText.startsWith('Locked')) {
    return 'text-red'
  }

  return 'text-black'
}

async function onRefresh() {
  hosts.value = []
  hosts.value = await getVmInfo()
}

async function getVmInfo() {
  try {
    const resp = await axios.get(API_BASE_URL + '/api/bhyve/vm/list', {
      timeout: 3000,
    })
    return resp.data
  } catch (err) {
    console.error(err)
  }
}
</script>
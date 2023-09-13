<template>
  <q-page class="">
    <q-toolbar class="bg-transparent text-primary">
      <q-toolbar-title>
        VM List
      </q-toolbar-title>
      <q-btn @click="onRefresh" flat icon="refresh" label="Refresh" />
    </q-toolbar>

    <div v-for="HostInfo in hosts" class="q-pt-md q-px-md">
      <q-table :title="'HOST: ' + HostInfo.host" :rows="HostInfo.vms" :columns="columns" :pagination.sync="pagination" :rows-per-page-options="RowsPerPageOptions" row-key="NAME">
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
              <q-btn @click="showStateDialog(props.row)" flat>
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
          <div>VM name: {{ SelectedVmName }}</div>
          <div>Current state: {{ SelectedVmState }}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-btn label="Start" v-close-popup class="full-width" color="green" flat/>
          <q-btn label="Stop" v-close-popup class="full-width" color="orange" flat/>
          <q-btn label="Destroy" v-close-popup class="full-width" color="red" flat/>
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

// const debug = 'resp.data'
const isShowStateDialog = ref(null)
isShowStateDialog.value = false
const SelectedVmState = ref(null)
const SelectedVmName = ref(null)

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

function showStateDialog(VmInfo) {
  isShowStateDialog.value = true
  SelectedVmState.value = VmInfo.STATE.toUpperCase()
  SelectedVmName.value = VmInfo.NAME.toUpperCase()
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
  const resp = await axios.get('http://192.168.88.7:8000/api/bhyve/vm/list')
  return resp.data
}
</script>
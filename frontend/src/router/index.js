import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import EvidenceList from '@/views/EvidenceList.vue'
import Analysis from '@/views/Analysis.vue'
import Findings from '@/views/Findings.vue'
import Report from '@/views/Report.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/evidence', name: 'EvidenceList', component: EvidenceList },
  { path: '/evidence/:id', name: 'EvidenceDetail', component: EvidenceList },
  { path: '/analysis', name: 'Analysis', component: Analysis },
  { path: '/findings', name: 'Findings', component: Findings },
  { path: '/report', name: 'Report', component: Report }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

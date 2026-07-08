<template>
  <div class="evidence-detail" v-if="evidence">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
      <h1>📄 {{ evidence.original_name }}</h1>
      <router-link to="/evidence" class="btn">返回列表</router-link>
    </div>

    <!-- 基本信息 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">文件类型</div>
        <div class="stat-value" style="font-size: 1.2rem;">{{ evidence.evidence_type }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">文件大小</div>
        <div class="stat-value" style="font-size: 1.2rem;">{{ formatSize(evidence.file_size) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">状态</div>
        <div class="stat-value">
          <span class="badge" :class="'badge-' + evidence.status">{{ statusMap[evidence.status] }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">发现数量</div>
        <div class="stat-value">{{ findings.length }}</div>
      </div>
    </div>

    <!-- 哈希值 -->
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">🔒 哈希值</h2>
      </div>
      <div style="font-family: monospace; font-size: 0.875rem;">
        <div style="margin-bottom: 0.5rem;"><strong>MD5:</strong> {{ evidence.md5 }}</div>
        <div><strong>SHA256:</strong> {{ evidence.sha256 }}</div>
      </div>
    </div>

    <!-- 实时分析状态 -->
    <div class="card" v-if="runningTasks.length > 0">
      <div class="card-header">
        <h2 class="card-title">🔄 实时分析进度</h2>
        <span class="badge badge-analyzing">WebSocket 已连接</span>
      </div>
      <div v-for="task in runningTasks" :key="task.id" style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
          <span>{{ task.tool }}</span>
          <span>{{ task.progress }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: task.progress + '%' }"></div>
        </div>
        <div style="font-size: 0.75rem; color: var(--gray-500); margin-top: 0.25rem;">
          {{ wsMessages[task.id] || '' }}
        </div>
      </div>
    </div>

    <!-- 分析任务列表 -->
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">🔬 分析任务</h2>
        <button class="btn btn-primary" @click="showRunModal = true">启动分析</button>
      </div>
      
      <!-- 运行分析 Modal -->
      <div v-if="showRunModal" class="modal-overlay" @click.self="showRunModal = false">
        <div class="modal">
          <h2>启动分析</h2>
          <div class="form-group">
            <label>选择工具</label>
            <select v-model="selectedTool" class="form-control">
              <option value="">-- 请选择 --</option>
              <option v-for="tool in availableTools" :key="tool.name" :value="tool.name">
                {{ tool.description }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>参数 (JSON, 可选)</label>
            <textarea v-model="paramsStr" class="form-control" rows="3" placeholder='{"key": "value"}'></textarea>
          </div>
          <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
            <button class="btn" @click="showRunModal = false">取消</button>
            <button class="btn btn-primary" @click="runAnalysis" :disabled="!selectedTool">开始</button>
          </div>
        </div>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>工具</th>
              <th>状态</th>
              <th>进度</th>
              <th>创建时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in tasks" :key="task.id">
              <td>{{ task.tool }}</td>
              <td><span class="badge" :class="'badge-' + task.status">{{ task.status }}</span></td>
              <td>
                <div class="progress-bar" style="width: 100px;">
                  <div class="progress-fill" :style="{ width: task.progress + '%' }"></div>
                </div>
                <span style="font-size: 0.75rem;">{{ task.progress }}%</span>
              </td>
              <td>{{ formatDate(task.created_at) }}</td>
            </tr>
            <tr v-if="tasks.length === 0">
              <td colspan="4" style="text-align: center; color: var(--gray-400);">暂无任务</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 发现列表 -->
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">🔎 发现列表</h2>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>类型</th>
              <th>等级</th>
              <th>标题</th>
              <th>内容</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in findings" :key="item.id">
              <td>{{ item.finding_type }}</td>
              <td><span class="badge" :class="'badge-' + item.severity">{{ item.severity }}</span></td>
              <td>{{ item.title }}</td>
              <td style="max-width: 400px; overflow: hidden; text-overflow: ellipsis;">{{ item.content }}</td>
            </tr>
            <tr v-if="findings.length === 0">
              <td colspan="4" style="text-align: center; color: var(--gray-400);">暂无发现</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 证据链 -->
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">🔗 证据链</h2>
      </div>
      <div class="timeline">
        <div v-for="item in chain" :key="item.id" class="timeline-item">
          <div class="timeline-dot"></div>
          <div class="timeline-content">
            <div style="font-weight: 500;">{{ item.description }}</div>
            <div style="font-size: 0.75rem; color: var(--gray-500);">{{ formatDate(item.timestamp) }}</div>
            <div v-if="item.details" style="font-size: 0.75rem; margin-top: 0.25rem;">
              <pre style="background: var(--gray-50); padding: 0.5rem; border-radius: 0.25rem; overflow-x: auto;">{{ item.details }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else style="text-align: center; padding: 3rem; color: var(--gray-400);">
    加载中...
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useEvidenceStore } from '@/stores/evidence'
import { evidenceAPI, analysisAPI, EvidenceWebSocket } from '@/services/api'

const route = useRoute()
const store = useEvidenceStore()

const evidence = ref(null)
const findings = ref([])
const chain = ref([])
const tasks = ref([])
const availableTools = ref([])
const showRunModal = ref(false)
const selectedTool = ref('')
const paramsStr = ref('')
const wsMessages = ref({})
const ws = ref(null)

const statusMap = {
  pending: '等待分析',
  analyzing: '分析中',
  completed: '已完成',
  error: '错误'
}

const runningTasks = computed(() => tasks.value.filter(t => t.status === 'running' || t.status === 'pending'))

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0, size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
}

const formatDate = (date) => date ? new Date(date).toLocaleString('zh-CN') : '-'

const loadData = async () => {
  const id = route.params.id
  try {
    const [ev, findingsRes, chainRes, tasksRes] = await Promise.all([
      evidenceAPI.get(id),
      evidenceAPI.getFindings(id),
      evidenceAPI.getChain(id),
      analysisAPI.getTasks(id)
    ])
    evidence.value = ev.data
    findings.value = findingsRes.data
    chain.value = chainRes.data
    tasks.value = tasksRes.data
  } catch (e) {
    console.error('Failed to load:', e)
  }
}

const runAnalysis = async () => {
  let params = {}
  if (paramsStr.value.trim()) {
    try { params = JSON.parse(paramsStr.value) } catch (e) { alert('JSON 格式错误'); return }
  }
  await analysisAPI.run(evidence.value.id, selectedTool.value, JSON.stringify(params))
  showRunModal.value = false
  selectedTool.value = ''
  paramsStr.value = ''
  await loadData()
}

// WebSocket 连接
const connectWS = () => {
  const id = route.params.id
  ws.value = new EvidenceWebSocket(id)
  ws.value.connect((msg) => {
    if (msg.type === 'progress') {
      wsMessages.value[msg.task_id] = msg.message
      // 更新任务进度
      const task = tasks.value.find(t => t.id === msg.task_id)
      if (task) task.progress = msg.progress
    } else if (msg.type === 'finding') {
      // 添加新发现
      findings.value.unshift({
        id: Date.now(),
        ...msg.finding
      })
    } else if (msg.type === 'task_complete') {
      loadData()
    }
  })
}

onMounted(async () => {
  await loadData()
  connectWS()
  // 加载工具列表
  const toolsRes = await analysisAPI.listTools()
  availableTools.value = toolsRes.data
})

onUnmounted(() => {
  if (ws.value) ws.value.disconnect()
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
.modal {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  width: 90%;
  max-width: 500px;
}
.modal h2 { margin-bottom: 1rem; }

.timeline {
  position: relative;
  padding-left: 2rem;
}
.timeline::before {
  content: '';
  position: absolute;
  left: 0.5rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--gray-200);
}
.timeline-item {
  position: relative;
  margin-bottom: 1.5rem;
}
.timeline-dot {
  position: absolute;
  left: -1.5rem;
  top: 0.25rem;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--primary);
  border: 2px solid white;
  box-shadow: 0 0 0 2px var(--primary);
}
.timeline-content {
  background: var(--gray-50);
  padding: 1rem;
  border-radius: 0.5rem;
}
</style>

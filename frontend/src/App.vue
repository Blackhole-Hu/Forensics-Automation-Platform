<template>
  <div id="app">
    <nav class="sidebar">
      <div class="logo">
        <h1>🔍 CTF 取证平台</h1>
      </div>
      <ul class="nav-links">
        <li><router-link to="/">📊 仪表盘</router-link></li>
        <li><router-link to="/evidence">📁 证据管理</router-link></li>
        <li><router-link to="/analysis">🔬 分析任务</router-link></li>
        <li><router-link to="/findings">🔎 发现列表</router-link></li>
        <li><router-link to="/report">📝 报告生成</router-link></li>
      </ul>
    </nav>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

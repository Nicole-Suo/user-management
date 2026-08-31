<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-name">UserMgmt</div>
      <div class="username">{{ username }}</div>
    </div>

    <nav class="nav">
      <button
        v-for="item in menuItems"
        :key="item.label"
        type="button"
        class="nav-item"
        @click="nav(item.url)"
      >
        {{ item.label }}
      </button>
    </nav>

    <button type="button" class="logout" @click="logout">退出登录</button>
  </aside>
</template>

<script>
export default {
  props: {
    menuItems: {
      type: Array,
      default: () => []
    },
    username: {
      type: String,
      default: ''
    }
  },
  methods: {
    nav(path) {
      this.$emit('navigate', path)
    },
    logout() {
      this.$emit('logout')
    }
  }
}
</script>

<style scoped>
.sidebar {
  width: 230px;
  background: #102a43;
  color: #f8fafc;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.brand {
  padding: 10px 8px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.brand-name {
  font-size: 24px;
  font-weight: 700;
}

.username {
  font-size: 13px;
  margin-top: 8px;
  color: #cbd5e1;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-item,
.logout {
  border: none;
  background: rgba(148, 163, 184, 0.1);
  color: #f8fafc;
  border-radius: 10px;
  padding: 12px 14px;
  text-align: left;
  font-size: 15px;
  cursor: pointer;
}

.nav-item:hover,
.logout:hover {
  background: rgba(96, 165, 250, 0.3);
}

.logout {
  margin-top: auto;
  background: rgba(239, 68, 68, 0.18);
}
</style>

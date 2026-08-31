<template>
  <div v-if="!loggedIn" class="login-page">
    <div class="login-card">
      <h2>用户管理系统</h2>
      <p class="sub-title">登录查看权限菜单与管理数据</p>
      <form @submit.prevent="login">
        <label>
          用户名
          <input v-model="loginForm.username" type="text" placeholder="admin" />
        </label>
        <label>
          密码
          <input v-model="loginForm.password" type="password" placeholder="admin123" />
        </label>
        <button type="submit">登录</button>
      </form>
      <p class="hint">默认账号：admin / admin123</p>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>

  <div v-else class="layout">
    <Sidebar
      :menu-items="menuItems"
      :username="username"
      @navigate="setSrc"
      @logout="logout"
    />
    <main class="main-panel">
      <iframe :src="currentSrc" title="User management content" />
    </main>
  </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue'

export default {
  components: { Sidebar },
  data() {
    return {
      loggedIn: false,
      username: '',
      permissions: [],
      menuItems: [],
      currentSrc: '/dashboard',
      error: '',
      loginForm: {
        username: 'admin',
        password: 'admin123'
      }
    }
  },
  mounted() {
    this.refreshUser()
  },
  methods: {
    hasPermission(name) {
      return !name || this.permissions.includes(name)
    },
    buildMenu() {
      const allItems = [
        { label: '首页', url: '/dashboard', permission: 'dashboard.view' },
        { label: '用户管理', url: '/users', permission: 'user.read' },
        { label: '角色权限', url: '/roles', permission: 'role.read' },
        { label: '个人资料', url: '/profile' }
      ]

      this.menuItems = allItems.filter((item) => this.hasPermission(item.permission))
      if (!this.menuItems.length) {
        this.currentSrc = '/profile'
      }
    },
    setSrc(path) {
      this.currentSrc = path
    },
    async refreshUser() {
      try {
        const response = await fetch('/api/me', { credentials: 'include' })
        if (!response.ok) {
          this.loggedIn = false
          return
        }

        const user = await response.json()
        this.username = user.username
        this.permissions = user.permissions || []
        this.loggedIn = true
        this.buildMenu()
      } catch (error) {
        this.loggedIn = false
      }
    },
    async login() {
      this.error = ''
      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.loginForm)
        })

        if (!response.ok) {
          const data = await response.json()
          this.error = data.error || '登录失败'
          return
        }

        await this.refreshUser()
      } catch (error) {
        this.error = '无法连接到后端服务，请先启动 Flask。'
      }
    },
    async logout() {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      })
      this.loggedIn = false
      this.username = ''
      this.permissions = []
      this.currentSrc = '/dashboard'
      this.error = ''
    }
  }
}
</script>

<style scoped>
.login-page {
  display: grid;
  place-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #eef4ff, #dfefff);
}

.login-card {
  width: min(420px, 90vw);
  padding: 28px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 20px 40px rgba(47, 81, 126, 0.12);
}

h2 {
  margin: 0 0 8px;
  font-size: 28px;
}

.sub-title {
  color: #567;
  margin-bottom: 24px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-weight: 600;
  color: #234;
}

input {
  padding: 12px 14px;
  border: 1px solid #cad9ef;
  border-radius: 10px;
  font-size: 16px;
}

button {
  border: none;
  border-radius: 10px;
  background: #2d6cdf;
  color: #fff;
  padding: 12px 16px;
  cursor: pointer;
  font-size: 16px;
}

.hint {
  color: #64748b;
  margin-top: 16px;
}

.error {
  margin-top: 12px;
  color: #d13a3a;
}

.layout {
  display: flex;
  height: 100vh;
  background: #f6f8fb;
}

.main-panel {
  flex: 1;
  background: #fff;
}

iframe {
  width: 100%;
  height: 100%;
  border: 0;
  background: #fff;
}
</style>

<template>
  <div class="panel">
    <div class="header">
      <h2>用户管理（SPA）</h2>
      <button @click="loadUsers">刷新</button>
      <button @click="showCreate = true">新建用户</button>
    </div>

    <div v-if="showCreate" class="panel form">
      <h3>创建用户</h3>
      <label>用户名<input v-model="form.username" /></label>
      <label>邮箱<input v-model="form.email" /></label>
      <label>姓名<input v-model="form.full_name" /></label>
      <label>密码<input v-model="form.password" type="password" /></label>
      <label>角色 (id, 逗号分隔)<input v-model="form.role_ids" /></label>
      <button @click="createUser">提交</button>
      <button @click="showCreate = false">取消</button>
    </div>

    <table>
      <thead>
        <tr><th>ID</th><th>用户名</th><th>邮箱</th><th>姓名</th><th>操作</th></tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td>{{ u.id }}</td>
          <td>{{ u.username }}</td>
          <td>{{ u.email }}</td>
          <td>{{ u.full_name || '-' }}</td>
          <td>
            <button @click="editUser(u)">编辑</button>
            <button @click="deleteUser(u.id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="editing" class="panel form">
      <h3>编辑用户</h3>
      <label>用户名<input v-model="editForm.username" /></label>
      <label>邮箱<input v-model="editForm.email" /></label>
      <label>姓名<input v-model="editForm.full_name" /></label>
      <label>密码 (留空不变)<input v-model="editForm.password" type="password" /></label>
      <label>角色 ids (逗号分隔)<input v-model="editForm.role_ids" /></label>
      <button @click="updateUser">保存</button>
      <button @click="cancelEdit">取消</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      users: [],
      showCreate: false,
      editing: false,
      form: { username: '', email: '', full_name: '', password: '', role_ids: '' },
      editForm: { id: null, username: '', email: '', full_name: '', password: '', role_ids: '' }
    }
  },
  mounted() {
    this.loadUsers()
  },
  methods: {
    async loadUsers() {
      const res = await fetch('/api/users', { credentials: 'include' })
      if (!res.ok) return
      this.users = await res.json()
    },
    async createUser() {
      const payload = {
        username: this.form.username,
        email: this.form.email,
        full_name: this.form.full_name,
        password: this.form.password,
        role_ids: this.form.role_ids ? this.form.role_ids.split(',').map(Number) : []
      }
      const res = await fetch('/api/users', { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      if (res.status === 201) {
        this.showCreate = false
        this.form = { username: '', email: '', full_name: '', password: '', role_ids: '' }
        this.loadUsers()
      } else {
        const data = await res.json()
        alert(data.error || '创建失败')
      }
    },
    editUser(u) {
      this.editing = true
      this.editForm = { id: u.id, username: u.username, email: u.email, full_name: u.full_name || '', password: '', role_ids: (u.roles||[]).map(r=>r.id).join(',') }
    },
    async updateUser() {
      const id = this.editForm.id
      const payload = {
        username: this.editForm.username,
        email: this.editForm.email,
        full_name: this.editForm.full_name,
        password: this.editForm.password || undefined,
        role_ids: this.editForm.role_ids ? this.editForm.role_ids.split(',').map(Number) : []
      }
      const res = await fetch(`/api/users/${id}`, { method: 'PUT', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      if (res.ok) {
        this.editing = false
        this.loadUsers()
      } else {
        const data = await res.json()
        alert(data.error || '更新失败')
      }
    },
    cancelEdit() { this.editing = false },
    async deleteUser(id) {
      if (!confirm('确认删除用户？')) return
      const res = await fetch(`/api/users/${id}`, { method: 'DELETE', credentials: 'include' })
      if (res.status === 204) this.loadUsers(); else alert('删除失败')
    }
  }
}
</script>

<style scoped>
.panel { padding: 18px }
.header { display:flex; gap:12px; align-items:center }
.form { margin-top: 12px; }
label { display:block; margin:6px 0 }
input { padding:6px; }
</style>

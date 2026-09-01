<template>
  <div class="panel">
    <div class="header">
      <h2>角色管理（SPA）</h2>
      <button @click="loadRoles">刷新</button>
      <button @click="showCreate = true">新建角色</button>
    </div>

    <div v-if="showCreate" class="panel form">
      <h3>创建角色</h3>
      <label>名称<input v-model="form.name" /></label>
      <label>描述<input v-model="form.description" /></label>
      <label>权限 (逗号分隔的 permission 名称)<input v-model="form.permissions" /></label>
      <button @click="createRole">提交</button>
      <button @click="showCreate = false">取消</button>
    </div>

    <table>
      <thead>
        <tr><th>ID</th><th>名称</th><th>描述</th><th>权限</th><th>操作</th></tr>
      </thead>
      <tbody>
        <tr v-for="r in roles" :key="r.id">
          <td>{{ r.id }}</td>
          <td>{{ r.name }}</td>
          <td>{{ r.description || '-' }}</td>
          <td>{{ (r.permissions||[]).join(', ') }}</td>
          <td>
            <button @click="editRole(r)">编辑</button>
            <button @click="deleteRole(r.id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="editing" class="panel form">
      <h3>编辑角色</h3>
      <label>名称<input v-model="editForm.name" /></label>
      <label>描述<input v-model="editForm.description" /></label>
      <label>权限 (逗号分隔)<input v-model="editForm.permissions" /></label>
      <button @click="updateRole">保存</button>
      <button @click="cancelEdit">取消</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      roles: [],
      showCreate: false,
      editing: false,
      form: { name: '', description: '', permissions: '' },
      editForm: { id: null, name: '', description: '', permissions: '' }
    }
  },
  mounted() { this.loadRoles() },
  methods: {
    async loadRoles() {
      const res = await fetch('/api/roles', { credentials: 'include' })
      if (!res.ok) return
      this.roles = await res.json()
    },
    async createRole() {
      const payload = { name: this.form.name, description: this.form.description, permissions: this.form.permissions ? this.form.permissions.split(',').map(s=>s.trim()) : [] }
      const res = await fetch('/api/roles', { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      if (res.status === 201) { this.showCreate=false; this.form={name:'',description:'',permissions:''}; this.loadRoles() } else { const d=await res.json(); alert(d.error||'创建失败') }
    },
    editRole(r){ this.editing=true; this.editForm={ id:r.id, name:r.name, description:r.description||'', permissions:(r.permissions||[]).join(',') } },
    async updateRole(){ const id=this.editForm.id; const payload={ name:this.editForm.name, description:this.editForm.description, permissions:this.editForm.permissions?this.editForm.permissions.split(',').map(s=>s.trim()):[] }; const res=await fetch(`/api/roles/${id}`,{ method:'PUT', credentials:'include', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)}); if(res.ok){ this.editing=false; this.loadRoles() } else { const d=await res.json(); alert(d.error||'更新失败') } },
    cancelEdit(){ this.editing=false },
    async deleteRole(id){ if(!confirm('确认删除角色？')) return; const res=await fetch(`/api/roles/${id}`,{ method:'DELETE', credentials:'include' }); if(res.status===204) this.loadRoles(); else alert('删除失败') }
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

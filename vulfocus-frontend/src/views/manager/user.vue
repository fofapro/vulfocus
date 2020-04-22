<template>
  <div class="app-container">
  <el-table
    :data="tableData"
    border
    stripe
    style="width: 100%">
    <el-table-column
      type="index"
      width="50">
    </el-table-column>
    <el-table-column
      prop="name"
      label="用户名">
    </el-table-column>
    <el-table-column
      prop="email"
      label="邮箱">
    </el-table-column>
    <el-table-column
      prop="roles"
      label="权限">
    </el-table-column>
    <el-table-column
      prop="rank"
      label="Rank">
    </el-table-column>
    <el-table-column
      prop="combination_desc"
      label="操作"
      :show-overflow-tooltip=true
      width="200">
      <template slot-scope="{row}">
        <el-button
          size="mini"
          type="primary"
          icon="el-icon-edit"
          @click="changePwd(row)"
        >修改密码</el-button>
      </template>
    </el-table-column>
  </el-table>
  </div>

</template>

<script>

  import { userList,userChangePwd } from '@/api/user'
  export default {
    name: 'user',
    data(){
      return {
        tableData: []
      }
    },
    created(){
      this.initUserList()
    },
    methods:{
      initUserList(){
        userList().then(response => {
          let data = response.data
          this.tableData = data
        })
      },
      changePwd(row){
        this.$prompt("请输入新密码","提示",{
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputErrorMessage: "密码格式不正确",
          inputValidator: this.inputValidatorPwd,
          inputPlaceholder: "密码长度不得小于6位"
        }).then(({ value }) => {
          userChangePwd({pwd: value},row.id).then(response => {
            let rsData = response.data
            if(rsData.status === 200){
              this.$message({
                type: 'success',
                message: '密码修改成功'
              });
            }else{
              this.$message({
                type: 'error',
                message: rsData.msg
              });
            }
          })
        })
      },
      inputValidatorPwd(nwePwd){
        if(nwePwd == null || nwePwd.length < 6){
          nwePwd = nwePwd.trim()
          if(nwePwd.length){
            return false
          }
          return false
        }
        return true
      }
    }
  }
</script>

<style scoped>

</style>

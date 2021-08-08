<template>
  <div class="app-container">
    <el-input v-model="search" style="width: 230px;" size="medium"></el-input>
    <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-search" @click="userHandleQuery">
      查询
    </el-button>
    <el-table :data="tableData" border stripe style="width: 100%" v-loading="loading">
      <el-table-column type="index" width="50"></el-table-column>
      <el-table-column prop="name" label="用户名"></el-table-column>
      <el-table-column prop="email" label="邮箱"></el-table-column>
      <el-table-column prop="roles" label="权限"></el-table-column>
      <el-table-column prop="rank" label="Rank"></el-table-column>
      <el-table-column prop="rank_count" label="通过数量"></el-table-column>
      <el-table-column prop="date_joined" label="注册时间"></el-table-column>
      <el-table-column prop="combination_desc" label="操作" :show-overflow-tooltip=true width="200">
        <template slot-scope="{row}">
          <el-button size="mini" type="primary" icon="el-icon-edit" @click="changePwd(row)" >修改密码</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="margin-top: 20px">
      <el-pagination
        :page-size="page.size"
        @current-change="initUserList"
        layout="total, prev, pager, next, jumper"
        :total="page.total">
      </el-pagination>
    </div>
  </div>

</template>

<script>

  import { userList,userChangePwd } from '@/api/user'
  export default {
    name: 'user',
    data(){
      return {
        page:{
          total: 0,
          size: 20,
        },
        search: "",
        tableData: [],
        loading:true
      }
    },
    created(){
      this.initUserList(1)
    },
    methods:{
      initUserList(page){
        userList(page,this.search).then(response => {
          let data = response.data.results
          this.tableData = data
          this.page.total = response.data.count
          this.loading=false
        })

      },
      userHandleQuery(){
        this.initUserList(1)
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

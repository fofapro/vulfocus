<template>
  <div class="app-container">
    <el-table
      :data="tableData" border stripe style="width: 100%">
      <el-table-column type="index" width="50"></el-table-column>
      <el-table-column prop="vul_name" width="150" :show-overflow-tooltip=true label="漏洞名称"></el-table-column>
      <el-table-column :show-overflow-tooltip=true prop="user_name" width="100" label="用户名"></el-table-column>
      <el-table-column prop="vul_host" width="200" :show-overflow-tooltip=true label="访问地址"></el-table-column>
      <el-table-column label="状态" width="85">
        <template slot-scope="{row}">
          <el-tag>{{row.container_status}}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="vul_desc" :show-overflow-tooltip=true width="300" label="漏洞描述"></el-table-column>
      <el-table-column prop="combination_desc" label="操作" :show-overflow-tooltip=true>
        <template slot-scope="{row}">
          <el-button size="mini" type="primary" icon="el-icon-caret-left" v-if="row.container_status === 'stop'"
                     @click="startContainer(row)" >启动</el-button>
          <el-button size="mini" type="primary" icon="el-icon-loading" v-if="row.container_status === 'running'"
                     @click="stopContainer(row)" >停止</el-button>
          <el-button size="mini" type="danger" icon="el-icon-delete" v-if="row.container_status === 'running' || row.container_status === 'stop'"
                     @click="delContainer(row)" >删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="margin-top: 20px">
      <el-pagination
        :page-size="page.size"
        @current-change="initTable"
        layout="total, prev, pager, next, jumper"
        :total="page.total">
      </el-pagination>
    </div>
  </div>
</template>

<script>
  import { containerList,containerStop,containerStart,containerDel } from '@/api/container'
  import { getTask } from '@/api/tasks'
  import CountDown from 'vue2-countdown'
  export default {
    name: 'image',
    data(){
      return {
        page:{
          total: 0,
          size: 20,
        },
        tableData: []
      }
    },
    components: {
      CountDown
    },
    created(){
      this.initTable(1)
    },
    methods:{
      initTable(page){
        containerList('list', page).then(response => {
          this.tableData = response.data.results
          this.page.total = response.data.count
        })
      },
      stopContainer(row){
        containerStop(row.container_id).then(response => {
          let taskId = response.data["data"]
          let tmpStopContainerInterval = window.setInterval(() => {
            setTimeout(()=>{
              getTask(taskId).then(response=>{
                let responseStatus = response.data["status"]
                let responseData = response.data
                if (responseStatus === 1001){
                  // 一直轮训
                }else{
                  clearInterval(tmpStopContainerInterval)
                  if(responseStatus === 200){
                    this.$message({
                      type: "success",
                      message: "删除成功"
                    });
                    this.initTable()
                  }else{
                    this.$message({
                      type: "error",
                      message: responseData["msg"]
                    })
                  }
                }
              })
            },1)
          },1000)
        })
      },
      startContainer(row){
        containerStart(row.container_id).then(response => {
          let taskId = response.data["data"]
          let tmpRunContainerInterval = window.setInterval(() => {
            setTimeout(()=>{
              getTask(taskId).then(response=>{
                let responseStatus = response.data["status"]
                let responseData = response.data
                if (responseStatus === 1001){
                  // 一直轮训
                }else{
                  clearInterval(tmpRunContainerInterval)
                  if(responseStatus === 200){
                    this.$message({
                      type: "success",
                      message: "启动成功"
                    });
                    this.initTable()
                  }else{
                    this.$message({
                      type: "error",
                      message: responseData["msg"]
                    })
                  }
                }
              })
            },1)
          },1000)
        })
      },
      delContainer(row){
        containerDel(row.container_id).then(response => {
          let taskId = response.data["data"]
          let tmpDeleteContainerInterval = window.setInterval(() => {
            setTimeout(()=>{
              getTask(taskId).then(response=>{
                let responseStatus = response.data["status"]
                let responseData = response.data
                if (responseStatus === 1001){
                  // 一直轮训
                }else{
                  clearInterval(tmpDeleteContainerInterval)
                  if (responseStatus === 200) {
                    this.$message({
                      type: 'success',
                      message: '删除成功'
                    });
                    this.initTable()
                  }else{
                    this.$message({
                      message: responseData["msg"],
                      type: "error",
                    })
                  }
                }
              })
            },1)
          },1000)
        })
      }
    }
  }
</script>

<style scoped>
</style>
